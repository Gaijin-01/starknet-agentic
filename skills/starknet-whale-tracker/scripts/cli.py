#!/usr/bin/env python3
"""
Starknet Whale Tracker - CLI Interface
"""
import argparse
import asyncio
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import DEFAULT_CONFIG
from tracker import StarknetWhaleTracker, create_tracker
from whale_db import WhaleDatabase, WhaleWallet


def cmd_start(args):
    """Start monitoring"""
    tracker = create_tracker(
        rpc_url=args.rpc or DEFAULT_CONFIG.starknet.rpc_url,
        db_path=args.db or "./data/whales.db",
        telegram_token=args.telegram_token or "",
        telegram_chat_id=args.telegram_chat or ""
    )

    # Register alert callback
    def on_alert(message, data):
        print(f"\n🚨 {message}")

    tracker.on_alert(on_alert)

    try:
        asyncio.run(tracker.start(mode=args.mode))
    except KeyboardInterrupt:
        print("\n🛑 Interrupted")


def cmd_stop(args):
    """Stop monitoring"""
    print("Use Ctrl+C to stop the tracker")


def cmd_track(args):
    """Track a new wallet"""
    tracker = create_tracker(
        rpc_url=args.rpc or DEFAULT_CONFIG.starknet.rpc_url,
        db_path=args.db or "./data/whales.db"
    )

    tags = args.tags.split(",") if args.tags else ["whale"]
    alert_on = args.alert_on.split(",") if args.alert_on else ["large_transfer", "new_position"]

    asyncio.run(tracker.track_wallet(
        address=args.address,
        tags=tags,
        alert_on=alert_on
    ))

    print(f"✅ Now tracking {args.address[:20]}... [{', '.join(tags)}]")


def cmd_untrack(args):
    """Stop tracking a wallet"""
    db = WhaleDatabase(args.db or "./data/whales.db")
    deleted = db.delete_whale(args.address)

    if deleted:
        print(f"✅ Removed {args.address[:20]}... from tracking")
    else:
        print(f"⚠️ Wallet not found")


def cmd_list(args):
    """List tracked whales"""
    db = WhaleDatabase(args.db or "./data/whales.db")

    if args.tag:
        whales = db.get_by_tag(args.tag)
    else:
        whales = db.get_all_whales()

    if not whales:
        print("No whales tracked")
        return

    print(f"\n🐋 Tracked Whales ({len(whales)}):")
    print("-" * 80)

    for whale in whales[:args.limit]:
        last_seen = whale.last_seen[:10] if whale.last_seen else "never"
        print(f"  {whale.address[:20]}... [{', '.join(whale.tags)}] (seen: {last_seen})")


def cmd_activity(args):
    """Show recent activity"""
    db = WhaleDatabase(args.db or "./data/whales.db")
    activities = db.get_recent_activity(hours=args.hours, limit=args.limit)

    if not activities:
        print("No recent activity")
        return

    print(f"\n📜 Recent Activity (last {args.hours}h):")
    print("-" * 80)

    for activity in activities:
        print(f"  {activity.timestamp[:19]} | {activity.event_type:20} | {activity.wallet_address[:16]}...")


def cmd_arbitrage(args):
    """Scan for arbitrage opportunities"""
    from arbitrage import ArbitrageScanner

    scanner = ArbitrageScanner(
        min_profit_percent=args.min_profit or 0.5,
        dexes=args.dexes.split(",") if args.dexes else ["jediswap", "ekubo", "10k"]
    )

    opportunities = asyncio.run(scanner.scan())

    if not opportunities:
        print("No profitable opportunities found")
        return

    print(f"\n💰 Arbitrage Opportunities ({len(opportunities)}):")
    print("-" * 80)

    for i, opp in enumerate(opportunities[:args.limit], 1):
        print(f"\n{i}. {opp.dex_from} → {opp.dex_to}")
        print(f"   Path: {' → '.join(opp.token_path)}")
        print(f"   Profit: ${opp.estimated_profit:.2f} ({opp.profit_percent:.2f}%)")
        print(f"   Volume: ${opp.volume_optimal:.0f}")
        print(f"   Confidence: {opp.confidence * 100:.0f}%")


def cmd_stats(args):
    """Show database statistics"""
    db = WhaleDatabase(args.db or "./data/whales.db")
    stats = db.get_whale_stats()

    print("\n📊 Whale Database Stats:")
    print("-" * 40)
    print(f"  Total whales: {stats['total_whales']}")
    print(f"  Activity today: {stats['activity_today']}")

    if stats.get("by_tag"):
        print("\n  By tag:")
        for tag, count in stats["by_tag"].items():
            print(f"    {tag}: {count}")


def cmd_import(args):
    """Import whales from CSV"""
    db = WhaleDatabase(args.db or "./data/whales.db")
    db.import_from_csv(args.file)
    print(f"✅ Imported whales from {args.file}")


def cmd_export(args):
    """Export whales to CSV"""
    db = WhaleDatabase(args.db or "./data/whales.db")
    db.export_to_csv(args.file)
    print(f"✅ Exported whales to {args.file}")


def cmd_summary(args):
    """Generate summary report"""
    db = WhaleDatabase(args.db or "./data/whales.db")
    stats = db.get_whale_stats()
    activities = db.get_recent_activity(hours=args.hours, limit=10)

    print(f"\n📊 Starknet Whale Tracker Summary")
    print("=" * 50)
    print(f"Tracked whales: {stats['total_whales']}")
    print(f"Activity ({args.hours}h): {stats['activity_today']}")

    print(f"\n🐋 Most Active ({args.hours}h):")
    for activity in activities[:5]:
        print(f"  {activity.event_type}: {activity.wallet_address[:16]}...")

    print(f"\n📈 By Tag:")
    for tag, count in stats.get("by_tag", {}).items():
        print(f"  {tag}: {count}")


def main():
    parser = argparse.ArgumentParser(
        description="🐋 Starknet Whale Tracker - Monitor smart money on Starknet",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py start --mode all          Start all monitoring
  python cli.py track 0x123... --tags deployer  Track a wallet
  python cli.py list                       List tracked whales
  python cli.py activity --hours 24        Show recent activity
  python cli.py arbitrage                  Scan for opportunities
  python cli.py summary --hours 24         Generate daily summary
        """
    )

    parser.add_argument(
        "--rpc",
        help="Starknet RPC URL",
        default=DEFAULT_CONFIG.starknet.rpc_url
    )
    parser.add_argument(
        "--db",
        help="Database path",
        default="./data/whales.db"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # start
    start_parser = subparsers.add_parser("start", help="Start monitoring")
    start_parser.add_argument(
        "--mode",
        choices=["mempool", "arbitrage", "all"],
        default="all",
        help="Monitoring mode"
    )
    start_parser.add_argument(
        "--telegram-token",
        help="Telegram bot token",
        default=""
    )
    start_parser.add_argument(
        "--telegram-chat",
        help="Telegram chat ID",
        default=""
    )
    start_parser.set_defaults(func=cmd_start)

    # track
    track_parser = subparsers.add_parser("track", help="Track a wallet")
    track_parser.add_argument("address", help="Wallet address")
    track_parser.add_argument("--tags", help="Comma-separated tags", default="")
    track_parser.add_argument("--alert-on", help="Alert on events", default="")
    track_parser.set_defaults(func=cmd_track)

    # untrack
    untrack_parser = subparsers.add_parser("untrack", help="Stop tracking a wallet")
    untrack_parser.add_argument("address", help="Wallet address")
    untrack_parser.set_defaults(func=cmd_untrack)

    # list
    list_parser = subparsers.add_parser("list", help="List tracked whales")
    list_parser.add_argument("--tag", help="Filter by tag", default="")
    list_parser.add_argument("--limit", type=int, default=20, help="Max results")
    list_parser.set_defaults(func=cmd_list)

    # activity
    activity_parser = subparsers.add_parser("activity", help="Show recent activity")
    activity_parser.add_argument("--hours", type=int, default=24, help="Hours to look back")
    activity_parser.add_argument("--limit", type=int, default=20, help="Max results")
    activity_parser.set_defaults(func=cmd_activity)

    # arbitrage
    arbitrage_parser = subparsers.add_parser("arbitrage", help="Scan arbitrage")
    arbitrage_parser.add_argument("--min-profit", type=float, help="Min profit %%", default=0.5)
    arbitrage_parser.add_argument("--dexes", help="Comma-separated DEX names")
    arbitrage_parser.add_argument("--limit", type=int, default=10, help="Max results")
    arbitrage_parser.set_defaults(func=cmd_arbitrage)

    # stats
    stats_parser = subparsers.add_parser("stats", help="Show database stats")
    stats_parser.set_defaults(func=cmd_stats)

    # import
    import_parser = subparsers.add_parser("import", help="Import from CSV")
    import_parser.add_argument("file", help="CSV file path")
    import_parser.set_defaults(func=cmd_import)

    # export
    export_parser = subparsers.add_parser("export", help="Export to CSV")
    export_parser.add_argument("file", help="CSV file path")
    export_parser.set_defaults(func=cmd_export)

    # summary
    summary_parser = subparsers.add_parser("summary", help="Generate summary")
    summary_parser.add_argument("--hours", type=int, default=24, help="Hours for report")
    summary_parser.set_defaults(func=cmd_summary)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
