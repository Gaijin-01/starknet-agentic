#!/usr/bin/env python3
"""Price service main entry point."""

import asyncio
import json


async def main():
    """Main entry point for price service."""
    from scripts.prices import PriceService
    
    print("💰 Price Service")
    print("=" * 50)
    
    async with PriceService() as service:
        # Get prices for common tokens
        token_ids = ["ethereum", "starknet", "bitcoin"]
        print(f"\n📊 Fetching prices for: {', '.join(token_ids)}")
        
        prices = await service.get_prices(token_ids)
        
        print(f"\n{'Token':<12} {'Price':<15} {'24h %':<10}")
        print("-" * 40)
        
        for token_id, data in prices.items():
            price = data.get('usd', 0)
            change = data.get('usd_24h_change', 0)
            print(f"{token_id:<12} ${price:<14,.2f} {change:+.2f}%")
        
        # Get OHLCV for analysis
        print(f"\n📈 Bitcoin OHLCV (7 days):")
        ohlcv = await service.get_ohlcv("bitcoin", days="7")
        if ohlcv:
            latest = ohlcv[-1]
            print(f"   Latest: O=${latest.open:.2f}, H=${latest.high:.2f}, L=${latest.low:.2f}, C=${latest.close:.2f}")
            print(f"   Data points: {len(ohlcv)}")


if __name__ == "__main__":
    asyncio.run(main())
