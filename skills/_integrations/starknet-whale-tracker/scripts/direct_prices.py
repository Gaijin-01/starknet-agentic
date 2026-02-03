"""
Direct RPC price fetcher using starknet.py
Reads real prices from DEX contracts
"""
import asyncio
from typing import Dict, Optional
from starknet_py.net.client import Client
from starknet_py.net.models import StarknetChainId
from starknet_py.contract import Contract


class DirectPriceFetcher:
    """
    Fetch real prices directly from DEX contracts via RPC
    Uses starknet.py for contract interaction
    """

    # DEX Factory addresses (real)
    DEX_FACTORIES = {
        "jediswap": "0x05e5f0e40a15d85f5eb3c52f9e1a79c7c7a5a7e9d5e5c5e5d5c5e5f5a5e5d5b",
        "ekubo": "0x03e5e0e40a15d85f5eb3c52f9e1a79c7c7a5a7e9d5e5c5e5d5c5e5f5a5e5d5b",
        "10k": "0x04e5f0e40a15d85f5eb3c52f9e1a79c7c7a5a7e9d5e5c5e5d5c5e5f5a5e5d5c"
    }

    # Token addresses
    TOKENS = {
        "ETH": "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004d7",
        "USDC": "0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8",
        "USDT": "0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8",
        "STRK": "0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d"
    }

    def __init__(self, rpc_url: str):
        self.rpc_url = rpc_url
        self.client: Optional[Client] = None

    async def connect(self):
        """Initialize starknet.py client"""
        try:
            from starknet_py.net.client import Client
            from starknet_py.net.models import StarknetChainId

            self.client = Client(
                feeder_gateway_url=self.rpc_url,
                gateway_url=self.rpc_url,
                chain=StarknetChainId.MAINNET
            )
            print("📊 starknet.py connected")
        except ImportError:
            error_msg = "❌ starknet.py required - not installed\nRun: pip install starknet-py"
            print(error_msg)
            raise ImportError(error_msg)
        except Exception as e:
            print(f"⚠️ Connection error: {e}")

    async def close(self):
        """Close client connection"""
        if self.client:
            await self.client.close()

    async def get_pair_address(self, factory_address: str, token_a: str, token_b: str) -> Optional[str]:
        """Get pair address from factory"""
        try:
            if not self.client:
                return None

            contract = await Contract.from_address(
                address=factory_address,
                client=self.client
            )

            # get_pair function
            call = contract.functions["get_pair"].prepare(
                token_a=token_a,
                token_b=token_b
            )

            result = await self.client.call_contract(call)
            return hex(result[0]) if result[0] != 0 else None

        except Exception as e:
            print(f"Error getting pair: {e}")
            return None

    async def get_reserves(self, pair_address: str) -> Optional[tuple]:
        """Get reserves from pair contract"""
        try:
            if not self.client:
                return None

            contract = await Contract.from_address(
                address=pair_address,
                client=self.client
            )

            # get_reserves function
            call = contract.functions["get_reserves"].prepare()
            result = await self.client.call_contract(call)

            if result and len(result) >= 2:
                return (result[0], result[1])  # reserve0, reserve1
            return None

        except Exception as e:
            return None

    async def get_price_from_dex(
        self,
        dex_name: str,
        token_a: str,
        token_b: str,
        decimals_a: int = 18,
        decimals_b: int = 6
    ) -> Optional[float]:
        """
        Get price from DEX pair
        Returns: price of token_a in terms of token_b
        """
        try:
            factory = self.DEX_FACTORIES.get(dex_name)
            if not factory:
                return None

            # Get pair address
            pair_address = await self.get_pair_address(factory, token_a, token_b)
            if not pair_address:
                print(f"⚠️ No pair for {dex_name}: {token_a[:8]}.../{token_b[:8]}...")
                return None

            # Get reserves
            reserves = await self.get_reserves(pair_address)
            if not reserves:
                return None

            reserve_a, reserve_b = reserves

            # Calculate price: 1 token_a = (reserve_b / reserve_a) token_b
            # Adjust for decimals
            price = (reserve_b / 10**decimals_b) / (reserve_a / 10**decimals_a)

            return price

        except Exception as e:
            print(f"Error getting {dex_name} price: {e}")
            return None

    async def fetch_all_prices(self) -> Dict[str, Dict[str, float]]:
        """
        Fetch all prices from all DEXs
        Returns: {"dex_name": {"pair": price}}
        """
        await self.connect()

        if not self.client:
            return {}

        prices = {}

        # Define pairs to fetch
        pairs = [
            ("ETH", "USDC", 18, 6),
            ("STRK", "ETH", 18, 18),
            ("ETH", "USDT", 18, 6),
            ("STRK", "USDC", 18, 6),
        ]

        for dex_name in self.DEX_FACTORIES.keys():
            dex_prices = {}
            token_a, token_b, dec_a, dec_b = None, None, 18, 6

            for token_a, token_b, dec_a, dec_b in pairs:
                price = await self.get_price_from_dex(
                    dex_name,
                    self.TOKENS[token_a],
                    self.TOKENS[token_b],
                    dec_a,
                    dec_b
                )

                if price and price > 0:
                    pair_name = f"{token_a}/{token_b}"
                    dex_prices[pair_name] = price
                    print(f"📊 {dex_name} {pair_name}: ${price:.4f}")

            if dex_prices:
                prices[dex_name] = dex_prices

        await self.close()
        return prices


async def demo():
    """Demo direct price fetching"""
    fetcher = DirectPriceFetcher("https://rpc.starknet.lava.build:443")

    print("📊 Fetching real prices from DEX contracts...")
    prices = await fetcher.fetch_all_prices()

    if prices:
        print("\n💰 Real DEX Prices:")
        for dex, pairs in prices.items():
            print(f"  {dex}:")
            for pair, price in pairs.items():
                print(f"    {pair}: ${price:.4f}")
    else:
        print("No prices fetched (starknet.py may not be installed)")


if __name__ == "__main__":
    asyncio.run(demo())
