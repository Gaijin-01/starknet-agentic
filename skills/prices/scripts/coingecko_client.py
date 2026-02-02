"""
CoinGecko API Client for Price Fetching.

Provides async methods for fetching cryptocurrency prices, market data, and OHLCV charts.

API Documentation: https://docs.coingecko.com
Free Tier: 10-50 req/min (limited endpoints)
Pro Tier: 150-1000+ req/min (all endpoints)
"""

import aiohttp
import asyncio
from typing import Optional, Literal
from dataclasses import dataclass
from datetime import datetime


# Supported timeframes for OHLCV
OHLCVTimeframe = Literal["1", "7", "14", "30", "90", "180", "365", "max"]


@dataclass
class PriceData:
    """Represents price data for a cryptocurrency."""
    id: str
    symbol: str
    name: str
    price: float
    market_cap: Optional[float]
    volume_24h: Optional[float]
    change_24h: Optional[float]
    last_updated: Optional[int]


@dataclass
class OHLCVData:
    """Represents OHLCV (candlestick) data point."""
    timestamp: int
    open: float
    high: float
    low: float
    close: float


class CoinGeckoClient:
    """
    Async client for CoinGecko API v3.
    
    Usage:
        client = CoinGeckoClient(api_key="YOUR_API_KEY")
        prices = await client.get_prices(["bitcoin", "ethereum"])
        ohlcv = await client.get_ohlcv("bitcoin", days=7)
    """
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        rate_limit_delay: float = 1.0,
    ):
        """
        Initialize the CoinGecko client.
        
        Args:
            api_key: CoinGecko Pro API key for higher rate limits
            timeout: Request timeout in seconds (default: 30)
            rate_limit_delay: Delay between requests in seconds (default: 1.0)
        """
        self.api_key = api_key
        self.timeout = timeout
        self.rate_limit_delay = rate_limit_delay
        self._session: Optional[aiohttp.ClientSession] = None
        self._last_request_time: float = 0
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session
    
    async def close(self):
        """Close the underlying aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def _rate_limit(self):
        """Enforce rate limiting between requests."""
        now = asyncio.get_event_loop().time()
        time_since_last = now - self._last_request_time
        
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        
        self._last_request_time = asyncio.get_event_loop().time()
    
    async def _request(
        self,
        endpoint: str,
        params: Optional[dict] = None,
        method: str = "GET",
    ) -> dict:
        """
        Make a request to the CoinGecko API.
        
        Args:
            endpoint: API endpoint (without base URL)
            params: Query parameters
            method: HTTP method (GET or POST)
            
        Returns:
            JSON response as dict
            
        Raises:
            aiohttp.ClientError: On network errors
            ValueError: On invalid JSON response
        """
        await self._rate_limit()
        
        session = await self._get_session()
        url = f"{self.BASE_URL}{endpoint}"
        
        headers = {}
        if self.api_key:
            headers["x-cg-pro-api-key"] = self.api_key
        
        if method == "GET":
            async with session.get(url, params=params, headers=headers) as response:
                await self._handle_response(response)
                return await response.json()
        else:
            async with session.post(url, params=params, headers=headers) as response:
                await self._handle_response(response)
                return await response.json()
    
    async def _handle_response(self, response: aiohttp.ClientResponse):
        """
        Handle API response, raising appropriate errors.
        
        Args:
            response: aiohttp response object
            
        Raises:
            ValueError: On rate limiting (429)
            aiohttp.ClientError: On other HTTP errors
        """
        if response.status == 429:
            # Rate limited - wait and retry
            await asyncio.sleep(2)
            raise ValueError("Rate limit exceeded. Please slow down.")
        
        response.raise_for_status()
    
    # ==================== Simple Price Endpoints ====================
    
    async def get_price(
        self,
        token_id: str,
        currency: str = "usd",
        include_24h_change: bool = False,
        include_market_cap: bool = False,
        include_24h_vol: bool = False,
    ) -> dict[str, float]:
        """
        Get the price of a single token.
        
        Args:
            token_id: CoinGecko token ID (e.g., "bitcoin", "starknet")
            currency: Target currency (e.g., "usd", "eur")
            include_24h_change: Include 24h price change
            include_market_cap: Include market cap
            include_24h_vol: Include 24h volume
            
        Returns:
            Dict with price data
        """
        params = {
            "ids": token_id,
            "vs_currencies": currency,
        }
        
        if include_24h_change:
            params["include_24hr_change"] = True
        if include_market_cap:
            params["include_market_cap"] = True
        if include_24h_vol:
            params["include_24hr_vol"] = True
        
        data = await self._request("/simple/price", params)
        
        # Extract just the price
        token_data = data.get(token_id, {})
        result = {currency: token_data.get(currency)}
        
        if include_24h_change:
            result[f"{currency}_24h_change"] = token_data.get(f"{currency}_24h_change")
        if include_market_cap:
            result[f"{currency}_market_cap"] = token_data.get(f"{currency}_market_cap")
        if include_24h_vol:
            result[f"{currency}_24h_vol"] = token_data.get(f"{currency}_24h_vol")
        
        return result
    
    async def get_prices(
        self,
        token_ids: list[str],
        currency: str = "usd",
        include_24h_change: bool = False,
        include_market_cap: bool = False,
        include_24h_vol: bool = False,
        precision: Optional[int] = None,
    ) -> dict[str, dict[str, float]]:
        """
        Get prices for multiple tokens.
        
        Args:
            token_ids: List of CoinGecko token IDs
            currency: Target currency (e.g., "usd", "eur")
            include_24h_change: Include 24h price change
            include_market_cap: Include market cap
            include_24h_vol: Include 24h volume
            precision: Decimal places (0-18 or "full")
            
        Returns:
            Dict mapping token ID to price data
        """
        params = {
            "ids": ",".join(token_ids),
            "vs_currencies": currency,
        }
        
        if include_24h_change:
            params["include_24hr_change"] = True
        if include_market_cap:
            params["include_market_cap"] = True
        if include_24h_vol:
            params["include_24hr_vol"] = True
        if precision is not None:
            params["precision"] = str(precision)
        
        return await self._request("/simple/price", params)
    
    async def get_token_price_by_address(
        self,
        platform_id: str,
        token_addresses: list[str],
        currency: str = "usd",
        include_24h_change: bool = False,
    ) -> dict[str, dict[str, float]]:
        """
        Get token prices by contract address.
        
        Args:
            platform_id: Asset platform ID (e.g., "ethereum", "starknet")
            token_addresses: List of token contract addresses
            currency: Target currency
            include_24h_change: Include 24h price change
            
        Returns:
            Dict mapping address to price data
        """
        params = {
            "contract_addresses": ",".join(token_addresses),
            "vs_currencies": currency,
        }
        
        if include_24h_change:
            params["include_24hr_change"] = True
        
        return await self._request(f"/simple/token_price/{platform_id}", params)
    
    async def get_supported_currencies(self) -> list[str]:
        """
        Get all supported fiat and crypto currencies.
        
        Returns:
            List of currency codes
        """
        return await self._request("/simple/supported_vs_currencies")
    
    # ==================== Market Data Endpoints ====================
    
    async def get_markets(
        self,
        currency: str = "usd",
        token_ids: Optional[list[str]] = None,
        order: str = "market_cap_desc",
        per_page: int = 100,
        page: int = 1,
        sparkline: bool = False,
        price_change_percentage: Optional[str] = None,
    ) -> list[dict]:
        """
        Get market data for multiple tokens.
        
        Args:
            currency: Target currency
            token_ids: Filter by token IDs
            order: Sort order (market_cap_desc, volume_desc, etc.)
            per_page: Results per page (1-250)
            page: Page number
            sparkline: Include sparkline data
            price_change_percentage: Include change for periods (24h,7d,14d,30d,200d,1y)
            
        Returns:
            List of market data objects
        """
        params = {
            "vs_currency": currency,
            "order": order,
            "per_page": per_page,
            "page": page,
            "sparkline": sparkline,
        }
        
        if token_ids:
            params["ids"] = ",".join(token_ids)
        if price_change_percentage:
            params["price_change_percentage"] = price_change_percentage
        
        return await self._request("/coins/markets", params)
    
    async def get_coin_data(
        self,
        token_id: str,
        localization: bool = False,
        tickers: bool = False,
        market_data: bool = True,
        community_data: bool = False,
        developer_data: bool = False,
        sparkline: bool = False,
    ) -> dict:
        """
        Get full data for a single coin.
        
        Args:
            token_id: CoinGecko token ID
            localization: Include localized descriptions
            tickers: Include ticker data
            market_data: Include market data
            community_data: Include community metrics
            developer_data: Include developer metrics
            sparkline: Include price sparkline
            
        Returns:
            Full coin data object
        """
        params = {
            "localization": localization,
            "tickers": tickers,
            "market_data": market_data,
            "community_data": community_data,
            "developer_data": developer_data,
            "sparkline": sparkline,
        }
        
        return await self._request(f"/coins/{token_id}", params)
    
    # ==================== OHLCV Endpoints ====================
    
    async def get_ohlcv(
        self,
        token_id: str,
        currency: str = "usd",
        days: OHLCVTimeframe = "7",
    ) -> list[OHLCVData]:
        """
        Get OHLCV (candlestick) chart data.
        
        Args:
            token_id: CoinGecko token ID
            currency: Target currency
            days: Timeframe (1, 7, 14, 30, 90, 180, 365, or "max")
            
        Returns:
            List of OHLCV data points: [[timestamp, open, high, low, close], ...]
        """
        params = {
            "vs_currency": currency,
            "days": days,
        }
        
        data = await self._request(f"/coins/{token_id}/ohlc", params)
        
        return [
            OHLCVData(
                timestamp=item[0],
                open=item[1],
                high=item[2],
                low=item[3],
                close=item[4],
            )
            for item in data
        ]
    
    async def get_market_chart(
        self,
        token_id: str,
        currency: str = "usd",
        days: int = 30,
    ) -> dict:
        """
        Get historical market chart data.
        
        Args:
            token_id: CoinGecko token ID
            currency: Target currency
            days: Days of data
            
        Returns:
            Dict with prices, market_caps, and total_volumes arrays
        """
        params = {
            "vs_currency": currency,
            "days": days,
        }
        
        return await self._request(f"/coins/{token_id}/market_chart", params)
    
    async def get_market_chart_range(
        self,
        token_id: str,
        currency: str = "usd",
        from_timestamp: Optional[int] = None,
        to_timestamp: Optional[int] = None,
    ) -> dict:
        """
        Get historical market chart data within a date range.
        
        Args:
            token_id: CoinGecko token ID
            currency: Target currency
            from_timestamp: UNIX timestamp (start)
            to_timestamp: UNIX timestamp (end)
            
        Returns:
            Dict with prices, market_caps, and total_volumes arrays
        """
        params = {"vs_currency": currency}
        
        if from_timestamp:
            params["from"] = from_timestamp
        if to_timestamp:
            params["to"] = to_timestamp
        
        return await self._request(f"/coins/{token_id}/market_chart/range", params)
    
    # ==================== Utility Methods ====================
    
    async def get_starknet_price(
        self,
        currency: str = "usd",
        include_24h_change: bool = True,
    ) -> dict[str, float]:
        """
        Get STRK price in USD.
        
        Args:
            currency: Target currency
            include_24h_change: Include 24h change
            
        Returns:
            Dict with price data
        """
        return await self.get_price(
            token_id="starknet",
            currency=currency,
            include_24h_change=include_24h_change,
        )
    
    async def get_bitcoin_price(
        self,
        currency: str = "usd",
        include_24h_change: bool = True,
    ) -> dict[str, float]:
        """
        Get BTC price in USD.
        
        Args:
            currency: Target currency
            include_24h_change: Include 24h change
            
        Returns:
            Dict with price data
        """
        return await self.get_price(
            token_id="bitcoin",
            currency=currency,
            include_24h_change=include_24h_change,
        )
    
    async def get_ethereum_price(
        self,
        currency: str = "usd",
        include_24h_change: bool = True,
    ) -> dict[str, float]:
        """
        Get ETH price in USD.
        
        Args:
            currency: Target currency
            include_24h_change: Include 24h change
            
        Returns:
            Dict with price data
        """
        return await self.get_price(
            token_id="ethereum",
            currency=currency,
            include_24h_change=include_24h_change,
        )
    
    async def get_top_coins(
        self,
        currency: str = "usd",
        limit: int = 10,
    ) -> list[dict]:
        """
        Get top coins by market cap.
        
        Args:
            currency: Target currency
            limit: Number of coins to return
            
        Returns:
            List of market data for top coins
        """
        return await self.get_markets(
            currency=currency,
            order="market_cap_desc",
            per_page=min(limit, 250),
        )
    
    async def get_trending_coins(self) -> dict:
        """
        Get trending coins from search.
        
        Returns:
            Dict with trending coins data
        """
        return await self._request("/search/trending")
    
    async def get_global_data(self) -> dict:
        """
        Get global cryptocurrency market data.
        
        Returns:
            Dict with global market data
        """
        return await self._request("/global")
    
    async def ping(self) -> dict:
        """
        Check API server status.
        
        Returns:
            Dict with server status
        """
        return await self._request("/ping")
    
    async def search(self, query: str) -> dict:
        """
        Search for coins, categories, and markets.
        
        Args:
            query: Search term
            
        Returns:
            Dict with search results
        """
        return await self._request("/search", {"query": query})


# ==================== Example Usage ====================

async def main():
    """Example usage of the CoinGeckoClient."""
    async with CoinGeckoClient(
        api_key=None,  # Add your API key for higher rate limits
        rate_limit_delay=1.5,  # Respect rate limits
    ) as client:
        # Check API status
        print("Pinging CoinGecko API...")
        result = await client.ping()
        print(f"Status: {result}")
        
        # Get single price
        print("\nGetting Bitcoin price...")
        btc_price = await client.get_bitcoin_price(include_24h_change=True)
        print(f"BTC: ${btc_price.get('usd', 'N/A')}")
        print(f"24h Change: {btc_price.get('usd_24h_change', 'N/A')}%")
        
        # Get multiple prices
        print("\nGetting multiple prices...")
        prices = await client.get_prices(
            token_ids=["bitcoin", "ethereum", "starknet", "solana"],
            currency="usd",
            include_24h_change=True,
        )
        for token_id, data in prices.items():
            print(f"{token_id}: ${data.get('usd', 'N/A')} ({data.get('usd_24h_change', 0):.2f}%)")
        
        # Get OHLCV data
        print("\nGetting Bitcoin OHLCV (7 days)...")
        ohlcv = await client.get_ohlcv("bitcoin", days="7")
        print(f"Data points: {len(ohlcv)}")
        if ohlcv:
            latest = ohlcv[-1]
            print(f"Latest candle: O=${latest.open:.2f}, H=${latest.high:.2f}, L=${latest.low:.2f}, C=${latest.close:.2f}")
        
        # Get market data
        print("\nGetting top 5 coins by market cap...")
        markets = await client.get_top_coins(limit=5)
        for coin in markets:
            print(f"{coin['name']} ({coin['symbol']}): ${coin['current_price']:,}")


if __name__ == "__main__":
    asyncio.run(main())
