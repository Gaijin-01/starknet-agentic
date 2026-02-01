#!/usr/bin/env python3
"""
Intelligence Skill CLI - Unified research, prices, onchain, CT analysis
"""

import argparse
import logging
import sys
import os
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_ROOT))

from main import Intelligence, SearchResult, PriceData, CTSentiment

logger = logging.getLogger(__name__)


def main():
    try:
        parser = argparse.ArgumentParser(
            description="Intelligence Skill - Unified data gathering",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        subparsers = parser.add_subparsers(dest="command", help="Commands")
        
        # Status
        status_parser = subparsers.add_parser("status", help="Show status")
        
        # Research
        research_parser = subparsers.add_parser("research", help="Run research")
        research_parser.add_argument("query", help="Research query")
        
        # Prices
        prices_parser = subparsers.add_parser("prices", help="Price operations")
        prices_parser.add_argument("--token", "-t", help="Token symbol")
        prices_parser.add_argument("--json", "-j", action="store_true", help="JSON output")
        
        # On-chain
        onchain_parser = subparsers.add_parser("onchain", help="On-chain operations")
        onchain_parser.add_argument("--address", help="Wallet address")
        onchain_parser.add_argument("--whales", action="store_true", help="Show whale activity")
        
        # CT
        ct_parser = subparsers.add_parser("ct", help="Crypto Twitter analysis")
        ct_parser.add_argument("--sentiment", action="store_true", help="Show sentiment")
        ct_parser.add_argument("--user", help="Twitter user")
        
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return
        
        skill = Intelligence()
        
        if args.command == "status":
            print("Intelligence Skill - Active")
            print("Merged: research, prices, onchain, ct-intelligence")
        
        elif args.command == "research":
            print(f"Researching: {args.query}")
        
        elif args.command == "prices":
            print("Use 'prices' skill directly: python3 skills/prices/scripts/main.py")
        
        elif args.command == "onchain":
            print("Use 'crypto-trading' skill for on-chain data")
        
        elif args.command == "ct":
            print("Use 'ct-intelligence' skill for Twitter analysis")
        
        else:
            parser.print_help()
    
    except Exception as e:
        logger.error(f"Intelligence skill error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
