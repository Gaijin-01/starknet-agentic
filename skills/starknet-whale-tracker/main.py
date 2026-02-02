#!/usr/bin/env python3
"""Whale tracker main entry point."""

import asyncio
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from arbitrage_tracker import ArbitrageTracker


async def main():
    """Main entry point for whale tracking."""
    tracker = ArbitrageTracker()
    
    try:
        # Get market summary
        print("🐋 Starknet Whale Tracker")
        print("=" * 50)
        
        summary = await tracker.get_market_summary()
        print(f"\n📊 Market Summary")
        print(f"   TVL: ${summary.get('total_tvl_usd', 0):,.0f}")
        print(f"   24h Volume: ${summary.get('volume_24h_usd', 0):,.0f}")
        print(f"   Pools: {summary.get('pool_count', 0)}")
        
        # Get arbitrage opportunities
        opportunities = await tracker.get_arbitrage_opportunities()
        print(f"\n💰 Arbitrage Opportunities")
        print(f"   Found: {len(opportunities)}")
        
        for opp in opportunities[:5]:
            print(f"\n   Trade: {opp.token_a[:10]}... → {opp.token_b[:10]}...")
            print(f"   Profit: {opp.profit_percent:.2f}% (${opp.profit_usd:.2f})")
            print(f"   Depth: ${opp.depth:,.0f}")
            print(f"   Confidence: {opp.confidence:.0%}")
        
        # Get whale movements
        movements = await tracker.get_whale_movements()
        print(f"\n🐋 Recent Whale Movements")
        print(f"   Found: {len(movements)}")
        
        for move in movements[:3]:
            print(f"   {move['type']}: {move['value']} {move['token']}")
            print(f"   {move['address'][:16]}...")
    
    finally:
        await tracker.close()


if __name__ == "__main__":
    asyncio.run(main())
