"""
Quick Demo Script for Starknet Intelligence Colony
===================================================
Demonstrate key features without running full system.
"""

import asyncio
from pathlib import Path
import sys

# Add parent to path for direct execution
sys.path.insert(0, str(Path(__file__).parent.parent))


async def demo():
    print("""
    🧠 Starknet Intelligence Colony
    ═══════════════════════════════════
    
    Running quick demo...
    """)

    # 1. Test Shared State
    print("\n📦 1. Testing Shared State...")
    from colony.shared_state import shared_state, MarketData, ArbitrageOpportunity
    
    market_data = MarketData(
        timestamp="2024-01-01T12:00:00",
        prices={"ETH": 3500, "STRK": 0.85, "USDC": 1.0},
        volumes={"ETH": 1000000},
        changes_24h={"ETH": 2.5, "STRK": -1.2}
    )
    await shared_state.update_market_data(market_data)
    print("   ✅ Market data updated")

    opp = ArbitrageOpportunity(
        token="STRK",
        buy_dex="ekubo",
        sell_dex="jediswap",
        buy_price=0.82,
        sell_price=0.88,
        profit_percent=7.3,
        volume_usd=50000
    )
    await shared_state.add_arbitrage(opp)
    print("   ✅ Arbitrage opportunity added")

    # 2. Test CoinGecko Client
    print("\n💰 2. Testing CoinGecko Client...")
    from colony.clients.coingecko_client import coingecko_client
    
    prices = await coingecko_client.get_price(["ethereum", "starknet"])
    if prices:
        print(f"   ✅ Got prices for {len(prices)} tokens")
    else:
        print("   ⚠️  Price fetch failed (API limit)")

    # 3. Test Ekubo Client
    print("\n⚡ 3. Testing Ekubo Client...")
    from colony.clients.ekubo_client import ekubo_client
    
    pools = await ekubo_client.get_pools()
    print(f"   ✅ Found {len(pools)} pools")
    
    tvl = await ekubo_client.get_tvl()
    print(f"   ✅ Total TVL: ${tvl:,.0f}")

    # 4. Test Whale DB Client
    print("\n🐋 4. Testing Whale DB Client...")
    from colony.clients.whale_db_client import whale_db_client
    
    txs = await whale_db_client.get_sample_transactions(limit=5)
    print(f"   ✅ Found {len(txs)} sample whale transactions")
    
    summary = await whale_db_client.get_whale_movement_summary()
    print(f"   ✅ 24h volume: ${summary['total_volume_usd']:,.0f}")

    # 5. Test Market Agent
    print("\n📊 5. Testing Market Agent...")
    from colony.agents.market_agent import MarketAgent
    
    agent = MarketAgent()
    summary = await agent.get_market_summary()
    print(f"   ✅ Market summary: {summary.total_tvl:,.0f} TVL")

    # 6. Test Content Agent
    print("\n📝 6. Testing Content Agent...")
    from colony.agents.content_agent import ContentAgent
    
    agent = ContentAgent()
    brief = await agent._generate_market_brief({
        "prices": {"prices": {"ETH": 3500, "STRK": 0.85}},
        "arbitrage_count": 3,
        "whale_count": 5
    })
    print(f"   ✅ Generated: {brief.title}")

    # 7. Test Research Agent
    print("\n📚 7. Testing Research Agent...")
    from colony.agents.research_agent import ResearchAgent
    
    agent = ResearchAgent()
    thesis = await agent.generate_investment_thesis("Ekubo")
    print(f"   ✅ Generated thesis for Ekubo")

    # 8. Get Colony Status
    print("\n🔍 8. Colony Status...")
    status = await shared_state.get_snapshot()
    print(f"   ✅ Market data: {'✓' if status['market_data'] else '✗'}")
    print(f"   ✅ Arbitrage: {status['arbitrage_count']} opportunities")
    print(f"   ✅ Whales: {status['whale_count']} tracked")

    print("""
    ═══════════════════════════════════
    ✅ Demo Complete!
    
    To run the full system:
    $ python3 -m colony.main
    
    To run the dashboard:
    $ python3 -m colony.dashboard.app
    
    To run scheduled reports:
    $ python3 -m colony.cron_integration
    """)


if __name__ == "__main__":
    asyncio.run(demo())
