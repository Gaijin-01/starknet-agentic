#!/usr/bin/env python3
"""
Prices Skill - CLI Interface.

Checks cryptocurrency prices and alerts.
"""

import sys
import os
import argparse
import json
import logging

# Import module functions directly
from prices import get_prices

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


def main():
    """Main entry point with error handling."""
    parser = argparse.ArgumentParser(
        description="Prices - Cryptocurrency price checking",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--token", "-t", help="Token symbol (e.g., BTC, ETH)")
    parser.add_argument("--all", "-a", action="store_true", help="Get all tracked assets")
    parser.add_argument("--json", "-j", action="store_true", help="JSON output")
    
    args = parser.parse_args()
    
    try:
        if args.token:
            result = get_prices(asset=args.token)
        elif args.all:
            result = get_prices(all_assets=True)
        else:
            # Default: get a few key assets
            result = get_prices(asset="STRK")
        
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            for item in result.get('prices', []):
                print(f"{item.get('asset_id', '?')}: ${item.get('price', 0):,.2f}")
    except Exception as e:
        logger.error(f"Error fetching prices: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
