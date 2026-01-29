#!/usr/bin/env python3
"""
CT Intelligence - Competitor tracking and sentiment analysis for Crypto Twitter.
"""

import argparse
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from tracker import Tracker
from sentiment import SentimentAnalyzer
from alerts import AlertManager, AlertType


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="CT Intelligence - Track competitors and analyze sentiment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Track competitor accounts
  python main.py add VitalikButerin
  python main.py addelon
  
  # List tracked accounts
  python main.py list
  
  # Detect trends
  python main.py trends --hours 24
  
  # Analyze sentiment
  python main.py sentiment "Bitcoin is mooning! 🚀"
  
  # Send test alert
  python main.py alert --type trend --message "New trend detected: AI agents"
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Tracker commands
    tracker_parser = subparsers.add_parser("track", help="Account tracking")
    tracker_parser.add_argument("--add", help="Add account to track")
    tracker_parser.add_argument("--remove", help="Remove account")
    tracker_parser.add_argument("--list", action="store_true", help="List tracked")
    tracker_parser.add_argument("--fetch", metavar="USER", help="Fetch tweets")
    tracker_parser.add_argument("--limit", type=int, default=10, help="Tweet limit")
    
    # Trend commands
    trend_parser = subparsers.add_parser("trends", help="Trend detection")
    trend_parser.add_argument("--hours", type=int, default=24, help="Lookback hours")
    trend_parser.add_argument("--limit", type=int, default=10, help="Max trends")
    
    # Sentiment commands
    sentiment_parser = subparsers.add_parser("sentiment", help="Sentiment analysis")
    sentiment_parser.add_argument("--text", help="Text to analyze")
    sentiment_parser.add_argument("--json", action="store_true", help="JSON output")
    
    # Alert commands
    alert_parser = subparsers.add_parser("alert", help="Alert management")
    alert_parser.add_argument("--type", choices=["mention", "trend", "competitor", "sentiment"],
                            help="Alert type")
    alert_parser.add_argument("--message", "-m", help="Alert message")
    alert_parser.add_argument("--priority", type=int, default=3, help="Priority 1-5")
    alert_parser.add_argument("--list", action="store_true", help="List alerts")
    
    # Status command
    subparsers.add_parser("status", help="Show status")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute commands
    if args.command == "track":
        tracker = Tracker()
        
        if args.add:
            tracker.add_account(args.add)
            print(f"✓ Added {args.add} to tracking")
            
        elif args.remove:
            tracker.remove_account(args.remove)
            print(f"✓ Removed {args.remove} from tracking")
            
        elif args.list:
            accounts = tracker.get_accounts()
            print(f"Tracked accounts ({len(accounts)}):")
            for acc in accounts:
                print(f"  - @{acc}")
                
        elif args.fetch:
            tweets = tracker.fetch_tweets(args.fetch, args.limit)
            print(f"Fetched {len(tweets)} tweets from @{args.fetch}")
            for tweet in tweets[:3]:
                print(f"  - {tweet.get('text', '')[:80]}...")
    
    elif args.command == "trends":
        tracker = Tracker()
        trends = tracker.detect_trends(args.hours)
        print(f"Trends from last {args.hours}h:")
        for i, trend in enumerate(trends[:args.limit], 1):
            print(f"  {i}. {trend.keyword}: {trend.count} mentions")
    
    elif args.command == "sentiment":
        analyzer = SentimentAnalyzer()
        
        if args.text:
            result = analyzer.analyze_text(args.text)
            if args.json:
                import json
                print(json.dumps({
                    "sentiment": result.sentiment,
                    "score": result.score,
                    "keywords": result.keywords,
                    "confidence": result.confidence
                }, indent=2))
            else:
                print(f"Sentiment: {result.sentiment} ({result.score:+.2f})")
                print(f"Keywords: {', '.join(result.keywords) or 'none'}")
                print(f"Confidence: {result.confidence:.2%}")
    
    elif args.command == "alert":
        manager = AlertManager()
        
        if args.list:
            alerts = manager.get_alerts(limit=20)
            print(f"Recent alerts ({len(alerts)}):")
            for alert in alerts[-10:]:
                print(f"  [{alert.type.value}] {alert.message[:60]}...")
        
        elif args.type and args.message:
            alert_type = AlertType(args.type)
            manager.send_alert(alert_type, args.message, args.priority)
            print(f"✓ Alert sent: {args.type}")
    
    elif args.command == "status":
        tracker = Tracker()
        print("CT Intelligence Status")
        print(f"  Tracked accounts: {len(tracker.get_accounts())}")
        print("  Ready for tracking, trends, and alerts")


if __name__ == "__main__":
    main()
