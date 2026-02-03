#!/usr/bin/env python3
"""
Publisher Skill CLI - Unified post generation, scheduling, X/Twitter
"""

import argparse
import logging
import sys
import os
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_ROOT))

from main import Publisher, Post

logger = logging.getLogger(__name__)


def main():
    try:
        parser = argparse.ArgumentParser(
            description="Publisher Skill - Unified content publishing",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        subparsers = parser.add_subparsers(dest="command", help="Commands")
        
        # Status
        status_parser = subparsers.add_parser("status", help="Show status")
        
        # Generate
        gen_parser = subparsers.add_parser("generate", help="Generate content")
        gen_parser.add_argument("--topic", "-t", help="Topic")
        gen_parser.add_argument("--style", "-s", default="CT", help="Style")
        
        # Queue
        queue_parser = subparsers.add_parser("queue", help="Queue operations")
        queue_parser.add_argument("--list", action="store_true", help="List queued items")
        queue_parser.add_argument("--post", metavar="ID", help="Post item by ID")
        
        # Twitter
        tw_parser = subparsers.add_parser("twitter", help="Twitter operations")
        tw_parser.add_argument("--post", help="Post tweet")
        tw_parser.add_argument("--reply", help="Reply to tweet")
        
        # Schedule
        schedule_parser = subparsers.add_parser("schedule", help="Schedule post")
        schedule_parser.add_argument("--time", help="Schedule time")
        
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return
        
        if args.command == "status":
            print("Publisher Skill - Active")
            print("Merged: post-generator, queue-manager, twitter-api, x-algorithm-optimizer")
        
        elif args.command == "generate":
            print(f"Generating post about: {args.topic}")
        
        elif args.command == "queue":
            print("Use 'queue-manager' skill directly")
        
        elif args.command == "twitter":
            print("Use 'twitter-api' skill directly")
        
        elif args.command == "schedule":
            print(f"Scheduling for: {args.time}")
        
        else:
            parser.print_help()
    
    except Exception as e:
        logger.error(f"Publisher skill error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
