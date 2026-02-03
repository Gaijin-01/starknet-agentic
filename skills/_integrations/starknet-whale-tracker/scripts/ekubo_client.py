"""
Ekubo Protocol API Client for Starknet Whale Tracker.

Provides async methods for fetching liquidity pools, token data, and prices from Ekubo.

API Documentation: https://docs.ekubo.org
OpenAPI Spec: https://prod-api.ekubo.org/openapi.json

Security Note:
    This module uses blockchain contract addresses (0x...) which are public data.
    Static analysis may flag 40+ char hex strings as "API keys" - these are
    Starknet contract addresses, not secrets.
"""

import aiohttp
import asyncio
from typing import Optional
from dataclasses import dataclass


# Starknet Chain IDs
STARKNET_MAINNET = 1


@dataclass
class Token:
    """Represents a token on Starknet."""
    chain_id: str
    name: str
    symbol: str
    decimals: int
    address: str
    visibility_priority: int
    sort_order: int
    total_supply: Optional[int]
    logo_url: Optional[str]
    usd_price: Optional[float]
    bridge_infos: Optional[dict]


@dataclass
class Pool:
    """Represents a liquidity pool on Ekubo."""
    chain_id: str
    token0: str
    token1: str
    volume0_24h: str
    volume1_24h: str
    fees0_24h: str
    fees1_24h: str
    tvl0_total: str
    tvl1_total: str
    tvl0_delta_24h: str
    tvl1_delta_24h: str
    depth0: str
    depth1: str
    min_depth_percent: Optional[float]


class EkuboClient:
    """
    Async client for Ekubo Protocol API.
    
    Usage:
        client = EkuboClient()
        tokens = await client.get_tokens()
        pools = await client.get_overview_pairs()
    """
    
    BASE_URL = "https://prod-api.ekubo.org"
    
    def __init__(self, api_key: Optional[str] = None, timeout: float = 30.0):
        """
        Initialize the Ekubo client.
        
        Args:
            api_key: Optional API key for authenticated requests
            timeout: Request timeout in seconds (default: 30)
        """
        self.api_key = api_key
        self.timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None
    
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
    
    async def _request(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """
        Make a GET request to the Ekubo API.
        
        Args:
            endpoint: API endpoint (without base URL)
            params: Query parameters
            
        Returns:
            JSON response as dict
            
        Raises:
            aiohttp.ClientError: On network errors
            ValueError: On invalid JSON response
        """
        session = await self._get_session()
        url = f"{self.BASE_URL}{endpoint}"
        
        headers = {}
        if self.api_key:
            headers["x-api-key"] = self.api_key
        
        async with session.get(url, params=params, headers=headers) as response:
            response.raise_for_status()
            return await response.json()
    
    # ==================== Token Endpoints ====================
    
    async def get_tokens(
        self,
        chain_id: int = STARKNET_MAINNET,
        search: Optional[str] = None,
        page_size: int = 1000,
        after_token: Optional[str] = None,
        min_visibility_priority: Optional[int] = None,
    ) -> list[Token]:
        """
        Get a list of tokens for the given chain.
        
        Args:
            chain_id: Network ID (default: Starknet mainnet)
            search: Token symbol search query
            page_size: Number of tokens to return (max: 10000)
            after_token: Pagination cursor (format: chainId:tokenAddress)
            min_visibility_priority: Filter by visibility priority
            
        Returns:
            List of Token objects
        """
        params = {"chainId": chain_id}
        if search:
            params["search"] = search
        if page_size:
            params["pageSize"] = page_size
        if after_token:
            params["afterToken"] = after_token
        if min_visibility_priority is not None:
            params["minVisibilityPriority"] = min_visibility_priority
        
        data = await self._request("/tokens", params)
        
        return [
            Token(
                chain_id=item["chain_id"],
                name=item["name"],
                symbol=item["symbol"],
                decimals=item["decimals"],
                address=item["address"],
                visibility_priority=item["visibility_priority"],
                sort_order=item["sort_order"],
                total_supply=item.get("total_supply"),
                logo_url=item.get("logo_url"),
                usd_price=item.get("usd_price"),
                bridge_infos=item.get("bridgeInfos"),
            )
            for item in data
        ]
    
    async def get_token(
        self,
        chain_id: int,
        token_address: str,
    ) -> Token:
        """
        Get metadata for a specific token.
        
        Args:
            chain_id: Network ID
            token_address: Token contract address
            
        Returns:
            Token object
            
        Raises:
            ValueError: If token is not found
        """
        endpoint = f"/tokens/{chain_id}/{token_address}"
        data = await self._request(endpoint)
        
        return Token(
            chain_id=data["chain_id"],
            name=data["name"],
            symbol=data["symbol"],
            decimals=data["decimals"],
            address=data["address"],
            visibility_priority=data["visibility_priority"],
            sort_order=data["sort_order"],
            total_supply=data.get("total_supply"),
            logo_url=data.get("logo_url"),
            usd_price=data.get("usd_price"),
            bridge_infos=data.get("bridgeInfos"),
        )
    
    async def get_token_by_address(
        self,
        token_address: str,
        chain_id: int = STARKNET_MAINNET,
    ) -> Token:
        """
        Get token by address (alias for get_token).
        
        Args:
            token_address: Token contract address
            chain_id: Network ID
            
        Returns:
            Token object
        """
        return await self.get_token(chain_id, token_address)
    
    async def search_tokens(
        self,
        query: str,
        chain_id: int = STARKNET_MAINNET,
    ) -> list[Token]:
        """
        Search for tokens by symbol.
        
        Args:
            query: Search query (matches token symbol)
            chain_id: Network ID
            
        Returns:
            List of matching Token objects
        """
        return await self.get_tokens(chain_id=chain_id, search=query)
    
    # ==================== Pool/Stats Endpoints ====================
    
    async def get_overview_pairs(
        self,
        chain_id: int = STARKNET_MAINNET,
        min_tvl_usd: float = 1000.0,
    ) -> list[Pool]:
        """
        Get stats for the top trading pairs.
        
        Args:
            chain_id: Network ID
            min_tvl_usd: Minimum USD TVL required
            
        Returns:
            List of Pool objects
        """
        params = {"chainId": chain_id, "minTvlUsd": min_tvl_usd}
        data = await self._request("/overview/pairs", params)
        
        return [
            Pool(
                chain_id=item["chain_id"],
                token0=item["token0"],
                token1=item["token1"],
                volume0_24h=item["volume0_24h"],
                volume1_24h=item["volume1_24h"],
                fees0_24h=item["fees0_24h"],
                fees1_24h=item["fees1_24h"],
                tvl0_total=item["tvl0_total"],
                tvl1_total=item["tvl1_total"],
                tvl0_delta_24h=item["tvl0_delta_24h"],
                tvl1_delta_24h=item["tvl1_delta_24h"],
                depth0=item["depth0"],
                depth1=item["depth1"],
                min_depth_percent=item.get("min_depth_percent"),
            )
            for item in data.get("topPairs", [])
        ]
    
    async def get_tvl_stats(
        self,
        chain_id: int = STARKNET_MAINNET,
    ) -> dict:
        """
        Get Total Value Locked statistics.
        
        Args:
            chain_id: Network ID
            
        Returns:
            Dict with tvlByToken and tvlDeltaByTokenByDate
        """
        params = {"chainId": chain_id}
        return await self._request("/overview/tvl", params)
    
    async def get_volume_stats(
        self,
        chain_id: int = STARKNET_MAINNET,
    ) -> dict:
        """
        Get trading volume statistics.
        
        Args:
            chain_id: Network ID
            
        Returns:
            Dict with volumeByTokenByDate and volumeByToken_24h
        """
        params = {"chainId": chain_id}
        return await self._request("/overview/volume", params)
    
    async def get_revenue_stats(
        self,
        chain_id: int = STARKNET_MAINNET,
    ) -> dict:
        """
        Get protocol revenue statistics.
        
        Args:
            chain_id: Network ID
            
        Returns:
            Dict with revenueByTokenByDate and revenueByToken_24h
        """
        params = {"chainId": chain_id}
        return await self._request("/overview/revenue", params)
    
    async def get_pair_tvl(
        self,
        token_a: str,
        token_b: str,
        chain_id: int = STARKNET_MAINNET,
        tick_spacing: Optional[int] = None,
        fee: Optional[str] = None,
        extension: Optional[str] = None,
        core_address: Optional[str] = None,
    ) -> dict:
        """
        Get TVL stats for a specific trading pair.
        
        Args:
            token_a: First token address
            token_b: Second token address
            chain_id: Network ID
            tick_spacing: Pool tick spacing
            fee: Pool fee
            extension: Extension address
            core_address: Core contract address
            
        Returns:
            Dict with pair TVL data
        """
        endpoint = f"/pair/{chain_id}/{token_a}/{token_b}/tvl"
        params = {}
        if tick_spacing is not None:
            params["tickSpacing"] = tick_spacing
        if fee:
            params["fee"] = fee
        if extension:
            params["extension"] = extension
        if core_address:
            params["coreAddress"] = core_address
        
        return await self._request(endpoint, params)
    
    async def get_pair_volume(
        self,
        token_a: str,
        token_b: str,
        chain_id: int = STARKNET_MAINNET,
        tick_spacing: Optional[int] = None,
        fee: Optional[str] = None,
        extension: Optional[str] = None,
        core_address: Optional[str] = None,
    ) -> dict:
        """
        Get volume stats for a specific trading pair.
        
        Args:
            token_a: First token address
            token_b: Second token address
            chain_id: Network ID
            tick_spacing: Pool tick spacing
            fee: Pool fee
            extension: Extension address
            core_address: Core contract address
            
        Returns:
            Dict with pair volume data
        """
        endpoint = f"/pair/{chain_id}/{token_a}/{token_b}/volume"
        params = {}
        if tick_spacing is not None:
            params["tickSpacing"] = tick_spacing
        if fee:
            params["fee"] = fee
        if extension:
            params["extension"] = extension
        if core_address:
            params["coreAddress"] = core_address
        
        return await self._request(endpoint, params)
    
    # ==================== Block Endpoints ====================
    
    async def get_closest_block(
        self,
        timestamp: str,
        chain_id: int = STARKNET_MAINNET,
    ) -> dict:
        """
        Get the block closest to a given timestamp.
        
        Args:
            timestamp: ISO 8601 timestamp
            chain_id: Network ID
            
        Returns:
            Dict with block number and timestamp
        """
        endpoint = f"/blocks/{chain_id}/closest"
        params = {"timestamp": timestamp}
        return await self._request(endpoint, params)
    
    async def get_block(
        self,
        block_tag: str,
        chain_id: int = STARKNET_MAINNET,
    ) -> dict:
        """
        Get information about a specific block.
        
        Args:
            block_tag: Block number or "latest"
            chain_id: Network ID
            
        Returns:
            Dict with block number and timestamp
        """
        endpoint = f"/blocks/{chain_id}/{block_tag}"
        return await self._request(endpoint)
    
    # ==================== Price Methods ====================
    
    async def get_prices(
        self,
        tokens: list[str],
        chain_id: int = STARKNET_MAINNET,
    ) -> dict[str, float]:
        """
        Get current USD prices for tokens.
        
        Args:
            tokens: List of token addresses
            chain_id: Network ID
            
        Returns:
            Dict mapping token address to USD price
        """
        # Fetch all tokens and extract prices
        all_tokens = await self.get_tokens(chain_id=chain_id, page_size=10000)
        
        prices = {}
        for token in all_tokens:
            if token.address in tokens and token.usd_price:
                prices[token.address] = token.usd_price
        
        return prices
    
    async def get_price(
        self,
        token_address: str,
        chain_id: int = STARKNET_MAINNET,
    ) -> Optional[float]:
        """
        Get USD price for a single token.
        
        Args:
            token_address: Token contract address
            chain_id: Network ID
            
        Returns:
            USD price or None if not available
        """
        try:
            token = await self.get_token(chain_id, token_address)
            return token.usd_price
        except (aiohttp.ClientError, ValueError):
            return None
    
    # ==================== Utility Methods ====================
    
    async def get_strk_price(self) -> Optional[float]:
        """
        Get STRK USD price.
        
        Returns:
            STRK USD price or None
        """
        STRK_ADDRESS = "0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d"
        return await self.get_price(STRK_ADDRESS)
    
    async def get_eth_price(self) -> Optional[float]:
        """
        Get ETH USD price.
        
        Returns:
            ETH USD price or None
        """
        ETH_ADDRESS = "0x49d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"
        return await self.get_price(ETH_ADDRESS)
    
    async def get_liquidity_depth(
        self,
        token_a: str,
        token_b: str,
        chain_id: int = STARKNET_MAINNET,
    ) -> dict:
        """
        Get liquidity depth for a token pair.
        
        Args:
            token_a: First token address
            token_b: Second token address
            chain_id: Network ID
            
        Returns:
            Dict with depth information
        """
        pairs = await self.get_overview_pairs(chain_id=chain_id)
        
        for pool in pairs:
            if pool.token0 == token_a and pool.token1 == token_b:
                return {
                    "depth0": float(pool.depth0),
                    "depth1": float(pool.depth1),
                    "min_depth_percent": pool.min_depth_percent,
                }
        
        return {}


# ==================== Example Usage ====================

async def main():
    """Example usage of the EkuboClient."""
    async with EkuboClient() as client:
        # Get top pairs
        print("Fetching top trading pairs...")
        pairs = await client.get_overview_pairs()
        print(f"Found {len(pairs)} top pairs")
        
        # Get token prices
        print("\nFetching token prices...")
        tokens = await client.get_tokens(page_size=100)
        for token in tokens[:5]:
            print(f"{token.symbol}: ${token.usd_price or 'N/A'}")
        
        # Get specific token
        print("\nGetting STRK token info...")
        strk = await client.get_token(
            chain_id=STARKNET_MAINNET,
            token_address="0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d",
        )
        print(f"STRK: {strk.name} ({strk.symbol}) - ${strk.usd_price}")


if __name__ == "__main__":
    asyncio.run(main())
