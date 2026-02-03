"""
Ekubo DEX Client for Starknet Intelligence Colony
==================================================
Real-time data from Ekubo DEX on Starknet.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class EkuboPool:
    """Ekubo liquidity pool data"""
    token0: str
    token1: str
    fee: float
    tvl: float
    volume_24h: float
    apr: float
    token0_symbol: str
    token1_symbol: str
    
    def to_dict(self) -> dict:
        return {
            "token0": self.token0,
            "token1": self.token1,
            "fee": self.fee,
            "tvl": self.tvl,
            "volume_24h": self.volume_24h,
            "apr": self.apr,
            "token0_symbol": self.token0_symbol,
            "token1_symbol": self.token1_symbol
        }


@dataclass
class EkuboSwap:
    """Ekubo swap data"""
    token_in: str
    token_out: str
    amount_in: float
    amount_out: float
    price_impact: float
    pool: str
    timestamp: str
    
    def to_dict(self) -> dict:
        return {
            "token_in": self.token_in,
            "token_out": self.token_out,
            "amount_in": self.amount_in,
            "amount_out": self.amount_out,
            "price_impact": self.price_impact,
            "pool": self.pool,
            "timestamp": self.timestamp
        }


class EkuboClient:
    """
    Client for Ekubo DEX data on Starknet.
    
    Features:
    - Pool data retrieval
    - Liquidity information
    - Swap data
    - Arbitrage opportunity detection
    """
    
    def __init__(self, api_url: str = None, subgraph_url: str = None):
        from config import API
        self.api_url = api_url or API.EKUBO_API_URL
        self.subgraph_url = subgraph_url or API.EKUBO_SUBGRAPH_URL
        self._session = None
    
    async def _get_session(self):
        """Get HTTP session"""
        import aiohttp
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session
    
    async def close(self):
        """Close HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def _request(self, endpoint: str, method: str = "GET", 
                       data: Dict = None) -> Optional[Any]:
        """Make API request"""
        import aiohttp
        session = await self._get_session()
        url = f"{self.api_url}/{endpoint}"
        
        try:
            if method == "GET":
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
            elif method == "POST":
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        return await response.json()
        except Exception as e:
            logger.error(f"Ekubo request error: {e}")
        return None
    
    async def get_pools(self) -> List[EkuboPool]:
        """
        Get all Ekubo pools.
        
        Note: Ekubo API structure may vary. This uses a sample structure.
        Replace with actual API calls when available.
        """
        # Sample data for demonstration - replace with real API calls
        sample_pools = [
            {
                "token0": "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004d7",
                "token1": "0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a",
                "fee": 0.003,
                "tvl": 15_500_000,
                "volume_24h": 2_300_000,
                "apr": 12.5,
                "token0_symbol": "ETH",
                "token1_symbol": "USDC"
            },
            {
                "token0": "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004d7",
                "token1": "0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938",
                "fee": 0.003,
                "tvl": 8_200_000,
                "volume_24h": 1_100_000,
                "apr": 18.2,
                "token0_symbol": "ETH",
                "token1_symbol": "STRK"
            },
            {
                "token0": "0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a",
                "token1": "0x12d5398c66024acf409e8b5ad9e24c93d5386a4cf59fa2a9b00003bf9df6bf7",
                "fee": 0.003,
                "tvl": 5_800_000,
                "volume_24h": 890_000,
                "apr": 9.8,
                "token0_symbol": "USDC",
                "token1_symbol": "WBTC"
            },
            {
                "token0": "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004d7",
                "token1": "0x0000000000000000000000000000000000000000000000000000000000000000",
                "fee": 0.001,
                "tvl": 3_200_000,
                "volume_24h": 450_000,
                "apr": 8.5,
                "token0_symbol": "ETH",
                "token1_symbol": "ETH"
            }
        ]
        
        pools = []
        for p in sample_pools:
            pools.append(EkuboPool(
                token0=p["token0"],
                token1=p["token1"],
                fee=p["fee"],
                tvl=p["tvl"],
                volume_24h=p["volume_24h"],
                apr=p["apr"],
                token0_symbol=p["token0_symbol"],
                token1_symbol=p["token1_symbol"]
            ))
        
        return pools
    
    async def get_pool_by_pair(self, token0: str, token1: str) -> Optional[EkuboPool]:
        """Get specific pool by token pair"""
        pools = await self.get_pools()
        for pool in pools:
            if (pool.token0 == token0 and pool.token1 == token1) or \
               (pool.token0 == token1 and pool.token1 == token0):
                return pool
        return None
    
    async def get_tvl(self) -> float:
        """Get total value locked in Ekubo"""
        pools = await self.get_pools()
        return sum(pool.tvl for pool in pools)
    
    async def get_volume_24h(self) -> float:
        """Get 24h trading volume"""
        pools = await self.get_pools()
        return sum(pool.volume_24h for pool in pools)
    
    async def get_top_pools(self, limit: int = 5) -> List[EkuboPool]:
        """Get top pools by TVL"""
        pools = await self.get_pools()
        return sorted(pools, key=lambda p: p.tvl, reverse=True)[:limit]
    
    async def get_apr_leaders(self, limit: int = 5) -> List[EkuboPool]:
        """Get pools with highest APR"""
        pools = await self.get_pools()
        return sorted(pools, key=lambda p: p.apr, reverse=True)[:limit]
    
    # =========================================================================
    # Arbitrage Detection
    # =========================================================================
    
    async def detect_arbitrage_opportunities(self, 
                                              other_dex_prices: Dict[str, float],
                                              min_profit: float = 0.5) -> List[Dict]:
        """
        Detect arbitrage opportunities between Ekubo and other DEXs.
        
        Args:
            other_dex_prices: Dict of token -> price on other DEX
            min_profit: Minimum profit percentage to report
        
        Returns:
            List of arbitrage opportunities
        """
        opportunities = []
        pools = await self.get_pools()
        
        for pool in pools:
            # Calculate Ekubo's price for this pair
            if pool.token1_symbol in other_dex_prices:
                other_price = other_dex_prices[pool.token1_symbol]
                
                # Simplified price comparison
                # In reality, you'd need actual exchange rates
                if other_price > 0:
                    potential_profit = (other_price - pool.tvl) / pool.tvl * 100
                    
                    if potential_profit >= min_profit:
                        opportunities.append({
                            "token": pool.token1_symbol,
                            "buy_dex": "other",
                            "sell_dex": "ekubo",
                            "buy_price": other_price,
                            "sell_price": pool.tvl / 1000,  # Simplified
                            "profit_percent": potential_profit,
                            "pool": f"{pool.token0_symbol}/{pool.token1_symbol}",
                            "volume_usd": pool.volume_24h,
                            "timestamp": datetime.utcnow().isoformat()
                        })
        
        return opportunities
    
    async def get_arbitrage_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive arbitrage dashboard data"""
        pools = await self.get_pools()
        
        return {
            "pools": [p.to_dict() for p in pools],
            "total_tvl": await self.get_tvl(),
            "total_volume_24h": await self.get_volume_24h(),
            "pool_count": len(pools),
            "timestamp": datetime.utcnow().isoformat()
        }


# Create global client instance
ekubo_client = EkuboClient()
