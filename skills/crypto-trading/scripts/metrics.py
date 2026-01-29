"""
On-chain Metrics Module.

Fetches and analyzes on-chain data from various DEX APIs
including TVL, volume, fees, and liquidity metrics.
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TokenMetrics:
    """Token on-chain metrics."""
    symbol: str
    name: str
    address: str
    chain: str
    price: float
    price_change_24h: float
    market_cap: float
    volume_24h: float
    tvl: float
    tvl_change_24h: float
    fees_24h: float
    apr: float
    liquidity: float
    holders: Optional[int] = None
    transactions_24h: Optional[int] = None


@dataclass
class PoolMetrics:
    """DEX pool metrics."""
    pair_address: str
    token0_symbol: str
    token1_symbol: string = ""
    tvl: float = 0.0
    volume_24h: float = 0.0
    fees_24h: float = 0.0
    apr: float = 0.0
    token0_reserve: float = 0.0
    token1_reserve: float = 0.0


class OnChainMetrics:
    """Fetches on-chain metrics from DEX APIs."""
    
    # API endpoints
    DEXSCREENER_API = "https://api.dexscreener.com/latest/dex"
    DEXTVL_API = "https://api.llamafox.com/v1/tvl"
    ETHERSCAN_API = "https://api.etherscan.io/api"
    BSCSCAN_API = "https://api.bscscan.com/api"
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        """
        Initialize on-chain metrics fetcher.
        
        Args:
            api_keys: Dict of API keys for blockchain explorers
        """
        self.api_keys = api_keys or {
            "etherscan": os.getenv("ETHERSCAN_API_KEY", ""),
            "bscscan": os.getenv("BSCSCAN_API_KEY", ""),
        }
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Close async client."""
        await self.client.aclose()
    
    # ============ Token Metrics ============
    
    async def get_token_metrics(
        self,
        token_address: str,
        chain: str = "ethereum"
    ) -> Optional[TokenMetrics]:
        """
        Get on-chain metrics for a token.
        
        Args:
            token_address: Token contract address
            chain: Blockchain (ethereum, bsc, arbitrum, etc.)
            
        Returns:
            TokenMetrics object or None
        """
        try:
            # Try DexScreener first
            url = f"{self.DEXSCREENER_API}/tokens/{chain}/{token_address}"
            response = await self.client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                pair = data.get("pair")
                if pair:
                    return self._parse_dexscreener_pair(pair, token_address, chain)
            
            # Fallback to manual price fetch
            return await self._fetch_basic_metrics(token_address, chain)
            
        except Exception as e:
            logger.error(f"Failed to get token metrics: {e}")
            return None
    
    async def get_token_price(
        self,
        token_address: str,
        chain: str = "ethereum"
    ) -> Optional[float]:
        """
        Get current price of a token.
        
        Args:
            token_address: Token contract address
            chain: Blockchain name
            
        Returns:
            Price in USD or None
        """
        try:
            url = f"{self.DEXSCREENER_API}/tokens/{chain}/{token_address}"
            response = await self.client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                pair = data.get("pair")
                if pair:
                    return float(pair.get("priceUsd", 0))
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get price: {e}")
            return None
    
    async def search_tokens(
        self,
        query: str,
        limit: int = 10
    ) -> List[TokenMetrics]:
        """
        Search for tokens by symbol or name.
        
        Args:
            query: Search query
            limit: Max results
            
        Returns:
            List of matching tokens
        """
        try:
            url = f"{self.DEXSCREENER_API}/search"
            params = {"q": query, "limit": limit}
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                tokens = []
                for pair in data.get("pairs", [])[:limit]:
                    tokens.append(self._parse_dexscreener_pair(
                        pair,
                        pair.get("baseToken", {}).get("address", ""),
                        pair.get("chainId", "ethereum")
                    ))
                return tokens
            
            return []
            
        except Exception as e:
            logger.error(f"Token search failed: {e}")
            return []
    
    # ============ Pool Metrics ============
    
    async def get_pool_metrics(
        self,
        pool_address: str,
        chain: str = "ethereum"
    ) -> Optional[PoolMetrics]:
        """
        Get metrics for a specific pool.
        
        Args:
            pool_address: Pool/ pair address
            chain: Blockchain
            
        Returns:
            PoolMetrics object or None
        """
        try:
            url = f"{self.DEXSCREENER_API}/pairs/{chain}/{pool_address}"
            response = await self.client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                pair = data.get("pair")
                if pair:
                    return self._parse_pool_metrics(pair)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get pool metrics: {e}")
            return None
    
    async def get_top_pools(
        self,
        chain: str = "ethereum",
        limit: int = 20,
        sort_by: str = "tvl"
    ) -> List[PoolMetrics]:
        """
        Get top pools by TVL or volume.
        
        Args:
            chain: Blockchain name
            limit: Max results
            sort_by: "tvl", "volume", or "apr"
            
        Returns:
            List of PoolMetrics
        """
        try:
            url = f"{self.DEXSCREENER_API}/pairs/{chain}"
            params = {"limit": limit}
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                pools = []
                for pair in data.get("pairs", [])[:limit]:
                    pools.append(self._parse_pool_metrics(pair))
                return pools
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get top pools: {e}")
            return []
    
    # ============ Trending/New Pools ============
    
    async def get_trending_pools(
        self,
        chain: Optional[str] = None,
        limit: int = 10
    ) -> List[PoolMetrics]:
        """
        Get trending/pumping pools.
        
        Args:
            chain: Optional chain filter
            limit: Max results
            
        Returns:
            List of trending pools
        """
        try:
            url = f"{self.DEXSCREENER_API}/pairs"
            params = {"limit": limit}
            
            if chain:
                params["chainId"] = chain
            
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                pools = []
                
                for pair in data.get("pairs", [])[:limit]:
                    # Filter for trending (high price change)
                    if float(pair.get("priceChange", {}).get("h24", 0)) > 20:
                        pools.append(self._parse_pool_metrics(pair))
                
                return pools[:limit]
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get trending pools: {e}")
            return []
    
    async def get_new_pools(
        self,
        chain: str = "ethereum",
        limit: int = 10
    ) -> List[PoolMetrics]:
        """
        Get newly created pools.
        
        Args:
            chain: Blockchain name
            limit: Max results
            
        Returns:
            List of new pools
        """
        try:
            url = f"{self.DEXSCREENER_API}/pairs/{chain}/new"
            params = {"limit": limit}
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                pools = []
                for pair in data.get("pairs", [])[:limit]:
                    pools.append(self._parse_pool_metrics(pair))
                return pools
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get new pools: {e}")
            return []
    
    # ============ Market Overview ============
    
    async def get_market_overview(
        self,
        chains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get crypto market overview.
        
        Args:
            chains: List of chains to include
            
        Returns:
            Market overview dict
        """
        chains = chains or ["ethereum", "bsc", "arbitrum", "base"]
        
        overview = {
            "timestamp": datetime.now().isoformat(),
            "chains": {},
            "total_tvl": 0,
            "total_volume_24h": 0
        }
        
        tasks = [self._get_chain_stats(chain) for chain in chains]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for chain, stats in zip(chains, results):
            if isinstance(stats, dict):
                overview["chains"][chain] = stats
                overview["total_tvl"] += stats.get("tvl", 0)
                overview["total_volume_24h"] += stats.get("volume_24h", 0)
        
        return overview
    
    async def _get_chain_stats(self, chain: str) -> Dict[str, Any]:
        """Get stats for a specific chain."""
        try:
            pools = await self.get_top_pools(chain, limit=50)
            
            tvl = sum(p.tvl for p in pools)
            volume = sum(p.volume_24h for p in pools)
            fees = sum(p.fees_24h for p in pools)
            
            return {
                "chain": chain,
                "pool_count": len(pools),
                "tvl": tvl,
                "volume_24h": volume,
                "fees_24h": fees,
                "top_pools": [p.__dict__ for p in pools[:5]]
            }
            
        except Exception as e:
            logger.error(f"Chain stats failed for {chain}: {e}")
            return {"chain": chain, "error": str(e)}
    
    # ============ Helper Methods ============
    
    def _parse_dexscreener_pair(
        self,
        pair: Dict,
        address: str,
        chain: str
    ) -> TokenMetrics:
        """Parse DexScreener pair data to TokenMetrics."""
        base_token = pair.get("baseToken", {})
        price_change = pair.get("priceChange", {})
        liquidity = pair.get("liquidity", {})
        
        return TokenMetrics(
            symbol=base_token.get("symbol", "?"),
            name=base_token.get("name", ""),
            address=address,
            chain=chain,
            price=float(pair.get("priceUsd", 0)),
            price_change_24h=float(price_change.get("h24", 0)),
            market_cap=float(pair.get("marketCap", 0)),
            volume_24h=float(pair.get("volume", {}).get("h24", 0)),
            tvl=float(liquidity.get("usd", 0)),
            tvl_change_24h=float(liquidity.get("change", 0)),
            fees_24h=float(pair.get("fdv", 0)),
            apr=float(price_change.get("h24", 0)),  # Approximation
            liquidity=float(liquidity.get("usd", 0)),
            holders=None,
            transactions_24h=None
        )
    
    def _parse_pool_metrics(self, pair: Dict) -> PoolMetrics:
        """Parse DexScreener pair to PoolMetrics."""
        base_token = pair.get("baseToken", {})
        quote_token = pair.get("quoteToken", {})
        liquidity = pair.get("liquidity", {})
        price_change = pair.get("priceChange", {})
        
        return PoolMetrics(
            pair_address=pair.get("pairAddress", ""),
            token0_symbol=base_token.get("symbol", "?"),
            token1_symbol=quote_token.get("symbol", "?"),
            tvl=float(liquidity.get("usd", 0)),
            volume_24h=float(pair.get("volume", {}).get("h24", 0)),
            fees_24h=float(pair.get("fdv", 0)),
            apr=float(price_change.get("h24", 0)),
            token0_reserve=0,  # Not in DexScreener basic
            token1_reserve=0
        )
    
    async def _fetch_basic_metrics(
        self,
        address: str,
        chain: str
    ) -> TokenMetrics:
        """Fetch basic metrics as fallback."""
        return TokenMetrics(
            symbol="?",
            name="",
            address=address,
            chain=chain,
            price=0,
            price_change_24h=0,
            market_cap=0,
            volume_24h=0,
            tvl=0,
            tvl_change_24h=0,
            fees_24h=0,
            apr=0,
            liquidity=0
        )


# Synchronous wrapper
class SyncOnChainMetrics:
    """Synchronous wrapper for OnChainMetrics."""
    
    def __init__(self):
        self._async = OnChainMetrics()
    
    def get_token_metrics(self, address: str, chain: str = "ethereum"):
        """Get token metrics synchronously."""
        return asyncio.run(self._async.get_token_metrics(address, chain))
    
    def get_token_price(self, address: str, chain: str = "ethereum"):
        """Get token price synchronously."""
        return asyncio.run(self._async.get_token_price(address, chain))
    
    def search_tokens(self, query: str, limit: int = 10):
        """Search tokens synchronously."""
        return asyncio.run(self._async.search_tokens(query, limit))
    
    def get_top_pools(self, chain: str = "ethereum", limit: int = 20):
        """Get top pools synchronously."""
        return asyncio.run(self._async.get_top_pools(chain, limit))
    
    def get_market_overview(self, chains: Optional[List[str]] = None):
        """Get market overview synchronously."""
        return asyncio.run(self._async.get_market_overview(chains))
    
    def close(self):
        """Close async resources."""
        asyncio.run(self._async.close())
