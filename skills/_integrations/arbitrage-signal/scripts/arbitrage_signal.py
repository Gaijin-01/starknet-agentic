#!/usr/bin/env python3
"""
Arbitrage Signal Scanner for Starknet DEXs
Scans for price differences and sends Telegram alerts
"""
import asyncio
import os
import sys
from dataclasses import dataclass
from typing import Dict, List

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import aiohttp
except ImportError:
    print("Install requirements: pip install aiohttp")
    sys.exit(1)


@dataclass
class ArbitrageOpportunity:
    """Arbitrage opportunity details"""
    dex_a: str
    dex_b: str
    pair: str
    price_a: float
    price_b: float
    spread_percent: float
    profit_usd: float
    confidence: float
    
    @property
    def path(self) -> str:
        return f"{self.dex_a} → {self.dex_b}"
    
    @property
    def direction(self) -> str:
        """Which DEX to buy/sell"""
        if self.price_a < self.price_b:
            return f"Buy on {self.dex_a}, Sell on {self.dex_b}"
        return f"Buy on {self.dex_b}, Sell on {self.dex_a}"


class PriceFetcher:
    """Fetch prices from CoinGecko + simulate DEX spreads"""
    
    # Token addresses on Starknet
    TOKENS = {
        "ETH": "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004d7",
        "STRK": "0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d",
        "USDC": "0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8",
        "USDT": "0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8",
        "WBTC": "0x03fe2b97c1fd3528a7c3c6f7a5e6f5a8b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1",
        "LINK": "0x07c8b7a85c5d1bb7a5d3d9e6f8a7c5b4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a",
    }
    
    # DEX spread simulation (small differences)
    SPREADS = {
        "ekubo": 0.0003,    # +0.03%
        "jediswap": 0.0,    # baseline
        "10k": -0.0003,     # -0.03%
    }
    
    async def fetch_coingecko_prices(self) -> Dict[str, float]:
        """Fetch real prices from CoinGecko"""
        try:
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                "vs_currency": "usd",
                "ids": "ethereum,starknet,usd-coin,tether,bitcoin,chainlink",
                "order": "market_cap_desc",
                "per_page": 6,
                "page": 1,
                "sparkline": False
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as resp:
                    if resp.status == 429:
                        print("⚠️ CoinGecko rate limited")
                        return {}
                    if resp.status != 200:
                        print(f"⚠️ CoinGecko error: {resp.status}")
                        return {}
                    
                    data = await resp.json()
                    
                    prices = {}
                    for coin in data:
                        coin_id = coin.get("id")
                        price = coin.get("current_price", 0)
                        
                        mapping = {
                            "ethereum": "ETH",
                            "starknet": "STRK",
                            "usd-coin": "USDC",
                            "tether": "USDT",
                            "bitcoin": "WBTC",
                            "chainlink": "LINK",
                        }
                        
                        if coin_id in mapping:
                            prices[mapping[coin_id]] = price
                    
                    return prices
                    
        except Exception as e:
            print(f"CoinGecko error: {e}")
            return {}
    
    async def get_dex_prices(self) -> Dict[str, Dict[str, float]]:
        """Get prices for each DEX with simulated spreads"""
        base_prices = await self.fetch_coingecko_prices()
        
        if not base_prices:
            return {}
        
        dex_prices = {}
        
        for dex, spread in self.SPREADS.items():
            dex_prices[dex] = {}
            
            # ETH pairs
            if "ETH" in base_prices:
                eth_price = base_prices["ETH"]
                dex_prices[dex]["ETH/USDC"] = eth_price * (1 + spread)
                dex_prices[dex]["ETH/USDT"] = eth_price * (1 + spread * 0.8)
            
            # STRK pairs
            if "STRK" in base_prices and "ETH" in base_prices:
                strk_eth = base_prices["STRK"] / base_prices["ETH"]
                dex_prices[dex]["STRK/ETH"] = strk_eth * (1 + spread)
            
            if "STRK" in base_prices:
                dex_prices[dex]["STRK/USDC"] = base_prices["STRK"] * (1 + spread)
            
            # WBTC pairs
            if "WBTC" in base_prices and "ETH" in base_prices:
                wbtc_eth = base_prices["WBTC"] / base_prices["ETH"]
                dex_prices[dex]["WBTC/ETH"] = wbtc_eth * (1 + spread)
            
            # LINK pairs
            if "LINK" in base_prices and "ETH" in base_prices:
                link_eth = base_prices["LINK"] / base_prices["ETH"]
                dex_prices[dex]["LINK/ETH"] = link_eth * (1 + spread)
        
        return dex_prices


class ArbitrageScanner:
    """Scan for arbitrage opportunities"""
    
    def __init__(self, min_profit_percent: float = 0.3, min_profit_usd: float = 1.0):
        self.min_profit_percent = min_profit_percent
        self.min_profit_usd = min_profit_usd
        self.price_fetcher = PriceFetcher()
    
    async def scan(self) -> List[ArbitrageOpportunity]:
        """Scan all DEXs for arbitrage opportunities"""
        dex_prices = await self.price_fetcher.get_dex_prices()
        
        if not dex_prices:
            return []
        
        opportunities = []
        dexes = list(dex_prices.keys())
        
        # Compare each pair across DEXs
        for i, dex_a in enumerate(dexes):
            for dex_b in dexes[i+1:]:
                for pair in dex_prices[dex_a]:
                    if pair not in dex_prices[dex_b]:
                        continue
                    
                    price_a = dex_prices[dex_a][pair]
                    price_b = dex_prices[dex_b][pair]
                    
                    if price_a == 0 or price_b == 0:
                        continue
                    
                    # Calculate spread
                    higher = max(price_a, price_b)
                    lower = min(price_a, price_b)
                    spread_percent = ((higher - lower) / lower) * 100
                    
                    # Estimate profit (for 1 unit of base token)
                    base_value = lower  # value of 1 unit on lower-priced DEX
                    profit_usd = base_value * (spread_percent / 100) * 0.5  # assume 50% capture
                    
                    # Check thresholds
                    if spread_percent >= self.min_profit_percent and profit_usd >= self.min_profit_usd:
                        # Calculate confidence based on spread size
                        confidence = min(0.95, 0.5 + spread_percent * 2)
                        
                        opp = ArbitrageOpportunity(
                            dex_a=dex_a,
                            dex_b=dex_b,
                            pair=pair,
                            price_a=price_a,
                            price_b=price_b,
                            spread_percent=spread_percent,
                            profit_usd=profit_usd,
                            confidence=confidence
                        )
                        opportunities.append(opp)
        
        # Sort by profit
        return sorted(opportunities, key=lambda x: x.profit_usd, reverse=True)


class ConsoleAlert:
    """Output arbitrage alerts to console (Moltbot delivers to Telegram)"""
    
    def __init__(self):
        pass
    
    def send_opportunities(self, opportunities: List[ArbitrageOpportunity]):
        """Output arbitrage opportunities to stdout"""
        if not opportunities:
            print("🔍 Scan complete: No arbitrage opportunities found.")
            return
        
        # Output each opportunity
        for opp in opportunities[:5]:  # Max 5 per scan
            message = self.format_opportunity(opp)
            print(message)
    
    def format_opportunity(self, opp: ArbitrageOpportunity) -> str:
        """Format opportunity as message"""
        emoji_profit = "💰" if opp.profit_usd > 5 else "🪙"
        emoji_conf = "🎯" if opp.confidence > 0.7 else "🤔"
        
        message = f"""
{emoji_profit} ARBITRAGE SIGNAL
━━━━━━━━━━━━━━━━━━━━━━
📈 PROFIT: ${opp.profit_usd:.2f} ({opp.spread_percent:.2f}%)
{emoji_conf} CONFIDENCE: {opp.confidence*100:.0f}%
📊 PAIR: {opp.pair}

🔄 PATH
{opp.dex_a}: ${opp.price_a:.4f}
{opp.dex_b}: ${opp.price_b:.4f}

🎯 ACTION
{opp.direction}

📝 EXECUTE:
1. Buy on {'lower' if opp.price_a < opp.price_b else 'higher'} DEX
2. Sell on {'higher' if opp.price_a < opp.price_b else 'lower'} DEX
"""
        return message


async def run_scan():
    """Main scan function"""
    # Load config from environment
    min_profit_percent = float(os.getenv("ARBITRAGE_MIN_PROFIT", "0.3"))
    min_profit_usd = float(os.getenv("ARBITRAGE_MIN_USD", "1.0"))
    
    print(f"🔍 Arbitrage Signal Scanner")
    print(f"   Min profit: {min_profit_percent}% / ${min_profit_usd}")
    
    # Scan for opportunities
    scanner = ArbitrageScanner(
        min_profit_percent=min_profit_percent,
        min_profit_usd=min_profit_usd
    )
    
    print("📊 Fetching prices...")
    opportunities = await scanner.scan()
    
    print(f"📈 Found {len(opportunities)} opportunities")
    
    # Display results
    for opp in opportunities[:5]:
        print(f"   {opp.pair}: {opp.dex_a} → {opp.dex_b}: ${opp.profit_usd:.2f} ({opp.spread_percent:.2f}%)")
    
    # Output alerts (Moltbot delivers to Telegram)
    print("\n--- ALERTS ---")
    alert = ConsoleAlert()
    alert.send_opportunities(opportunities)
    print("--- END ---")


def main():
    """Entry point"""
    asyncio.run(run_scan())


if __name__ == "__main__":
    main()
