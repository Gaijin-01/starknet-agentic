#!/usr/bin/env python3
"""
Analyze tracking.log and show statistics
Usage: python3 stats.py [--pair STRK-USDC] [--format json|text]
"""
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


TRACKING_LOG = Path(__file__).parent / "tracking.log"


def load_log() -> List[dict]:
    """Load all entries from tracking log"""
    entries = []
    if not TRACKING_LOG.exists():
        return entries

    with open(TRACKING_LOG, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    return entries


def calculate_stats(entries: List[dict]) -> Dict:
    """Calculate statistics from log entries"""
    if not entries:
        return {"error": "No data in tracking log"}

    # Group by unique opportunity (using last entry per opportunity)
    opportunities = {}
    for entry in entries:
        # Create key from pair + dexs
        key = f"{entry.get('dex_from', '')}-{entry.get('dex_to', '')}-{'-'.join(entry.get('token_path', []))}"
        if key not in opportunities:
            opportunities[key] = entry
        else:
            # Update with latest entry (has actual profit if executed)
            opportunities[key] = entry

    opp_list = list(opportunities.values())

    # Basic counts
    executed = [o for o in opp_list if o.get("status") == "executed"]
    scanned = [o for o in opp_list if o.get("status") == "scanned"]
    expired = [o for o in opp_list if o.get("status") == "expired"]

    # Variance calculation
    variances = []
    gas_costs = []
    lifespans = []

    for o in executed:
        est = o.get("estimated_profit", 0) or 0
        act = o.get("actual_profit", 0) or 0
        if est > 0 and act > 0:
            variance = ((act - est) / est) * 100
            variances.append(variance)

        gas = o.get("gas_used")
        if gas:
            gas_costs.append(gas)

        # Calculate lifespan
        if o.get("first_seen") and o.get("executed_at"):
            try:
                first = datetime.fromisoformat(o["first_seen"].replace("Z", ""))
                exec_dt = datetime.fromisoformat(o["executed_at"].replace("Z", ""))
                lifespan_min = (exec_dt - first).total_seconds() / 60
                if lifespan_min > 0:
                    lifespans.append(lifespan_min)
            except ValueError:
                pass

    # By pair analysis
    by_pair = {}
    for o in opp_list:
        pair = o.get("pair", "unknown")
        if pair not in by_pair:
            by_pair[pair] = {"count": 0, "total_estimated": 0, "executed": 0}
        by_pair[pair]["count"] += 1
        by_pair[pair]["total_estimated"] += o.get("estimated_profit", 0) or 0
        if o.get("status") == "executed":
            by_pair[pair]["executed"] += 1

    # By DEX analysis
    by_dex = {}
    for o in opp_list:
        dex = f"{o.get('dex_from', '')} → {o.get('dex_to', '')}"
        if dex not in by_dex:
            by_dex[dex] = {"count": 0, "total_estimated": 0}
        by_dex[dex]["count"] += 1
        by_dex[dex]["total_estimated"] += o.get("estimated_profit", 0) or 0

    return {
        "total_entries": len(entries),
        "unique_opportunities": len(opp_list),
        "status_breakdown": {
            "executed": len(executed),
            "scanned": len(scanned),
            "expired": len(expired)
        },
        "variance": {
            "avg": sum(variances) / len(variances) if variances else None,
            "count": len(variances),
            "min": min(variances) if variances else None,
            "max": max(variances) if variances else None
        },
        "gas": {
            "avg": sum(gas_costs) / len(gas_costs) if gas_costs else None,
            "count": len(gas_costs)
        },
        "lifespan": {
            "avg_min": sum(lifespans) / len(lifespans) if lifespans else None,
            "count": len(lifespans)
        },
        "by_pair": by_pair,
        "by_dex": by_dex
    }


def format_text(stats: Dict) -> str:
    """Format stats as human-readable text"""
    lines = []

    lines.append("📊 ARBITRAGE TRACKING STATS")
    lines.append("=" * 40)

    lines.append(f"\n📈 Overview:")
    lines.append(f"  Total entries: {stats.get('total_entries', 0)}")
    lines.append(f"  Unique opportunities: {stats.get('unique_opportunities', 0)}")

    status = stats.get("status_breakdown", {})
    lines.append(f"  Status breakdown:")
    lines.append(f"    - Executed: {status.get('executed', 0)}")
    lines.append(f"    - Scanned: {status.get('scanned', 0)}")
    lines.append(f"    - Expired: {status.get('expired', 0)}")

    variance = stats.get("variance", {})
    if variance.get("avg") is not None:
        lines.append(f"\n📐 Variance (Actual vs Estimated):")
        lines.append(f"  Avg: {variance['avg']:.1f}%")
        if variance.get("min") is not None:
            lines.append(f"  Min: {variance['min']:.1f}%")
            lines.append(f"  Max: {variance['max']:.1f}%")
        lines.append(f"  Samples: {variance.get('count', 0)}")
    else:
        lines.append(f"\n📐 Variance: No executed opportunities yet")

    gas = stats.get("gas", {})
    if gas.get("avg") is not None:
        lines.append(f"\n⛽ Gas Costs:")
        lines.append(f"  Avg: ${gas['avg']:.4f}")
        lines.append(f"  Samples: {gas.get('count', 0)}")
    else:
        lines.append(f"\n⛽ Gas Costs: No data yet")

    lifespan = stats.get("lifespan", {})
    if lifespan.get("avg_min") is not None:
        lines.append(f"\n⏱️ Opportunity Lifespan:")
        lines.append(f"  Avg: {lifespan['avg_min']:.1f} min")
        lines.append(f"  Samples: {lifespan.get('count', 0)}")
    else:
        lines.append(f"\n⏱️ Lifespan: No executed opportunities")

    by_pair = stats.get("by_pair", {})
    if by_pair:
        lines.append(f"\n💰 By Pair:")
        for pair, data in sorted(by_pair.items(), key=lambda x: x[1]["count"], reverse=True):
            lines.append(f"  {pair}: {data['count']} scans, ${data['total_estimated']:.2f} estimated")

    by_dex = stats.get("by_dex", {})
    if by_dex:
        lines.append(f"\n🔄 By DEX:")
        for dex, data in sorted(by_dex.items(), key=lambda x: x[1]["count"], reverse=True):
            lines.append(f"  {dex}: {data['count']} opps")

    return "\n".join(lines)


def main():
    """Main entry point"""
    format_type = "text"
    filter_pair = None

    # Parse args
    for arg in sys.argv[1:]:
        if arg == "--json":
            format_type = "json"
        elif arg == "--text":
            format_type = "text"
        elif arg.startswith("--pair="):
            filter_pair = arg.split("=", 1)[1]

    entries = load_log()

    if filter_pair:
        entries = [e for e in entries if e.get("pair") == filter_pair]

    stats = calculate_stats(entries)

    if format_type == "json":
        print(json.dumps(stats, indent=2))
    else:
        print(format_text(stats))


if __name__ == "__main__":
    main()
