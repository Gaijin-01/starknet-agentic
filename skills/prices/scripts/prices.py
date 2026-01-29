#!/usr/bin/env python3
"""
prices.py - Universal price fetching skill

Supports crypto (CoinGecko) and stocks (Yahoo Finance)
"""

import os
import sys
import json
import logging
import argparse
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from abc import ABC, abstractmethod

# Add parent to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "config"))
from config_loader import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================
# PRICE PROVIDER INTERFACE
# ============================================

class PriceProvider(ABC):
    """Base class for price providers"""
    
    @abstractmethod
    def get_price(self, asset_id: str) -> Optional[Dict]:
        """Get price for single asset"""
        pass
    
    @abstractmethod
    def get_prices(self, asset_ids: List[str]) -> List[Dict]:
        """Get prices for multiple assets"""
        pass


# ============================================
# COINGECKO (Crypto)
# ============================================

class CoinGeckoProvider(PriceProvider):
    """CoinGecko API (free tier)."""
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    def _request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make API request"""
        params = params or {}
        url = f"{self.BASE_URL}{endpoint}"
        
        if params:
            url += "?" + urllib.parse.urlencode(params)
        
        headers = {'Accept': 'application/json'}
        if self.api_key:
            headers['x-cg-demo-api-key'] = self.api_key
        
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    
    def get_price(self, asset_id: str) -> Optional[Dict]:
        """Get price for single crypto asset"""
        try:
            data = self._request('/simple/price', {
                'ids': asset_id.lower(),
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_7d_change': 'true',
                'include_market_cap': 'true'
            })
            
            if asset_id.lower() not in data:
                logger.warning(f"Asset not found: {asset_id}")
                return None
            
            info = data[asset_id.lower()]
            return {
                'asset_id': asset_id,
                'price': info.get('usd', 0),
                'change_24h': info.get('usd_24h_change', 0),
                'change_7d': info.get('usd_7d_change', 0),
                'market_cap': info.get('usd_market_cap', 0),
                'provider': 'coingecko',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"CoinGecko error: {e}")
            return None
    
    def get_prices(self, asset_ids: List[str]) -> List[Dict]:
        """Get prices for multiple assets"""
        ids_str = ','.join([a.lower() for a in asset_ids])
        
        try:
            data = self._request('/simple/price', {
                'ids': ids_str,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_7d_change': 'true'
            })
            
            results = []
            for asset_id in asset_ids:
                key = asset_id.lower()
                if key in data:
                    info = data[key]
                    results.append({
                        'asset_id': asset_id,
                        'price': info.get('usd', 0),
                        'change_24h': info.get('usd_24h_change', 0),
                        'change_7d': info.get('usd_7d_change', 0),
                        'provider': 'coingecko',
                        'timestamp': datetime.now().isoformat()
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"CoinGecko batch error: {e}")
            return []


# ============================================
# YAHOO FINANCE (Stocks)
# ============================================

class YahooFinanceProvider(PriceProvider):
    """Yahoo Finance API (unofficial)."""
    
    BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart"
    
    def __init__(self):
        pass
    
    def get_price(self, symbol: str) -> Optional[Dict]:
        """Get price for single stock"""
        try:
            url = f"{self.BASE_URL}/{symbol.upper()}"
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
            
            result = data.get('chart', {}).get('result', [])
            if not result:
                return None
            
            meta = result[0].get('meta', {})
            return {
                'asset_id': symbol.upper(),
                'symbol': symbol.upper(),
                'price': meta.get('regularMarketPrice', 0),
                'previous_close': meta.get('previousClose', 0),
                'change_24h': ((meta.get('regularMarketPrice', 0) / meta.get('previousClose', 1)) - 1) * 100,
                'currency': meta.get('currency', 'USD'),
                'provider': 'yahoo_finance',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Yahoo Finance error: {e}")
            return None
    
    def get_prices(self, symbols: List[str]) -> List[Dict]:
        """Get prices for multiple stocks"""
        results = []
        for symbol in symbols:
            price = self.get_price(symbol)
            if price:
                results.append(price)
        return results


# ============================================
# PROVIDER FACTORY
# ============================================

def get_provider(cfg: Config) -> PriceProvider:
    """Get price provider based on config."""
    
    provider_name = cfg.get('apis.prices.provider', 'coingecko')
    api_key = cfg.get_api_key('prices')
    
    if provider_name in ['coingecko', 'coinmarketcap']:
        return CoinGeckoProvider(api_key)
    
    elif provider_name in ['yahoo_finance', 'alpha_vantage']:
        return YahooFinanceProvider()
    
    else:
        logger.warning(f"Unknown provider: {provider_name}, using CoinGecko")
        return CoinGeckoProvider()


# ============================================
# POST FORMATTING
# ============================================

def format_price_post(price_data: Dict, cfg: Config) -> str:
    """Format price data as post using config templates."""
    
    template = cfg.get_template('price')
    
    # Determine direction emoji
    change = price_data.get('change_24h', 0)
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
    asset = cfg.get_asset(price_data['asset_id'])
    display = asset.get('display', price_data['asset_id']) if asset else price_data['asset_id']
    
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
# MAIN FUNCTION
# ============================================

def get_prices(
    asset: Optional[str] = None,
    all_assets: bool = False,
    format_as: str = "json",
    output_file: Optional[str] = None
) -> Dict:
    """
    Get prices for assets
    
    Args:
        asset: Single asset symbol
        all_assets: Get all tracked assets
        format_as: json | post
        output_file: Optional file to save
    
    Returns:
        Dict with price data
    """
    cfg = Config()
    provider = get_provider(cfg)
    
    results = []
    
    if asset:
        # Look up asset in config
        asset_cfg = cfg.get_asset(asset)
        asset_id = asset_cfg.get('id', asset) if asset_cfg else asset
        
        price = provider.get_price(asset_id)
        if price:
            results.append(price)
    
    elif all_assets:
        # Get all configured assets
        assets_cfg = cfg.assets
        
        # Crypto assets
        crypto = assets_cfg.get('crypto', [])
        if crypto:
            ids = [a['id'] for a in crypto if 'id' in a]
            results.extend(provider.get_prices(ids))
        
        # Stock assets (if using yahoo)
        stocks = assets_cfg.get('stocks', [])
        if stocks and isinstance(provider, YahooFinanceProvider):
            symbols = [s['symbol'] for s in stocks if 'symbol' in s]
            results.extend(provider.get_prices(symbols))
    
    output = {
        'timestamp': datetime.now().isoformat(),
        'count': len(results),
        'prices': results
    }
    
    # Save to file
    if output_file:
        path = Path(output_file).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(output, f, indent=2)
        logger.info(f"Saved to: {path}")
    
    return output


# ============================================
# CLI
# ============================================

def main():
    parser = argparse.ArgumentParser(description="Universal price fetching skill")
    parser.add_argument("--asset", "-a", help="Asset symbol (e.g., STRK, ETH, AAPL)")
    parser.add_argument("--all", action="store_true", help="Get all tracked assets")
    parser.add_argument("--format", choices=["json", "post"], default="json", help="Output format")
    parser.add_argument("--output", "-o", help="Output file path")
    
    args = parser.parse_args()
    
    if not args.asset and not args.all:
        parser.error("Either --asset or --all required")
    
    result = get_prices(
        asset=args.asset,
        all_assets=args.all,
        output_file=args.output
    )
    
    cfg = Config()
    
    if args.format == "post":
        for price in result['prices']:
            post = format_price_post(price, cfg)
            print(post)
            print()
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
