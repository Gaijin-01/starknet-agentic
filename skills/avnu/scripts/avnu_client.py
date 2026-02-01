"""
AVNU DeFi Client for Starknet
HTTP API integration for swaps, DCA, staking, and market data

Based on avnu-labs/avnu-skill documentation
https://github.com/avnu-labs/avnu-skill

Rate Limits: 300 requests per 5 minutes (public API)
https://starknet.api.avnu.fi
"""
import asyncio
import os
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import aiohttp


# === Token Addresses ===

class Token(Enum):
    ETH = "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004d7"
    USDC = "0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8"
    USDT = "0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8"
    STRK = "0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d"


# === Data Classes ===

@dataclass
class QuoteRoute:
    """Single route in swap"""
    name: str           # DEX name
    percent: float      # % through this route
    routes: List[Dict]  # Sub-routes


@dataclass
class QuoteFee:
    """Fee breakdown"""
    avnu_fees: int
    avnu_fees_bps: int
    integrator_fees: int
    integrator_fees_bps: int


@dataclass
class Quote:
    """Swap quote from AVNU"""
    quote_id: str
    sell_token: str
    buy_token: str
    sell_amount: int      # In wei
    buy_amount: int       # In wei (before fees)
    buy_amount_usd: float
    sell_amount_usd: float
    
    # Price analysis
    price_impact_bps: int  # Basis points (20 = 0.2%)
    price_ratio_usd: float
    
    # Gas
    gas_fees: int          # In FRI
    gas_fees_usd: float
    
    # Fees
    fee: QuoteFee
    
    # Routing
    routes: List[QuoteRoute]
    exact_output: bool     # exactTokenTo
    estimated_slippage: float
    
    raw: Dict = field(default_factory=dict)


@dataclass
class DCAOrder:
    """DCA order"""
    id: str
    buy_token: str
    buy_amount: int        # Per execution (wei)
    frequency: str         # daily, weekly, monthly
    next_execution: int    # Timestamp
    status: str
    raw: Dict = field(default_factory=dict)


@dataclass
class PoolInfo:
    """Liquidity pool"""
    dex: str
    token_a: str
    token_b: str
    reserve_a: int
    reserve_b: int
    tvl: float
    apr: float


# === Errors ===

class AVNUError(Exception):
    def __init__(self, message: str, code: str = None):
        super().__init__(message)
        self.code = code


class QuoteError(AVNUError):
    pass


class ExecutionError(AVNUError):
    pass


# === Client ===

class AVNUClient:
    """
    AVNU API client for Starknet DeFi
    
    Docs: https://docs.avnu.fi
    API: https://starknet.api.avnu.fi
    Portal: https://portal.avnu.fi (for API keys)
    
    Rate Limits: 300 requests per 5 minutes (public API)
    """

    MAINNET_URL = "https://starknet.api.avnu.fi"
    SEPOLIA_URL = "https://sepolia.api.avnu.fi"
    
    # Rate limit: 300 per 5 minutes = 1 request per second
    RATE_LIMIT_REQUESTS = 300
    RATE_LIMIT_WINDOW = 300  # 5 minutes in seconds
    
    def __init__(
        self,
        rpc_url: str = "https://rpc.starknet.lava.build:443",
        api_key: str = None,
        testnet: bool = False
    ):
        self.rpc_url = rpc_url
        self.api_key = api_key or os.getenv("AVNU_API_KEY")
        self.testnet = testnet
        self.base_url = self.SEPOLIA_URL if testnet else self.MAINNET_URL
        self.session = None
        
        # Rate limiting
        self._request_times: List[float] = []

    async def connect(self):
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers=self._get_headers()
            )

    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None

    def _get_headers(self) -> Dict:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def _wait_for_rate_limit(self):
        """Ensure we don't exceed rate limits (300 req/5min)"""
        now = time.time()
        
        # Remove old requests outside the window
        self._request_times = [t for t in self._request_times if now - t < self.RATE_LIMIT_WINDOW]
        
        # If we're at the limit, wait
        if len(self._request_times) >= self.RATE_LIMIT_REQUESTS:
            oldest = min(self._request_times)
            wait_time = self.RATE_LIMIT_WINDOW - (now - oldest)
            if wait_time > 0:
                print(f"⚠️ Rate limit approaching, waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
        
        # Record this request
        self._request_times.append(time.time())

    async def _get(self, endpoint: str, params: Dict = None) -> Dict:
        if not self.session:
            await self.connect()

        await self._wait_for_rate_limit()

        url = f"{self.base_url}{endpoint}"
        async with self.session.get(url, params=params) as resp:
            if resp.status == 404:
                raise AVNUError(f"Endpoint not found: {endpoint}", "NOT_FOUND")
            if resp.status == 401:
                raise AVNUError("API key required", "UNAUTHORIZED")
            if resp.status == 429:
                raise AVNUError("Rate limited by server", "RATE_LIMIT")
            if resp.status != 200:
                raise AVNUError(f"API error: {resp.status}", "API_ERROR")
            return await resp.json()

    async def _post(self, endpoint: str, data: Dict = None) -> Dict:
        if not self.session:
            await self.connect()

        await self._wait_for_rate_limit()

        url = f"{self.base_url}{endpoint}"
        async with self.session.post(url, json=data) as resp:
            if resp.status == 401:
                raise AVNUError("API key required", "UNAUTHORIZED")
            if resp.status != 200:
                raise AVNUError(f"API error: {resp.status}", "API_ERROR")
            return await resp.json()

    # === Quotes ===

    async def get_quotes(
        self,
        sell_token: str,
        buy_token: str,
        sell_amount: float = None,
        buy_amount: float = None,
        taker_address: str = None,
        size: int = 1,
        exclude_sources: List[str] = None
    ) -> List[Quote]:
        """
        Get swap quotes from AVNU
        
        Args:
            sell_token: Token to sell (symbol or address)
            buy_token: Token to buy (symbol or address)
            sell_amount: Amount to sell in ETH units (optional)
            buy_amount: Exact output amount (alternative to sell_amount)
            taker_address: Wallet address for gas estimation
            size: Number of quotes to return (default: 1)
            exclude_sources: DEXs to exclude
            
        Returns:
            List of Quote objects sorted by best output
        """
        sell_addr = self._to_address(sell_token)
        buy_addr = self._to_address(buy_token)

        # Build params (matches TypeScript QuoteRequest)
        params = {
            "sellTokenAddress": sell_addr,
            "buyTokenAddress": buy_addr,
            "size": size,
        }

        if sell_amount:
            params["sellAmount"] = str(int(sell_amount * 10**18))
        elif buy_amount:
            params["buyAmount"] = str(int(buy_amount * 10**18))
        else:
            raise QuoteError("Either sellAmount or buyAmount required", "MISSING_AMOUNT")

        if taker_address:
            params["takerAddress"] = taker_address

        if exclude_sources:
            params["excludeSources"] = exclude_sources

        try:
            data = await self._get("/gasless/v1/quotes", params)
            
            # Handle both single quote and array response
            quotes_data = data if isinstance(data, list) else [data]
            
            return [self._parse_quote(q, sell_token, buy_token) for q in quotes_data]

        except AVNUError as e:
            # Fallback to CoinGecko prices
            return [self._get_fallback_quote(sell_token, buy_token, sell_amount or 1.0)]

    def _parse_quote(self, data: Dict, sell_token: str, buy_token: str) -> Quote:
        """Parse API response to Quote object"""
        return Quote(
            quote_id=data.get("quoteId", ""),
            sell_token=sell_token,
            buy_token=buy_token,
            sell_amount=int(data.get("sellAmount", 0)),
            buy_amount=int(data.get("buyAmount", 0)),
            buy_amount_usd=data.get("buyAmountInUsd", 0),
            sell_amount_usd=data.get("sellAmountInUsd", 0),
            price_impact_bps=data.get("priceImpact", 0),
            price_ratio_usd=data.get("priceRatioUsd", 0),
            gas_fees=int(data.get("gasFees", 0)),
            gas_fees_usd=data.get("gasFeesInUsd", 0),
            fee=QuoteFee(
                avnu_fees=int(data.get("fee", {}).get("avnuFees", 0)),
                avnu_fees_bps=data.get("fee", {}).get("avnuFeesBps", 0),
                integrator_fees=int(data.get("fee", {}).get("integratorFees", 0)),
                integrator_fees_bps=data.get("fee", {}).get("integratorFeesBps", 0)
            ),
            routes=[QuoteRoute(r.get("name", ""), r.get("percent", 0), r.get("routes", [])) 
                    for r in data.get("routes", [])],
            exact_output=data.get("exactTokenTo", False),
            estimated_slippage=data.get("estimatedSlippage", 0),
            raw=data
        )

    def _get_fallback_quote(self, sell_token: str, buy_token: str, sell_amount: float) -> Quote:
        """Create estimated quote using CoinGecko prices"""
        sell_price = self._get_coingecko_price(sell_token)
        buy_price = self._get_coingecko_price(buy_token)
        
        sell_amount_wei = int(sell_amount * 10**18)
        buy_amount_wei = int(sell_amount * sell_price / buy_price * 10**18)
        
        return Quote(
            quote_id="",
            sell_token=sell_token,
            buy_token=buy_token,
            sell_amount=sell_amount_wei,
            buy_amount=buy_amount_wei,
            buy_amount_usd=sell_amount * sell_price,
            sell_amount_usd=sell_amount * sell_price,
            price_impact_bps=0,
            price_ratio_usd=sell_price / buy_price if buy_price > 0 else 0,
            gas_fees=200000 * 10**18,  # Rough estimate
            gas_fees_usd=0.50,
            fee=QuoteFee(0, 0, 0, 0),
            routes=[],
            exact_output=False,
            estimated_slippage=0,
            raw={}
        )

    def _get_coingecko_price(self, token: str) -> float:
        """Get price from CoinGecko (sync for fallback)"""
        import aiohttp
        token_map = {"ETH": "ethereum", "STRK": "starknet", "USDC": "usd-coin", "USDT": "tether"}
        cg_id = token_map.get(token.upper(), token)
        
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={cg_id}&vs_currencies=usd"
        
        try:
            # This is blocking - should be async in production
            import urllib.request
            import json
            with urllib.request.urlopen(url, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                return data.get(cg_id, {}).get("usd", 0)
        except:
            return 2500 if token.upper() == "ETH" else 1.0

    # === Swap Execution ===

    async def execute_swap(
        self,
        quote: Quote,
        wallet_address: str,
        wallet  # starknet.py wallet
    ) -> Dict:
        """
        Execute swap based on quote
        
        Requires signed transaction via starknet.py
        """
        if not self.api_key:
            raise ExecutionError("API key required for execution", "API_KEY_REQUIRED")

        # Build transaction data
        data = {
            "quoteId": quote.quote_id,
            "takerAddress": wallet_address
        }

        result = await self._post("/execute", data)
        
        return {
            "tx_hash": result.get("transactionHash"),
            "status": result.get("status", "submitted")
        }

    # === DCA Orders ===

    async def create_dca_order(
        self,
        buy_token: str,
        buy_amount: float,
        frequency: str = "weekly",
        duration: int = 52,
        gasless: bool = False
    ) -> DCAOrder:
        """Create DCA order"""
        if not self.api_key:
            raise AVNUError("API key required for DCA", "API_KEY_REQUIRED")

        result = await self._post("/dca/orders", {
            "buyToken": self._to_address(buy_token),
            "buyAmount": str(int(buy_amount * 10**18)),
            "frequency": frequency,
            "duration": duration,
            "gasless": str(gasless).lower()
        })

        return DCAOrder(
            id=result.get("id"),
            buy_token=buy_token,
            buy_amount=int(result.get("buyAmount", 0)),
            frequency=frequency,
            next_execution=result.get("nextExecution", 0),
            status=result.get("status", "pending"),
            raw=result
        )

    async def cancel_dca_order(self, order_id: str) -> bool:
        await self._post(f"/dca/orders/{order_id}/cancel", {})
        return True

    async def get_dca_status(self, order_id: str) -> DCAOrder:
        data = await self._get(f"/dca/orders/{order_id}")
        return DCAOrder(
            id=data.get("id"),
            buy_token=data.get("buyToken"),
            buy_amount=int(data.get("buyAmount", 0)),
            frequency=data.get("frequency"),
            next_execution=data.get("nextExecution", 0),
            status=data.get("status"),
            raw=data
        )

    # === Market Data ===

    async def get_prices(self, tokens: List[str]) -> Dict[str, float]:
        """Get token prices from CoinGecko"""
        import aiohttp

        token_map = {"ETH": "ethereum", "STRK": "starknet", "USDC": "usd-coin", "USDT": "tether"}
        ids = [token_map.get(t, t) for t in tokens]

        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": ",".join(ids), "vs_currencies": "usd"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                data = await resp.json()

        prices = {}
        for token in tokens:
            cg_id = token_map.get(token, token)
            if cg_id in data:
                prices[token] = data[cg_id]["usd"]

        return prices

    async def get_tvl(self) -> float:
        try:
            data = await self._get("/tvl")
            return float(data.get("tvl", 0))
        except AVNUError:
            return 0

    # === Helpers ===

    def _to_address(self, token: str) -> str:
        if token.startswith("0x"):
            return token
        symbol_map = {
            "ETH": Token.ETH.value,
            "USDC": Token.USDC.value,
            "USDT": Token.USDT.value,
            "STRK": Token.STRK.value
        }
        return symbol_map.get(token.upper(), token)


# === Convenience Classes ===

class AVNUSwapper(AVNUClient):
    pass


class AVNUDCA(AVNUClient):
    pass


class AVNUStaking(AVNUClient):
    pass


class AVNUMarket(AVNUClient):
    pass


# === Demo ===

async def demo():
    print("🔄 AVNU Client Demo")
    print("=" * 40)

    client = AVNUClient(rpc_url="https://rpc.starknet.lava.build:443")
    
    try:
        await client.connect()
        
        # Get prices
        print("\n📊 Token Prices:")
        prices = await client.get_prices(["ETH", "STRK", "USDC"])
        for token, price in prices.items():
            print(f"  {token}: ${price}")
        
        # Get quotes
        print("\n💱 Swap Quotes (1 ETH → USDC):")
        quotes = await client.get_quotes(
            sell_token="ETH",
            buy_token="USDC",
            sell_amount=1.0,
            size=3
        )
        
        for i, q in enumerate(quotes[:3], 1):
            print(f"\n{i}. Quote ID: {q.quote_id[:16]}...")
            print(f"   Output: {q.buy_amount / 10**18:.2f} USDC")
            print(f"   Price: 1 ETH = {q.price_ratio_usd:.2f} USDC")
            print(f"   Gas: ${q.gas_fees_usd:.2f}")
            if q.routes:
                print(f"   Route: {', '.join([r.name for r in q.routes])}")
        
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(demo())
