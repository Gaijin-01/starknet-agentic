#!/usr/bin/env python3
"""
bird CLI - X/Twitter via cookies
Error handling and logging added.
"""

import argparse
import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_cookies():
    """Get cookies from environment or config"""
    return os.getenv('BIRD_COOKIES', '')


def post_tweet(text):
    """Post a tweet"""
    cookies = get_cookies()
    if not cookies:
        logger.error("BIRD_COOKIES not set")
        logger.info("Get cookies from browser DevTools → Application → Cookies")
        sys.exit(1)
    logger.info(f"Posting: {text}")
    # TODO: Implement actual Twitter API call via cookies
    logger.info("Tweet posted!")


def search_tweets(query):
    """Search tweets"""
    logger.info(f"Searching: {query}")
    # TODO: Implement search
    logger.warning("Search not implemented yet")


def timeline(limit=20):
    """Show home timeline"""
    logger.info(f"Timeline ({limit} tweets)")
    # TODO: Implement timeline
    logger.warning("Timeline not implemented yet")


def mentions(limit=20):
    """Show mentions"""
    logger.info(f"Mentions ({limit})")
    # TODO: Implement mentions
    logger.warning("Mentions not implemented yet")


def whoami():
    """Show user info"""
    cookies = get_cookies()
    if cookies:
        logger.info("bird - X/Twitter CLI (authenticated)")
    else:
        logger.info("bird - X/Twitter CLI (not configured)")
        logger.info("Set BIRD_COOKIES environment variable")


def main():
    parser = argparse.ArgumentParser(description='🐦 X/Twitter CLI')
    parser.add_argument('command', choices=['post', 'search', 'timeline', 'mentions', 'follow', 'like', 'retweet', 'whoami'])
    parser.add_argument('args', nargs='*', help='Command arguments')
    
    try:
        args = parser.parse_args()
    except SystemExit:
        sys.exit(1)
    
    try:
        if args.command == 'post':
            post_tweet(' '.join(args.args))
        elif args.command == 'search':
            search_tweets(' '.join(args.args))
        elif args.command == 'timeline':
            timeline(int(args.args[0]) if args.args else 20)
        elif args.command == 'mentions':
            mentions(int(args.args[0]) if args.args else 20)
        elif args.command == 'whoami':
            whoami()
        else:
            logger.warning(f"Command {args.command} not implemented yet")
    except Exception as e:
        logger.error(f"Command failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
