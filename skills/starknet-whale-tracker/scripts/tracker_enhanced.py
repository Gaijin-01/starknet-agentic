"""
Enhanced Starknet Whale Tracker
Combines real whale database with CoinGecko prices
"""
import asyncio
import os
from datetime import datetime
from typing import Dict, List

from config import DEFAULT_CONFIG
from whales_real import STARKNET_WHALES, get_by_tag, get_stats as get_whale_stats
from arbitrage import ArbitrageScanner


class EnhancedWhaleTracker:
    """
    Enhanced whale tracking with real whale database
    """

    def __init__(self):
        self.rpc_url = os.getenv("STARKNET_RPC_URL", DEFAULT_CONFIG.starknet.rpc_url)
        self.arbitrage_scanner = ArbitrageScanner(
            rpc_url=self.rpc_url,
            min_profit_percent=0.05
        )
        self.alerts: List[Dict] = []
        self.last_scan = None

    async def scan(self) -> Dict:
        """
        Full scan of whale activity and arbitrage
        
        Returns:
            Dict with activity summary
        """
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "whale_activity": self.alerts[-50:],  # Recent alerts
            "arbitrage": [],
            "prices": {},
            "stats": {
                "whales_tracked": len(STARKNET_WHALES),
                "mempool_events": len(self.alerts),
            }
        }

        # 1. Get real DEX prices (with CoinGecko fallback)
        print("💱 Fetching market prices...")
        try:
            prices = await self.arbitrage_scanner.get_prices()
            for dex, dex_prices in prices.items():
                for pair, price in dex_prices.items():
                    results["prices"][f"{dex}:{pair}"] = price
        except Exception as e:
            print(f"⚠️ Price fetch error: {e}")

        # 2. Find arbitrage opportunities
        print("🎯 Scanning arbitrage...")
        try:
            opportunities = await self.arbitrage_scanner.scan()
            results["arbitrage"] = [
                {
                    "dex_from": o.dex_from,
                    "dex_to": o.dex_to,
                    "path": " → ".join(o.token_path),
                    "profit_usd": o.estimated_profit,
                    "profit_percent": o.profit_percent
                }
                for o in opportunities[:5]
            ]
        except Exception as e:
            print(f"⚠️ Arbitrage scan error: {e}")

        # 3. Stats
        results["stats"]["arbitrage_opps"] = len(results["arbitrage"])
        results["stats"]["dex_count"] = len(results["prices"])

        self.last_scan = datetime.utcnow()
        return results

    def add_whale(self, address: str, name: str, category: str, tags: List[str]):
        """Add custom whale to track"""
        from whales_real import WhaleAddress
        whale = WhaleAddress(
            address=address,
            name=name,
            category=category,
            tags=tags,
            source="manual",
            confidence=1.0
        )
        STARKNET_WHALES.append(whale)

    def get_summary(self) -> Dict:
        """Get tracker summary"""
        return {
            "whales": get_whale_stats(),
            "last_scan": self.last_scan.isoformat() if self.last_scan else None,
            "recent_alerts": len(self.alerts)
        }


async def demo():
    """Demo enhanced tracker"""
    
    print("🐋 Enhanced Whale Tracker")
    print("=" * 40)
    
    tracker = EnhancedWhaleTracker()
    
    # Show whale database
    print("\n📊 Whale Database:")
    stats = get_whale_stats()
    print(f"  Total: {stats['total_whales']}")
    for cat, count in stats["by_category"].items():
        print(f"  {cat}: {count}")
    
    # Show smart money
    smart_money = get_by_tag("smart_money")
    print(f"\n🧠 Smart Money: {len(smart_money)}")
    for w in smart_money:
        print(f"  {w.name}")
    
    # Show DeFi protocols
    protocols = get_by_tag("defi")
    print(f"\n🏦 DeFi Protocols: {len(protocols)}")
    for w in protocols:
        print(f"  {w.name}")
    
    # Run scan
    print("\n🔄 Running scan...")
    results = await tracker.scan()
    
    print(f"\n📈 Results:")
    print(f"  Whales tracked: {results['stats']['whales_tracked']}")
    print(f"  Arbitrage opps: {results['stats']['arbitrage_opps']}")
    
    if results["arbitrage"]:
        print(f"\n💰 Arbitrage Opportunities:")
        for opp in results["arbitrage"][:3]:
            print(f"  {opp['dex_from']} → {opp['dex_to']}: ${opp['profit_usd']:.2f} ({opp['profit_percent']:.2f}%)")


if __name__ == "__main__":
    asyncio.run(demo())
