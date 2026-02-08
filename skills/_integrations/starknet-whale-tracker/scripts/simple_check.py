#!/usr/bin/env python3
"""
Starknet Whale Tracker - Simplified Version
Works without starknet.py (Python 3.14 compatible)
"""
import asyncio
import sys
from pathlib import Path

# Use absolute paths for cron compatibility
CLAWD_DIR = Path("/home/wner/clawd")
SCRIPTS_DIR = CLAWD_DIR / "skills" / "_integrations" / "starknet-whale-tracker" / "scripts"

# Add paths
sys.path.insert(0, str(SCRIPTS_DIR))

# Import whales_real
import importlib.util
spec = importlib.util.spec_from_file_location("whales_real", str(SCRIPTS_DIR / "whales_real.py"))
whales_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(whales_module)
get_stats = whales_module.get_stats
get_by_tag = whales_module.get_by_tag

# Import coingecko using absolute path
COINGECKO_PATH = CLAWD_DIR / "skills" / "_system" / "prices" / "scripts" / "coingecko_client.py"
sys.path.insert(0, str(COINGECKO_PATH.parent))
cg_spec = importlib.util.spec_from_file_location("coingecko_client", str(COINGECKO_PATH))
cg_module = importlib.util.module_from_spec(cg_spec)
cg_spec.loader.exec_module(cg_module)
CoinGeckoClient = cg_module.CoinGeckoClient


async def simple_check():
    """Quick check without starknet.py"""
    print("=" * 50)
    print("🐋 STARKNET WHALE TRACKER (Simplified)")
    print("=" * 50)
    
    # 1. Whale database
    print("\n📋 WHALE DATABASE")
    stats = get_stats()
    print(f"Total whales: {stats['total_whales']}")
    print(f"  Foundation: {stats['by_category'].get('foundation', 0)}")
    print(f"  Protocols: {stats['by_category'].get('protocol', 0)}")
    print(f"  Smart Money: {len(get_by_tag('smart_money'))}")
    
    # 2. Prices
    print("\n💰 MARKET PRICES")
    try:
        async with CoinGeckoClient() as cg:
            prices = await cg.get_prices(
                ["starknet", "ethereum", "bitcoin"],
                currency="usd",
                include_24h_change=True
            )
            
            for token, data in prices.items():
                change = data.get("usd_24h_change", 0)
                emoji = "📈" if change > 0 else "📉"
                print(f"  {token}: ${data['usd']:,.4f} {emoji} {change:+.2f}%")
    except Exception as e:
        print(f"  Price fetch failed: {e}")
    
    # 3. Sample whales
    print("\n🐋 SAMPLE WHALES")
    whales = get_by_tag("foundation")[:2]
    for w in whales:
        print(f"  {w.address[:16]}... | {w.name}")
    
    print("\n✅ Status: Simplified mode")
    print("   Install starknet-py (Python 3.10-3.12) for full features")


if __name__ == "__main__":
    asyncio.run(simple_check())
