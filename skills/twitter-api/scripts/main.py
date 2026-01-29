#!/usr/bin/env python3
"""
Twitter API Skill - Main Entry Point.

CLI interface for Twitter/X operations.
"""

import sys
import os
import argparse
import json
from datetime import datetime

# Add skill scripts to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scripts.api import TwitterClient, get_client
from scripts.post import TweetPoster
from scripts.reply import ReplyManager
from scripts.quote import QuoteManager


def cmd_post(args):
    """Post a tweet."""
    poster = TweetPoster()
    result = poster.post(args.text)
    print(json.dumps(result, indent=2))


def cmd_reply(args):
    """Reply to a tweet."""
    reply_mgr = ReplyManager()
    result = reply_mgr.reply_with_context(
        args.tweet_id,
        args.text,
        include_context=not args.no_context
    )
    print(json.dumps(result, indent=2))


def cmd_quote(args):
    """Quote a tweet."""
    quote_mgr = QuoteManager()
    result = quote_mgr.quote(args.tweet_id, args.comment)
    print(json.dumps(result, indent=2))


def cmd_delete(args):
    """Delete a tweet."""
    poster = TweetPoster()
    result = poster.delete_tweet(args.tweet_id)
    print(json.dumps(result, indent=2))


def cmd_get(args):
    """Get tweet details."""
    poster = TweetPoster()
    result = poster.get_tweet(args.tweet_id)
    print(json.dumps(result, indent=2))


def cmd_schedule(args):
    """Schedule a tweet."""
    poster = TweetPoster()
    post_time = datetime.fromisoformat(args.at)
    result = poster.schedule_post(args.text, post_time)
    print(json.dumps(result, indent=2))


def cmd_scheduled(args):
    """List scheduled tweets."""
    poster = TweetPoster()
    scheduled = poster.get_scheduled()
    print(json.dumps(scheduled, indent=2))


def cmd_cancel(args):
    """Cancel scheduled tweet."""
    poster = TweetPoster()
    result = poster.cancel_scheduled(args.file)
    print(json.dumps(result, indent=2))


def cmd_search(args):
    """Search tweets."""
    client = get_client()
    tweets = client.search_recent_tweets(args.query, max_results=args.limit)
    results = [t.to_dict() for t in tweets]
    print(json.dumps(results, indent=2))


def cmd_mentions(args):
    """Get mentions."""
    reply_mgr = ReplyManager()
    mentions = reply_mgr.get_mentions(since_id=args.since, max_results=args.limit)
    print(json.dumps(mentions, indent=2))


def cmd_thread(args):
    """Post a thread."""
    with open(args.file) as f:
        tweets = [line.strip() for line in f if line.strip()]
    
    poster = TweetPoster()
    results = poster.post_thread(tweets, delay_seconds=args.delay)
    print(json.dumps(results, indent=2))


def cmd_whoami(args):
    """Get current user."""
    client = get_client()
    me = client.get_me()
    print(json.dumps(me, indent=2))


def cmd_followers(args):
    """Get followers."""
    client = get_client()
    user_id = args.user_id
    if not user_id:
        user_id = client.get_me()["data"]["id"]
    followers = client.get_followers(user_id, max_results=args.limit)
    print(json.dumps(followers, indent=2))


def cmd_rate(args):
    """Get rate limit status."""
    client = get_client()
    status = client.get_rate_limit_status()
    print(json.dumps(status, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Twitter API Skill - CLI interface",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Post
    post_parser = subparsers.add_parser("post", help="Post a tweet")
    post_parser.add_argument("text", help="Tweet text")
    post_parser.set_defaults(func=cmd_post)
    
    # Reply
    reply_parser = subparsers.add_parser("reply", help="Reply to a tweet")
    reply_parser.add_argument("tweet_id", help="Tweet ID to reply to")
    reply_parser.add_argument("text", help="Reply text")
    reply_parser.add_argument("--no-context", action="store_true", help="Don't add @author prefix")
    reply_parser.set_defaults(func=cmd_reply)
    
    # Quote
    quote_parser = subparsers.add_parser("quote", help="Quote a tweet")
    quote_parser.add_argument("tweet_id", help="Tweet ID to quote")
    quote_parser.add_argument("--comment", "-c", help="Comment to add")
    quote_parser.set_defaults(func=cmd_quote)
    
    # Delete
    delete_parser = subparsers.add_parser("delete", help="Delete a tweet")
    delete_parser.add_argument("tweet_id", help="Tweet ID to delete")
    delete_parser.set_defaults(func=cmd_delete)
    
    # Get
    get_parser = subparsers.add_parser("get", help="Get tweet details")
    get_parser.add_argument("tweet_id", help="Tweet ID")
    get_parser.set_defaults(func=cmd_get)
    
    # Schedule
    schedule_parser = subparsers.add_parser("schedule", help="Schedule a tweet")
    schedule_parser.add_argument("text", help="Tweet text")
    schedule_parser.add_argument("at", help="ISO datetime (e.g., 2024-01-15T14:30:00)")
    schedule_parser.set_defaults(func=cmd_schedule)
    
    # Scheduled list
    subparsers.add_parser("scheduled", help="List scheduled tweets").set_defaults(func=cmd_scheduled)
    
    # Cancel scheduled
    cancel_parser = subparsers.add_parser("cancel", help="Cancel scheduled tweet")
    cancel_parser.add_argument("file", help="Scheduled file name")
    cancel_parser.set_defaults(func=cmd_cancel)
    
    # Search
    search_parser = subparsers.add_parser("search", help="Search tweets")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--limit", "-l", type=int, default=10, help="Max results")
    search_parser.set_defaults(func=cmd_search)
    
    # Mentions
    mentions_parser = subparsers.add_parser("mentions", help="Get mentions")
    mentions_parser.add_argument("--since", "-s", help="Since tweet ID")
    mentions_parser.add_argument("--limit", "-l", type=int, default=20, help="Max results")
    mentions_parser.set_defaults(func=cmd_mentions)
    
    # Thread
    thread_parser = subparsers.add_parser("thread", help="Post a thread from file")
    thread_parser.add_argument("file", help="File with tweets (one per line)")
    thread_parser.add_argument("--delay", "-d", type=int, default=5, help="Delay between tweets")
    thread_parser.set_defaults(func=cmd_thread)
    
    # Whoami
    subparsers.add_parser("whoami", help="Get current user").set_defaults(func=cmd_whoami)
    
    # Followers
    followers_parser = subparsers.add_parser("followers", help="Get followers")
    followers_parser.add_argument("--user-id", "-u", help="User ID (default: self)")
    followers_parser.add_argument("--limit", "-l", type=int, default=100, help="Max results")
    followers_parser.set_defaults(func=cmd_followers)
    
    # Rate limit
    subparsers.add_parser("rate", help="Get rate limit status").set_defaults(func=cmd_rate)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
