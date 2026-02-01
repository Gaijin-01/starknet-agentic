#!/usr/bin/env python3
"""
Starknet Whale Tracker - Enhanced Quick Check
Uses real whale database + CoinGecko prices
"""
import asyncio
import os
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from config import DEFAULT_CONFIG
from whales_real import get_stats as get_whale_stats, get_by_tag
from arbitrage import ArbitrageScanner


async def check_and_report():
    """Check for activity and print alerts"""
    alerts = []

    try:
        # 1. Whale database stats
        stats = get_whale_stats()
        
        # 2. Smart money activity (would check DB in production)
        smart_money = get_by_tag("smart_money")
        
        # 3. Arbitrage scanning
        scanner = ArbitrageScanner(
            rpc_url=os.getenv("STARKNET_RPC_URL", DEFAULT_CONFIG.starknet.rpc_url),
            min_profit_percent=0.05,
            gas_cost_usd=0.10
        )

        print('📊 Scanning arbitrage...')
        opps = await scanner.scan()

        if opps:
            for o in opps[:3]:
                alerts.append(
                    f"💰 ARBITRAGE\n"
                    f"{o.dex_from} → {o.dex_to}\n"
                    f"Profit: ${o.estimated_profit:.2f} ({o.profit_percent:.2f}%)\n"
                    f"Path: {' → '.join(o.token_path)}"
                )

        # 4. Summary
        alerts.append(
            f"📊 WHALE DATABASE\n"
            f"Total: {stats['total_whales']}\n"
            f"  Foundation: {stats['by_category'].get('foundation', 0)}\n"
            f"  Protocols: {stats['by_category'].get('protocol', 0)}\n"
            f"  Smart Money: {len(smart_money)}\n"
            f"Arbitrage: {len(opps)} opportunities"
        )

        await scanner.price_fetcher.close()

    except Exception as e:
        alerts.append(f"❌ ERROR: {e}")

    # Output for Moltbot
    if alerts:
        print("=== WHALE TRACKER REPORT ===")
        for alert in alerts:
            print(alert)
            print("---")
    else:
        print("NO ALERTS")


if __name__ == "__main__":
    asyncio.run(check_and_report())
