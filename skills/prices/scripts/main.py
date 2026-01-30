#!/usr/bin/env python3
"""
Prices Skill - CLI Interface.

Checks cryptocurrency prices and alerts.
"""

import sys
import os
import argparse
import json

# Import module functions directly
from prices import get_prices


def main():
    parser = argparse.ArgumentParser(
        description="Prices - Cryptocurrency price checking",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--token", "-t", help="Token symbol (e.g., BTC, ETH)")
    parser.add_argument("--json", "-j", action="store_true", help="JSON output")
    
    args = parser.parse_args()
    
    if args.token:
        results = get_prices([args.token])
    else:
        results = get_prices(["ethereum", "bitcoin", "tether"])
    
    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        for item in results:
            print(f"{item.get('symbol', '?')}: ${item.get('price', 0):,.2f}")


if __name__ == "__main__":
    main()
