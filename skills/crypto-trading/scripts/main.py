#!/usr/bin/env python3
"""
Crypto Trading Skill - Main Entry Point.

CLI interface for on-chain metrics, whale tracking, and arbitrage detection.

Error Handling:
- All functions wrap operations in try/except
- Errors logged to console with context
- Non-zero exit codes on failure
"""

#!/usr/bin/env python3
"""Crypto Trading Skill - Main entry point for CLI operations."""

import sys
import os
import argparse
import json
from datetime import datetime

# Add skill directory to path (parent of scripts/)
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SKILL_DIR)

from scripts.metrics import OnChainMetrics, SyncOnChainMetrics
from scripts.whale import WhaleTracker, SyncWhaleTracker
from scripts.arbitrage import ArbitrageDetector, SyncArbitrageDetector


def cmd_metrics(args):
    """Get token metrics."""
    try:
        metrics = SyncOnChainMetrics()
        if args.token:
            result = metrics.get_token_metrics(args.token, args.chain)
            if result:
                print(json.dumps(result.__dict__, indent=2, default=str))
            else:
                print(json.dumps({"error": "Token not found"}, indent=2))
        elif args.search:
            results = metrics.search_tokens(args.search, limit=args.limit)
            print(json.dumps([r.__dict__ for r in results], indent=2, default=str))
        elif args.pools:
            pools = metrics.get_top_pools(args.chain, limit=args.limit)
            print(json.dumps([p.__dict__ for p in pools], indent=2, default=str))
        elif args.trending:
            pools = metrics.get_trending_pools(args.chain, limit=args.limit)
            print(json.dumps([p.__dict__ for p in pools], indent=2, default=str))
        else:
            overview = metrics.get_market_overview(args.chains)
            print(json.dumps(overview, indent=2, default=str))
        metrics.close()
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))
        sys.exit(1)


def cmd_whale(args):
    """Whale tracking commands."""
    try:
        tracker = SyncWhaleTracker()
        
        if args.add:
            tracker.add_tracked_wallet(
                args.add,
                label=args.label,
                tags=args.tags.split(",") if args.tags else []
            )
            print(json.dumps({"status": "added", "address": args.add}))
        elif args.list:
            wallets = tracker.list_tracked_wallets()
            print(json.dumps([w.__dict__ for w in wallets], indent=2, default=str))
        elif args.transactions:
            txs = tracker.get_large_transactions(args.chain, min_value_usd=args.min_value)
            print(json.dumps([tx.__dict__ for tx in txs], indent=2, default=str))
        elif args.wallet:
            txs = tracker.get_wallet_transactions(args.wallet, args.chain)
            print(json.dumps([tx.__dict__ for tx in txs], indent=2, default=str))
        elif args.update:
            updated = tracker.update_tracked_wallets(args.chains)
            print(json.dumps({k: v.__dict__ for k, v in updated.items()}, indent=2, default=str))
        else:
            txs = tracker.get_large_transactions(args.chain, min_value_usd=args.min_value)
            analysis = tracker.analyze_flow(txs)
            sentiment = tracker.get_whale_sentiment(txs)
            print(json.dumps({"analysis": analysis, "sentiment": sentiment}, indent=2, default=str))
        
        tracker.close()
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))
        sys.exit(1)


def cmd_arbitrage(args):
    """Arbitrage detection commands."""
    try:
        detector = SyncArbitrageDetector(
            gas_price_gwei=args.gas,
            profit_threshold_percent=args.threshold
        )
        
        if args.analyze:
            result = detector.analyze_pair(args.analyze, args.quote)
            print(json.dumps(result, indent=2, default=str))
        else:
            opportunities = detector.find_opportunities(
                min_spread_percent=args.threshold,
                max_results=args.limit
            )
            print(json.dumps([opp.__dict__ for opp in opportunities], indent=2, default=str))
        
        detector.close()
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Crypto Trading Skill - CLI interface",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Metrics commands
    metrics_parser = subparsers.add_parser("metrics", help="On-chain metrics")
    metrics_group = metrics_parser.add_mutually_exclusive_group()
    
    metrics_group.add_argument("--token", "-t", help="Token address")
    metrics_group.add_argument("--search", "-s", help="Search tokens")
    metrics_group.add_argument("--pools", "-p", action="store_true", help="Top pools")
    metrics_group.add_argument("--trending", "-T", action="store_true", help="Trending pools")
    
    metrics_parser.add_argument("--chain", "-c", default="ethereum", help="Chain")
    metrics_parser.add_argument("--chains", nargs="+", default=["ethereum", "bsc", "arbitrum"], help="Chains for overview")
    metrics_parser.add_argument("--limit", "-l", type=int, default=10, help="Max results")
    metrics_parser.set_defaults(func=cmd_metrics)
    
    # Whale commands
    whale_parser = subparsers.add_parser("whale", help="Whale tracking")
    whale_group = whale_parser.add_mutually_exclusive_group()
    
    whale_group.add_argument("--add", "-a", help="Add tracked wallet")
    whale_group.add_argument("--list", "-l", action="store_true", help="List tracked wallets")
    whale_group.add_argument("--transactions", "-t", action="store_true", help="Get large transactions")
    whale_group.add_argument("--wallet", "-w", help="Get wallet transactions")
    whale_group.add_argument("--update", "-u", action="store_true", help="Update tracked wallets")
    
    whale_parser.add_argument("--chain", "-c", default="ethereum", help="Chain")
    whale_parser.add_argument("--chains", nargs="+", default=["ethereum", "bsc"], help="Chains to update")
    whale_parser.add_argument("--min-value", "-m", type=float, default=100000, help="Min USD value")
    whale_parser.add_argument("--label", help="Wallet label")
    whale_parser.add_argument("--tags", help="Comma-separated tags")
    whale_parser.set_defaults(func=cmd_whale)
    
    # Arbitrage commands
    arb_parser = subparsers.add_parser("arbitrage", help="Arbitrage detection")
    arb_group = arb_parser.add_mutually_exclusive_group()
    
    arb_group.add_argument("--analyze", "-a", help="Analyze specific pair")
    arb_group.add_argument("--find", "-f", action="store_true", help="Find opportunities")
    
    arb_parser.add_argument("--quote", "-q", default="USDT", help="Quote token for analysis")
    arb_parser.add_argument("--threshold", "-t", type=float, default=1.0, help="Min spread %%")
    arb_parser.add_argument("--gas", "-g", type=float, default=20.0, help="Gas price in Gwei")
    arb_parser.add_argument("--limit", "-l", type=int, default=20, help="Max results")
    arb_parser.set_defaults(func=cmd_arbitrage)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
