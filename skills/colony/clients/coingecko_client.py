"""
CoinGecko API Client for Starknet Intelligence Colony
======================================================
Real-time price and market data from CoinGecko.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import aiohttp

from ..config import API

logger = logging.getLogger(__name__)


@dataclass
class TokenPrice:
    """Token price data"""
    id: str
    symbol: str
    name: str
    current_price: float
    market_cap: float
    volume_24h: float
    price_change_24h: float
    price_change_percent_24h: float
    price_change_percent_7d: Optional[float]
    price_change_percent_30d: Optional[float]
    last_updated: str
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "symbol": self.symbol,
            "name": self.name,
            "current_price": self.current_price,
            "market_cap": self.market_cap,
            "volume_24h": self.volume_24h,
            "price_change_24h": self.price_change_24h,
            "price_change_percent_24h": self.price_change_percent_24h,
            "price_change_percent_7d": self.price_change_percent_7d,
            "price_change_percent_30d": self.price_change_percent_30d,
            "last_updated": self.last_updated
        }


class CoinGeckoClient:
    """
    Async client for CoinGecko API.
    
    Features:
    - Token price fetching
    - Market data retrieval
    - Historical data
    - Price alerts
    """
    
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or API.COINGECKO_API_KEY
        self.base_url = base_url or API.COINGECKO_BASE_URL
        self._session: Optional[aiohttp.ClientSession] = None
        self._rate_limit_remaining = 100
        
        # Headers
        self._headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": self.api_key
        } if self.api_key else {"accept": "application/json"}
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers=self._headers,
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self._session
    
    async def close(self):
        """Close the HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def _request(self, endpoint: str, params: Dict = None) -> Optional[Any]:
        """Make an API request"""
        session = await self._get_session()
        url = f"{self.base_url}/{endpoint}"
        
        try:
            async with session.get(url, params=params) as response:
                # Update rate limit info
                remaining = response.headers.get("x-ratelimit-remaining")
                if remaining:
                    self._rate_limit_remaining = int(remaining)
                
                if response.status == 429:
                    logger.warning("CoinGecko rate limit hit")
                    await asyncio.sleep(60)
                    return await self._request(endpoint, params)
                
                if response.status != 200:
                    logger.error(f"CoinGecko error: {response.status}")
                    return None
                
                return await response.json()
        
        except aiohttp.ClientError as e:
            logger.error(f"CoinGecko request error: {e}")
            return None
    
    async def get_price(self, 
                       ids: List[str], 
                       vs_currencies: List[str] = ["usd"],
                       include_24hr_change: bool = True,
                       include_24hr_vol: bool = True,
                       include_market_cap: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get current prices for tokens.
        
        Args:
            ids: List of CoinGecko token IDs
            vs_currencies: Currencies to compare against
            include_24hr_change: Include 24h change
            include_24hr_vol: Include 24h volume
            include_market_cap: Include market cap
        
        Returns:
            Dict of token prices
        """
        params = {
            "ids": ",".join(ids),
            "vs_currencies": ",".join(vs_currencies),
            "include_24hr_change": str(include_24hr_change).lower(),
            "include_24hr_vol": str(include_24hr_vol).lower(),
            "include_market_cap": str(include_market_cap).lower()
        }
        
        data = await self._request("simple/price", params)
        
        if data:
            # Transform to cleaner format
            result = {}
            for token_id, prices in data.items():
                result[token_id] = {
                    "usd": prices.get("usd"),
                    "usd_24h_change": prices.get("usd_24h_change"),
                    "usd_24h_vol": prices.get("usd_24h_vol"),
                    "usd_market_cap": prices.get("usd_market_cap")
                }
            return result
        
        return None
    
    async def get_token_price_data(self, 
                                   ids: List[str],
                                   days: int = 1) -> Dict[str, List[Dict]]:
        """
        Get historical price data for tokens.
        
        Args:
            ids: List of CoinGecko token IDs
            days: Number of days of history
        
        Returns:
            Dict of token ID -> price history
        """
        result = {}
        
        for token_id in ids:
            params = {
                "vs_currency": "usd",
                "days": days,
                "interval": "hourly"
            }
            
            data = await self._request(f"coins/{token_id}/market_chart", params)
            
            if data:
                result[token_id] = {
                    "prices": data.get("prices", []),
                    "market_caps": data.get("market_caps", []),
                    "total_volumes": data.get("total_volumes", [])
                }
        
        return result
    
    async def get_coin_data(self, 
                           id: str,
                           localization: bool = False,
                           tickers: bool = True,
                           market_data: bool = True,
                           community_data: bool = False,
                           developer_data: bool = False,
                           sparkline: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get detailed data for a specific token.
        
        Args:
            id: CoinGecko token ID
            localization: Include localization
            tickers: Include ticker info
            market_data: Include market data
            community_data: Include community data
            developer_data: Include developer data
            sparkline: Include sparkline data
        
        Returns:
            Dict of token details
        """
        params = {
            "localization": str(localization).lower(),
            "tickers": str(tickers).lower(),
            "market_data": str(market_data).lower(),
            "community_data": str(community_data).lower(),
            "developer_data": str(developer_data).lower(),
            "sparkline": str(sparkline).lower()
        }
        
        return await self._request(f"coins/{id}", params)
    
    async def get_trending(self, 
                          limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending coins on CoinGecko"""
        data = await self._request("search/trending")
        
        if data and "coins" in data:
            return [
                {
                    "item": {
                        "id": coin["item"]["id"],
                        "name": coin["item"]["name"],
                        "symbol": coin["item"]["symbol"],
                        "market_cap_rank": coin["item"].get("market_cap_rank"),
                        "thumb": coin["item"].get("thumb")
                    }
                }
                for coin in data["coins"][:limit]
            ]
        
        return []
    
    async def get_global_data(self) -> Optional[Dict[str, Any]]:
        """Get global crypto market data"""
        data = await self._request("global")
        
        if data and "data" in data:
            return data["data"]
        
        return None
    
    async def get_dex_volume(self, 
                            days: int = 1) -> Optional[Dict[str, Any]]:
        """Get DEX volume data"""
        params = {
            "vs_currency": "usd",
            "days": days
        }
        
        return await self._request("exchanges/volume_chart", params)
    
    # =========================================================================
    # Starknet-Specific Methods
    # =========================================================================
    
    async def get_starknet_tokens(self) -> List[Dict[str, Any]]:
        """Get prices for common Starknet tokens"""
        starknet_ids = [
            "ethereum",       # bridged ETH
            "starknet",       # STRK
            "usd-coin",       # bridged USDC
            "tether",         # bridged USDT
            "bitcoin",        # bridged BTC
            "dai",            # bridged DAI
            "wrapped-starknet"
        ]
        
        return await self.get_price(starknet_ids)
    
    async def get_starknet_market_overview(self) -> Dict[str, Any]:
        """Get comprehensive Starknet market overview"""
        tokens = await self.get_starknet_tokens()
        global_data = await self.get_global_data()
        trending = await self.get_trending(5)
        
        return {
            "tokens": tokens,
            "global": global_data,
            "trending": trending,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_token_with_metadata(self, symbol: str) -> Optional[TokenPrice]:
        """Get token price with full metadata"""
        from .config import MONITORING
        token_id = MONITORING.TOKENS.get(symbol.lower())
        
        if not token_id:
            logger.warning(f"Unknown token symbol: {symbol}")
            return None
        
        data = await self.get_coin_data(token_id)
        
        if not data:
            return None
        
        market = data.get("market_data", {})
        
        return TokenPrice(
            id=token_id,
            symbol=data.get("symbol", "").upper(),
            name=data.get("name", ""),
            current_price=market.get("current_price", {}).get("usd", 0),
            market_cap=market.get("market_cap", {}).get("usd", 0),
            volume_24h=market.get("total_volume", {}).get("usd", 0),
            price_change_24h=market.get("price_change_24h", 0),
            price_change_percent_24h=market.get("price_change_percentage_24h", 0),
            price_change_percent_7d=market.get("price_change_percentage_7d"),
            price_change_percent_30d=market.get("price_change_percentage_30d"),
            last_updated=market.get("last_updated", datetime.utcnow().isoformat())
        )


# Create global client instance
coingecko_client = CoinGeckoClient()
