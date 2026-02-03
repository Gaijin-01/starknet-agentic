#!/usr/bin/env python3
"""
prices.py - Universal price fetching skill using real API clients.

Supports crypto (CoinGecko) and integrates with starknet-whale-tracker for DEX prices.
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add parent to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "config"))
from config_loader import Config

# Import real CoinGecko client
from .coingecko_client import CoinGeckoClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)


class PriceService:
    """
    Unified price service using real API clients.
    
    Uses CoinGeckoClient for cryptocurrency prices.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the price service.
        
        Args:
            api_key: Optional CoinGecko API key for higher rate limits
        """
        self.api_key = api_key
        self.client: Optional[CoinGeckoClient] = None
    
    async def _get_client(self) -> CoinGeckoClient:
        """Get or create CoinGecko client."""
        if self.client is None or self.client._session is None or self.client._session.closed:
            self.client = CoinGeckoClient(
                api_key=self.api_key,
                rate_limit_delay=1.5  # Respect free tier limits
            )
        return self.client
    
    async def close(self):
        """Close the client connection."""
        if self.client:
            await self.client.close()
            self.client = None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def get_price(self, token_id: str) -> Optional[Dict]:
        """
        Get current price for a token.
        
        Args:
            token_id: CoinGecko token ID (e.g., "bitcoin", "starknet")
            
        Returns:
            Dict with price data or None if not found
        """
        try:
            client = await self._get_client()
            data = await client.get_price(
                token_id=token_id,
                currency="usd",
                include_24h_change=True,
                include_market_cap=True,
            )
            
            if data:
                return {
                    "token_id": token_id,
                    "price": data.get("usd"),
                    "change_24h": data.get("usd_24h_change"),
                    "market_cap": data.get("usd_market_cap"),
                    "provider": "coingecko",
                    "timestamp": datetime.now().isoformat()
                }
            return None
            
        except Exception as e:
            logger.error(f"Error fetching price for {token_id}: {e}")
            return None
    
    async def get_prices(self, token_ids: List[str]) -> Dict[str, Dict]:
        """
        Get prices for multiple tokens.
        
        Args:
            token_ids: List of CoinGecko token IDs
            
        Returns:
            Dict mapping token ID to price data
        """
        try:
            client = await self._get_client()
            data = await client.get_prices(
                token_ids=token_ids,
                currency="usd",
                include_24h_change=True,
            )
            return data
            
        except Exception as e:
            logger.error(f"Error fetching prices for {token_ids}: {e}")
            return {}
    
    async def get_ohlcv(self, token_id: str, days: str = "7") -> List:
        """
        Get OHLCV data for a token.
        
        Args:
            token_id: CoinGecko token ID
            days: Timeframe (1, 7, 14, 30, 90, 180, 365, or "max")
            
        Returns:
            List of OHLCV data points
        """
        try:
            client = await self._get_client()
            return await client.get_ohlcv(token_id, days=days)
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {token_id}: {e}")
            return []
    
    async def get_top_coins(self, limit: int = 10) -> List[Dict]:
        """
        Get top coins by market cap.
        
        Args:
            limit: Number of coins to return
            
        Returns:
            List of market data
        """
        try:
            client = await self._get_client()
            return await client.get_top_coins(limit=limit)
        except Exception as e:
            logger.error(f"Error fetching top coins: {e}")
            return []


# ============================================
# POST FORMATTING
# ============================================

def format_price_post(price_data: Dict, cfg: Config) -> str:
    """Format price data as post using config templates."""
    
    template = cfg.get_template('price')
    
    # Determine direction emoji
    change = price_data.get('change_24h', 0) or 0
    if change > 5:
        direction = "🚀"
        sentiment = "bullish momentum"
    elif change > 0:
        direction = "📈"
        sentiment = "green candle"
    elif change < -5:
        direction = "💀"
        sentiment = "pain"
    else:
        direction = "📉"
        sentiment = "accumulation zone"
    
    # Get display name
    asset = cfg.get_asset(price_data.get('token_id', ''))
    display = asset.get('display', price_data.get('token_id', 'Unknown')) if asset else price_data.get('token_id', 'Unknown')
    
    # Format price
    price = price_data.get('price', 0)
    if price < 0.01:
        price_str = f"{price:.6f}"
    elif price < 1:
        price_str = f"{price:.4f}"
    elif price < 100:
        price_str = f"{price:.2f}"
    else:
        price_str = f"{price:,.0f}"
    
    post = template.format(
        coin=display,
        symbol=display,
        price=price_str,
        change=f"{change:+.1f}%",
        direction=direction,
        sentiment=sentiment,
        emoji=cfg.get_random_emoji()
    )
    
    return post[:280]


# ============================================
# MAIN FUNCTION (Async)
# ============================================

async def get_prices_async(
    token_ids: List[str],
    format_as: str = "json",
) -> Dict:
    """
    Get prices for tokens using real API.
    
    Args:
        token_ids: List of CoinGecko token IDs
        format_as: "json" or "post"
        
    Returns:
        Dict with price data
    """
    async with PriceService() as service:
        prices = await service.get_prices(token_ids)
        
        # Format for output
        results = []
        for token_id, data in prices.items():
            results.append({
                'token_id': token_id,
                'price': data.get('usd'),
                'change_24h': data.get('usd_24h_change'),
                'provider': 'coingecko',
                'timestamp': datetime.now().isoformat()
            })
        
        return {
            'timestamp': datetime.now().isoformat(),
            'count': len(results),
            'prices': results
        }


# ============================================
# CLI
# ============================================

def main():
    parser = argparse.ArgumentParser(description="Universal price fetching skill")
    parser.add_argument("--asset", "-a", help="Asset symbol (e.g., STRK, ETH, BTC)")
    parser.add_argument("--all", action="store_true", help="Get all tracked assets")
    parser.add_argument("--format", choices=["json", "post"], default="json", help="Output format")
    parser.add_argument("--top", type=int, help="Get top N coins by market cap")
    
    args = parser.parse_args()
    
    import asyncio
    
    async def run():
        async with PriceService() as service:
            if args.top:
                # Get top coins
                coins = await service.get_top_coins(limit=args.top)
                for coin in coins:
                    print(f"{coin['symbol'].upper()}: ${coin['current_price']:,} ({coin.get('price_change_percentage_24h', 0):.2f}%)")
            
            elif args.asset:
                # Get single asset
                price = await service.get_price(args.asset.lower())
                if price:
                    if args.format == "post":
                        cfg = Config()
                        post = format_price_post(price, cfg)
                        print(post)
                    else:
                        print(json.dumps(price, indent=2))
                else:
                    print(f"Price not found for: {args.asset}")
            
            elif args.all:
                # Get all tracked assets
                cfg = Config()
                assets_cfg = cfg.assets
                crypto = assets_cfg.get('crypto', [])
                token_ids = [a['id'] for a in crypto if 'id' in a]
                
                prices = await service.get_prices(token_ids)
                
                if args.format == "post":
                    for token_id, data in prices.items():
                        price_data = {
                            'token_id': token_id,
                            'price': data.get('usd'),
                            'change_24h': data.get('usd_24h_change'),
                        }
                        post = format_price_post(price_data, cfg)
                        print(post)
                        print()
                else:
                    print(json.dumps({
                        'timestamp': datetime.now().isoformat(),
                        'prices': prices
                    }, indent=2))
            
            else:
                parser.error("Either --asset, --all, or --top required")
    
    asyncio.run(run())


if __name__ == "__main__":
    main()
