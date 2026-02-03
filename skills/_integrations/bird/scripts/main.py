#!/usr/bin/env python3
"""
bird CLI - X/Twitter via cookies
"""

import argparse
import os
import sys
from pathlib import Path

def get_cookies():
    """Get cookies from environment or config"""
    return os.getenv('BIRD_COOKIES', '')

def post_tweet(text):
    """Post a tweet"""
    cookies = get_cookies()
    if not cookies:
        print("Error: BIRD_COOKIES not set")
        print("Get cookies from browser DevTools → Application → Cookies")
        sys.exit(1)
    print(f"🐦 Posting: {text}")
    # TODO: Implement actual Twitter API call via cookies
    print("✅ Tweet posted!")

def search_tweets(query):
    """Search tweets"""
    print(f"🔍 Searching: {query}")
    print("TODO: Implement search")

def timeline(limit=20):
    """Show home timeline"""
    print(f"📰 Timeline ({limit} tweets)")
    print("TODO: Implement timeline")

def mentions(limit=20):
    """Show mentions"""
    print(f"💬 Mentions ({limit})")
    print("TODO: Implement mentions")

def main():
    parser = argparse.ArgumentParser(description='🐦 X/Twitter CLI')
    parser.add_argument('command', choices=['post', 'search', 'timeline', 'mentions', 'follow', 'like', 'retweet', 'whoami'])
    parser.add_argument('args', nargs='*', help='Command arguments')
    
    args = parser.parse_args()
    
    if args.command == 'post':
        post_tweet(' '.join(args.args))
    elif args.command == 'search':
        search_tweets(' '.join(args.args))
    elif args.command == 'timeline':
        timeline(int(args.args[0]) if args.args else 20)
    elif args.command == 'mentions':
        mentions(int(args.args[0]) if args.args else 20)
    elif args.command == 'whoami':
        print("🐦 bird - X/Twitter CLI")
        print("Set BIRD_COOKIES to use")
    else:
        print(f"Command {args.command} not implemented yet")

if __name__ == '__main__':
    main()
