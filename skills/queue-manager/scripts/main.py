#!/usr/bin/env python3
"""
Queue Manager Skill - CLI Interface.

Manages task queues for scheduled operations.
"""

import sys
import os
import argparse
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from queue_manager import QueueManager


def main():
    parser = argparse.ArgumentParser(
        description="Queue Manager - Task queue operations",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # List queue
    list_parser = subparsers.add_parser("list", help="List queued tasks")
    list_parser.add_argument("--status", choices=["pending", "running", "completed", "failed"])
    list_parser.add_argument("--limit", type=int, default=20)
    
    # Add task
    add_parser = subparsers.add_parser("add", help="Add task to queue")
    add_parser.add_argument("--skill", required=True)
    add_parser.add_argument("--params", help="JSON params")
    add_parser.add_argument("--schedule", help="ISO datetime")
    
    # Status
    subparsers.add_parser("status", help="Show queue status")
    
    # Cleanup
    gc_parser = subparsers.add_parser("gc", help="Garbage collect old tasks")
    gc_parser.add_argument("--max-age-hours", type=int, default=24)
    
    args = parser.parse_args()
    
    manager = QueueManager()
    
    if args.command == "list":
        tasks = manager.list_tasks(status=args.status, limit=args.limit)
        print(json.dumps(tasks, indent=2, default=str))
        
    elif args.command == "add":
        params = json.loads(args.params) if args.params else {}
        task = manager.add_task(args.skill, params, args.schedule)
        print(json.dumps(task, indent=2, default=str))
        
    elif args.command == "status":
        status = manager.get_status()
        print(json.dumps(status, indent=2, default=str))
        
    elif args.command == "gc":
        count = manager.cleanup(max_age_hours=args.max_age_hours)
        print(json.dumps({"cleaned": count}, indent=2))
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
