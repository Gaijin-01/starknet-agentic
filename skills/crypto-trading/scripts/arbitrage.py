"""
Arbitrage Detection Module.

Detects price discrepancies across DEXs
for potential arbitrage opportunities.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PriceQuote:
    """Price quote from a DEX."""
    exchange: str
    pair: str
    token0_symbol: str
    token1_symbol: str
    price: float  # token1 per token0
    liquidity: float
    volume_24h: float
    timestamp: datetime


@dataclass
class ArbitrageOpportunity:
    """Detected arbitrage opportunity."""
    token_pair: str
    buy_exchange: str
    sell_exchange: str
    buy_price: float
    sell_price: float
    spread_percent: float
    profit_percent: float  # After fees
    estimated_profit_usd: float
    liquidity: float
    timestamp: datetime
    execution_risk: str  # low, medium, high
    notes: List[str] = None
    
    def __post_init__(self):
        if self.notes is None:
            self.notes = []


class ArbitrageDetector:
    """Detects cross-DEX arbitrage opportunities."""
    
    # Supported DEXes
    UNISWAP_V3 = "uniswap-v3"
    UNISWAP_V2 = "uniswap-v2"
    SUSHISWAP = "sushiswap"
    PANCAKESWAP = "pancakeswap"
    CURVE = "curve"
    BALANCER = "balancer"
    
    def __init__(
        self,
        gas_price_gwei: float = 20.0,
        profit_threshold_percent: float = 1.0,
        min_liquidity_usd: float = 10000
    ):
        """
        Initialize arbitrage detector.
        
        Args:
            gas_price_gwei: Current gas price in Gwei
            profit_threshold_percent: Minimum spread to report
            min_liquidity_usd: Minimum liquidity for opportunity
        """
        self.gas_price_gwei = gas_price_gwei
        self.profit_threshold = profit_threshold_percent
        self.min_liquidity = min_liquidity_usd
        
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Price cache
        self._price_cache: Dict[str, List[PriceQuote]] = {}
        self._cache_timestamp = None
        self._cache_ttl_seconds = 60
    
    async def close(self):
        """Close async client."""
        await self.client.aclose()
    
    # ============ Price Fetching ============
    
    async def get_prices_for_pair(
        self,
        token0_address: str,
        token1_address: str = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  # WETH
        chains: Optional[List[str]] = None
    ) -> List[PriceQuote]:
        """
        Get prices for a token pair across exchanges.
        
        Args:
            token0_address: Base token address
            token1_address: Quote token address
            chains: Chains to check
            
        Returns:
            List of PriceQuote from different exchanges
        """
        chains = chains or ["ethereum", "bsc", "arbitrum"]
        all_quotes = []
        
        # Fetch from multiple sources
        tasks = [
            self._get_uniswap_prices(token0_address, token1_address, "ethereum"),
            self._get_sushiswap_prices(token0_address, token1_address, "ethereum"),
            self._get_pancakeswap_prices(token0_address, token1_address, "bsc"),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_quotes.extend(result)
        
        return all_quotes
    
    async def get_all_prices(
        self,
        chains: Optional[List[str]] = None
    ) -> Dict[str, List[PriceQuote]]:
        """
        Get all tracked prices across exchanges.
        
        Args:
            chains: Chains to check
            
        Returns:
            Dict of token pair -> List of PriceQuote
        """
        # Check cache
        if self._price_cache and self._cache_timestamp:
            age = (datetime.now() - self._cache_timestamp).total_seconds()
            if age < self._cache_ttl_seconds:
                return self._price_cache
        
        chains = chains or ["ethereum", "bsc", "arbitrum"]
        all_prices: Dict[str, List[PriceQuote]] = defaultdict(list)
        
        try:
            # Fetch top pairs
            url = "https://api.dexscreener.com/latest/dex/pairs"
            
            for chain in chains:
                params = {"chainId": chain, "limit": 50}
                response = await self.client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    for pair in data.get("pairs", []):
                        quote = self._parse_dexscreener_pair(pair)
                        pair_key = f"{quote.token0_symbol}/{quote.token1_symbol}"
                        all_prices[pair_key].append(quote)
            
            # Update cache
            self._price_cache = dict(all_prices)
            self._cache_timestamp = datetime.now()
            
            return all_prices
            
        except Exception as e:
            logger.error(f"Failed to get all prices: {e}")
            return all_prices
    
    # ============ Arbitrage Detection ============
    
    async def find_opportunities(
        self,
        min_spread_percent: float = None,
        max_results: int = 20
    ) -> List[ArbitrageOpportunity]:
        """
        Find arbitrage opportunities.
        
        Args:
            min_spread_percent: Minimum spread percentage
            max_results: Max opportunities to return
            
        Returns:
            List of ArbitrageOpportunity
        """
        min_spread = min_spread_percent or self.profit_threshold
        
        all_prices = await self.get_all_prices()
        opportunities = []
        
        for pair, quotes in all_prices.items():
            if len(quotes) < 2:
                continue
            
            # Find best buy and sell prices
            sorted_quotes = sorted(quotes, key=lambda q: q.price)
            
            for i, buy_quote in enumerate(sorted_quotes[:3]):  # Top 3 cheapest
                for sell_quote in sorted_quotes[-3:]:  # Top 3 expensive
                    if buy_quote.exchange == sell_quote.exchange:
                        continue
                    
                    # Calculate spread
                    spread = ((sell_quote.price - buy_quote.price) / buy_quote.price) * 100
                    
                    if spread < min_spread:
                        continue
                    
                    # Estimate profit after fees
                    profit = self._estimate_profit(buy_quote, sell_quote, spread)
                    
                    if profit.profit_percent < min_spread:
                        continue
                    
                    opportunities.append(profit)
        
        # Sort by profit percentage
        opportunities.sort(key=lambda x: x.profit_percent, reverse=True)
        
        return opportunities[:max_results]
    
    async def analyze_pair(
        self,
        token0_symbol: str,
        token1_symbol: str = "USDT"
    ) -> Dict[str, Any]:
        """
        Analyze a specific token pair for arbitrage.
        
        Args:
            token0_symbol: Base token symbol
            token1_symbol: Quote token symbol
            
        Returns:
            Analysis results
        """
        all_prices = await self.get_all_prices()
        pair_key = f"{token0_symbol}/{token1_symbol}"
        
        quotes = all_prices.get(pair_key, [])
        
        if len(quotes) < 2:
            return {
                "pair": pair_key,
                "status": "insufficient_data",
                "quote_count": len(quotes)
            }
        
        # Find best prices
        sorted_quotes = sorted(quotes, key=lambda q: q.price)
        
        best_buy = sorted_quotes[0]
        best_sell = sorted_quotes[-1]
        
        spread = ((best_sell.price - best_buy.price) / best_buy.price) * 100
        profit = self._estimate_profit(best_buy, best_sell, spread)
        
        return {
            "pair": pair_key,
            "status": "opportunity" if profit.profit_percent > self.profit_threshold else "no_opportunity",
            "best_buy": {
                "exchange": best_buy.exchange,
                "price": best_buy.price,
                "liquidity": best_buy.liquidity
            },
            "best_sell": {
                "exchange": best_sell.exchange,
                "price": best_sell.price,
                "liquidity": best_sell.liquidity
            },
            "raw_spread_percent": spread,
            "estimated_profit_percent": profit.profit_percent,
            "estimated_profit_usd": profit.estimated_profit_usd,
            "all_quotes": [q.__dict__ for q in quotes],
            "recommendation": self._generate_recommendation(profit)
        }
    
    def _estimate_profit(
        self,
        buy_quote: PriceQuote,
        sell_quote: PriceQuote,
        raw_spread_percent: float
    ) -> ArbitrageOpportunity:
        """
        Estimate actual profit after fees and slippage.
        
        Args:
            buy_quote: Where to buy
            sell_quote: Where to sell
            raw_spread_percent: Raw spread percentage
            
        Returns:
            ArbitrageOpportunity with profit estimates
        """
        # Typical fees (can be adjusted)
        UNISWAP_FEE = 0.003  # 0.3%
        SUSHISWAP_FEE = 0.003
        PANCAKESWAP_FEE = 0.0025
        CURVE_FEE = 0.0004  # 0.04%
        
        fee_map = {
            "uniswap-v3": UNISWAP_FEE,
            "uniswap-v2": UNISWAP_FEE,
            "sushiswap": SUSHISWAP_FEE,
            "pancakeswap": PANCAKESWAP_FEE,
            "curve": CURVE_FEE,
        }
        
        buy_fee = fee_map.get(buy_quote.exchange, 0.003)
        sell_fee = fee_map.get(sell_quote.exchange, 0.003)
        
        # Slippage estimate (1% for small trades)
        slippage = 0.01
        
        # Gas cost estimate (varies by chain)
        gas_cost_usd = self._estimate_gas_cost(buy_quote)
        
        # Calculate net profit
        total_fees = buy_fee + sell_fee + slippage
        net_spread = raw_spread_percent - (total_fees * 100)
        
        # Estimate profit for $1000 trade
        trade_size = 1000
        gross_profit = trade_size * (raw_spread_percent / 100)
        net_profit = gross_profit - gas_cost_usd
        
        profit_percent = (net_profit / trade_size) * 100
        
        # Risk assessment
        if buy_quote.liquidity < 10000 or sell_quote.liquidity < 10000:
            risk = "high"
            notes = ["Low liquidity - high slippage risk"]
        elif net_spread < 0.5:
            risk = "high"
            notes = ["Narrow spread - execution risk"]
        elif net_spread < 1.0:
            risk = "medium"
            notes = []
        else:
            risk = "low"
            notes = []
        
        return ArbitrageOpportunity(
            token_pair=f"{buy_quote.token0_symbol}/{buy_quote.token1_symbol}",
            buy_exchange=buy_quote.exchange,
            sell_exchange=sell_quote.exchange,
            buy_price=buy_quote.price,
            sell_price=sell_quote.price,
            spread_percent=raw_spread_percent,
            profit_percent=profit_percent,
            estimated_profit_usd=net_profit,
            liquidity=min(buy_quote.liquidity, sell_quote.liquidity),
            timestamp=datetime.now(),
            execution_risk=risk,
            notes=notes
        )
    
    def _estimate_gas_cost(self, quote: PriceQuote) -> float:
        """Estimate gas cost in USD."""
        # Rough estimates
        chain_gas = {
            "ethereum": 0.02,  # ~$50 at 20 gwei
            "bsc": 0.005,      # ~$0.50
            "arbitrum": 0.003, # ~$0.30
            "polygon": 0.001,  # ~$0.10
        }
        
        # Estimate based on exchange complexity
        exchange_gas = {
            "uniswap-v3": 1.0,
            "uniswap-v2": 1.2,
            "sushiswap": 1.2,
            "pancakeswap": 0.5,
            "curve": 2.0,
            "balancer": 1.5,
        }
        
        chain = quote.exchange.split("-")[0] if "-" in quote.exchange else "ethereum"
        base_gas = chain_gas.get(chain, 0.02)
        exchange_mult = exchange_gas.get(quote.exchange, 1.0)
        
        return base_gas * exchange_mult
    
    def _generate_recommendation(self, opp: ArbitrageOpportunity) -> str:
        """Generate recommendation string."""
        if opp.profit_percent < 0:
            return "❌ Negative spread - not profitable"
        elif opp.profit_percent < 0.5:
            return "⚠️ Low profitability - barely covers gas"
        elif opp.execution_risk == "high":
            return "⚠️ High risk - execute quickly or avoid"
        elif opp.execution_risk == "medium":
            return "✅ Moderate opportunity - proceed with caution"
        else:
            return "✅ Good opportunity - safe execution"
    
    # ============ Helper Methods ============
    
    async def _get_uniswap_prices(
        self,
        token0: str,
        token1: str,
        chain: str
    ) -> List[PriceQuote]:
        """Get prices from Uniswap."""
        return []
    
    async def _get_sushiswap_prices(
        self,
        token0: str,
        token1: str,
        chain: str
    ) -> List[PriceQuote]:
        """Get prices from SushiSwap."""
        return []
    
    async def _get_pancakeswap_prices(
        self,
        token0: str,
        token1: str,
        chain: str
    ) -> List[PriceQuote]:
        """Get prices from PancakeSwap."""
        return []
    
    def _parse_dexscreener_pair(self, pair: Dict) -> PriceQuote:
        """Parse DexScreener pair to PriceQuote."""
        base_token = pair.get("baseToken", {})
        liquidity = pair.get("liquidity", {})
        
        return PriceQuote(
            exchange=pair.get("dexId", "unknown"),
            pair=pair.get("pairAddress", ""),
            token0_symbol=base_token.get("symbol", "?"),
            token1_symbol=pair.get("quoteToken", {}).get("symbol", "?"),
            price=float(pair.get("priceUsd", 0)),
            liquidity=float(liquidity.get("usd", 0)),
            volume_24h=float(pair.get("volume", {}).get("h24", 0)),
            timestamp=datetime.now()
        )


# Triangular Arbitrage

class TriangularArbitrage:
    """Detects triangular arbitrage opportunities."""
    
    async def find_opportunities(
        self,
        exchanges: Optional[List[str]] = None,
        min_profit_percent: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Find triangular arbitrage opportunities.
        
        Example: ETH → USDC → DAI → ETH
        
        Args:
            exchanges: Exchanges to check
            min_profit_percent: Minimum profit threshold
            
        Returns:
            List of triangular arbitrage opportunities
        """
        # This requires full order book data
        # Simplified implementation returns empty list
        logger.info("Triangular arbitrage detection requires order book data")
        return []


# Synchronous wrapper
class SyncArbitrageDetector:
    """Synchronous wrapper for ArbitrageDetector."""
    
    def __init__(
        self,
        gas_price_gwei: float = 20.0,
        profit_threshold_percent: float = 1.0
    ):
        self._async = ArbitrageDetector(
            gas_price_gwei=gas_price_gwei,
            profit_threshold_percent=profit_threshold_percent
        )
    
    def find_opportunities(self, min_spread_percent: float = None, max_results: int = 20):
        """Find opportunities synchronously."""
        return asyncio.run(self._async.find_opportunities(min_spread_percent, max_results))
    
    def analyze_pair(self, token0_symbol: str, token1_symbol: str = "USDT"):
        """Analyze pair synchronously."""
        return asyncio.run(self._async.analyze_pair(token0_symbol, token1_symbol))
    
    def close(self):
        """Close async resources."""
        asyncio.run(self._async.close())
