#!/usr/bin/env python3
"""
Research Skill - CLI Interface.

Research topics and summarize findings.
"""

import sys
import os
import argparse
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from research import BraveSearch


def main():
    parser = argparse.ArgumentParser(
        description="Research - Topic research and analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("topic", help="Research topic")
    parser.add_argument("--output", "-o", default="summary",
                        choices=["summary", "detailed", "report"],
                        help="Output format")
    parser.add_argument("--json", "-j", action="store_true", help="JSON output")
    
    args = parser.parse_args()
    
    search = BraveSearch()
    
    results = search.search(args.topic)
    
    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        print(results.get("answer", "No results"))


if __name__ == "__main__":
    main()
