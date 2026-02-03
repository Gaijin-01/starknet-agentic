#!/usr/bin/env python3
"""
Starknet Whale Tracker - Enhanced Quick Check
Uses real whale database + CoinGecko prices + Opportunity Tracking
Features:
- Cross-DEX arbitrage detection
- Triangular arbitrage detection
- Gas estimation
- Slippage simulation
"""
import asyncio
import os
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from config import DEFAULT_CONFIG
from whales_real import get_stats as get_whale_stats, get_by_tag
from arbitrage import ArbitrageScanner, GasEstimator, SlippageSimulator
from tracking import OpportunityTracker, get_tracker


async def check_and_report():
    """Check for activity and print alerts"""
    alerts = []
    tracker = get_tracker()

    # Load history on startup
    tracker.load_history()

    try:
        # 1. Whale database stats
        stats = get_whale_stats()
        
        # 2. Smart money activity (would check DB in production)
        smart_money = get_by_tag("smart_money")
        
        # 3. Initialize estimators
        gas_estimator = GasEstimator(eth_price_usd=2200)
        slippage_sim = SlippageSimulator()
        
        # 4. Arbitrage scanning
        scanner = ArbitrageScanner(
            rpc_url=os.getenv("STARKNET_RPC_URL", DEFAULT_CONFIG.starknet.rpc_url),
            min_profit_percent=0.05,
            gas_cost_usd=0.10
        )

        print('📊 Scanning arbitrage...')
        print('   (Cross-DEX + Triangular + Gas + Slippage)')
        opps = await scanner.scan()

        # 5. Track all opportunities
        if opps:
            for o in opps:
                tracker.log_opportunity(o)

            alerts.append(f"📊 Scanned: {len(opps)} opportunities")

        if opps:
            cross_dex = [o for o in opps if o.details.get('type') == 'cross_dex']
            triangular = [o for o in opps if o.details.get('type') == 'triangular']
            
            if cross_dex:
                alerts.append("🔄 CROSS-DEX ARBITRAGE")
                for o in cross_dex[:2]:
                    alerts.append(
                        f"💰 {o.dex_from} → {o.dex_to}\n"
                        f"   Path: {' → '.join(o.token_path)}\n"
                        f"   Profit: ${o.estimated_profit:.2f} ({o.profit_percent:.3f}%)\n"
                        f"   Gas: ${o.gas_estimate:.4f}"
                    )
            
            if triangular:
                alerts.append("🔺 TRIANGULAR ARBITRAGE")
                for o in triangular[:2]:
                    alerts.append(
                        f"💰 {o.dex_from} [{o.details.get('steps', 3)} swaps]\n"
                        f"   Path: {' → '.join(o.token_path)}\n"
                        f"   Profit: ${o.estimated_profit:.2f} ({o.profit_percent:.3f}%)\n"
                        f"   Fee: {o.details.get('fee_percent', 0.9):.2f}%"
                    )

        # 6. Gas & Slippage Analysis
        alerts.append("⛽ GAS ESTIMATION")
        gas_tri = gas_estimator.estimate_triangular('ekubo')
        gas_cross = gas_estimator.estimate_cross_dex('ekubo')
        alerts.append(f"   Triangular (3 swaps): {gas_tri['gas_units']:,} units = ${gas_tri['gas_cost_usd']:.4f}")
        alerts.append(f"   Cross-DEX (2 swaps): {gas_cross['gas_units']:,} units = ${gas_cross['gas_cost_usd']:.4f}")

        alerts.append("📉 SLIPPAGE CURVE (Ekubo)")
        for size in ['1k', '5k', '10k']:
            slip = slippage_sim.calculate_slippage(size)
            alerts.append(f"   {size}: {slip['slippage_percent']:.2f}% slippage")

        # 7. Optimal size recommendation
        alerts.append("🎯 OPTIMAL SIZE (0.5% spread)")
        opt = slippage_sim.get_optimal_size(spread_percent=0.5, gas_cost_usd=0.15)
        alerts.append(f"   {opt['optimal_size_formatted']} → ~${opt['expected_profit_usd']} profit")

        # 8. Summary with tracking stats
        tracking_stats = tracker.get_stats()
        alerts.append(
            f"📊 WHALE DATABASE\n"
            f"Total: {stats['total_whales']}\n"
            f"  Foundation: {stats['by_category'].get('foundation', 0)}\n"
            f"  Protocols: {stats['by_category'].get('protocol', 0)}\n"
            f"  Smart Money: {len(smart_money)}\n"
            f"Arbitrage: {len(opps)} opportunities"
        )

        # 9. Tracking stats with variance/lifespan
        if tracking_stats["total"] > 0:
            alerts.append(
                f"📈 TRACKING STATS\n"
                f"Total logged: {tracking_stats['total']}\n"
                f"Executed: {tracking_stats['executed']}\n"
                f"Active: {tracking_stats.get('active_opportunities', 0)}"
            )

            # Calculate variance/stddev by pair
            by_pair = tracker.analyze_by_pair()
            if by_pair:
                alerts.append("📊 PATTERN ANALYSIS")
                for pair, data in sorted(by_pair.items(), key=lambda x: -x[1]['count']):
                    count = data['count']
                    if count >= 2:
                        mean_profit = data.get('avg_profit_percent', 0) or 0
                        alerts.append(f"  {pair}: n={count}, mean={mean_profit:.4f}%")

            # Variance & lifespan metrics
            if tracking_stats["avg_variance"] is not None:
                alerts.append(f"📉 Variance: {tracking_stats['avg_variance']:+.1f}%")
            if tracking_stats["avg_gas"] is not None:
                alerts.append(f"⛽ Avg gas: ${tracking_stats['avg_gas']:.4f}")

            # Stability signal
            total = tracking_stats["total"]
            if total >= 4:
                variance = tracking_stats["avg_variance"]
                if variance is not None and abs(variance) < 5:
                    alerts.append("✅ LOW VARIANCE — pattern stable")

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
