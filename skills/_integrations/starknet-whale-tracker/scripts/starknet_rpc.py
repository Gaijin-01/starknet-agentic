"""
Starknet RPC and Indexing Layer
"""
import asyncio
import json
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from aiohttp import ClientSession, ClientError


@dataclass
class TransactionInfo:
    hash: str
    from_address: str
    to_address: str
    value: int
    calldata: List[str]
    block_number: int
    timestamp: int


@dataclass
class BalanceInfo:
    address: str
    token_address: str
    balance: int
    block_number: int


class StarknetRPC:
    """RPC client for Starknet blockchain"""

    def __init__(self, rpc_url: str, indexer_url: str = "https://api.starknet.io/v1"):
        self.rpc_url = rpc_url
        self.indexer_url = indexer_url
        self.session: Optional[ClientSession] = None

    async def connect(self):
        """Initialize HTTP session"""
        if not self.session:
            self.session = ClientSession()

    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None

    async def _call(self, method: str, params: List[Any] = None) -> Dict:
        """Make RPC call"""
        if not self.session:
            await self.connect()

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or []
        }

        async with self.session.post(self.rpc_url, json=payload) as response:
            result = await response.json()
            if "error" in result:
                raise Exception(f"RPC Error: {result['error']}")
            return result.get("result")

    async def get_block_number(self) -> int:
        """Get current block number"""
        result = await self._call("starknet_blockNumber")
        return result

    async def get_block_with_txs(self, block_number: int) -> Dict:
        """Get block with transactions"""
        return await self._call("starknet_getBlockWithTxs", [block_number])

    async def get_transaction(self, tx_hash: str) -> Dict:
        """Get transaction by hash"""
        return await self._call("starknet_getTransactionByHash", [tx_hash])

    async def get_transaction_receipt(self, tx_hash: str) -> Dict:
        """Get transaction receipt"""
        return await self._call("starknet_getTransactionReceipt", [tx_hash])

    async def call(self, contract_address: str, entry_point: str, calldata: List[str] = None) -> Dict:
        """Call contract view function"""
        return await self._call("starknet_call", [
            {
                "contract_address": contract_address,
                "entry_point_selector": entry_point,
                "calldata": calldata or []
            },
            "latest"
        ])

    async def get_storage_at(self, contract_address: str, key: str, block_number: int = None) -> str:
        """Get storage value at key"""
        block_id = block_number or "latest"
        return await self._call("starknet_getStorageAt", [
            contract_address,
            key,
            block_id
        ])

    async def get_nonce(self, address: str) -> str:
        """Get account nonce"""
        return await self._call("starknet_getNonce", [address])

    async def estimate_fee(self, calls: List[Dict], sender_address: str) -> Dict:
        """Estimate transaction fee"""
        return await self._call("starknet_estimateFee", [
            [
                {
                    "type": "INVOKE",
                    "sender_address": sender_address,
                    "calldata": calls
                }
            ]
        ])


class StarknetIndexer:
    """Indexer API client for historical data"""

    def __init__(self, base_url: str = "https://api.starknet.io/v1"):
        self.base_url = base_url
        self.session: Optional[ClientSession] = None

    async def connect(self):
        if not self.session:
            self.session = ClientSession()

    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def _get(self, endpoint: str) -> Dict:
        if not self.session:
            await self.connect()

        async with self.session.get(f"{self.base_url}{endpoint}") as response:
            return await response.json()

    async def get_addresses(self, limit: int = 100) -> List[Dict]:
        """Get recent addresses"""
        return await self._get(f"/addresses?limit={limit}")

    async def get_transactions(self, address: str, limit: int = 100) -> List[Dict]:
        """Get transactions for address"""
        return await self._get(f"/addresses/{address}/transactions?limit={limit}")

    async def get_events(self, address: str, limit: int = 100) -> List[Dict]:
        """Get events for address"""
        return await self._get(f"/addresses/{address}/events?limit={limit}")


class TokenClient:
    """ERC-20 Token utilities"""

    # Common token addresses on Starknet
    ETH_TOKEN = "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004d7"
    STRK_TOKEN = "0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d"
    USDC_TOKEN = "0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8"

    @staticmethod
    def parse_hex_value(hex_str: str) -> int:
        """Parse hex string to integer"""
        return int(hex_str, 16) if hex_str else 0

    @staticmethod
    def format_wei(value: int, decimals: int = 18) -> float:
        """Format wei to readable value"""
        return value / (10 ** decimals)

    async def get_balance(self, rpc: StarknetRPC, token_address: str, wallet_address: str) -> BalanceInfo:
        """Get ERC-20 balance for wallet"""
        # ERC-20 balanceOf selector
        selector = "0x70a08231000000000000000000000000"  # balanceOf(address)

        result = await rpc.call(
            contract_address=token_address,
            entry_point=selector,
            calldata=[wallet_address]
        )

        balance = self.parse_hex_value(result.get("result", ["0"])[0])
        block = await rpc.get_block_number()

        return BalanceInfo(
            address=wallet_address,
            token_address=token_address,
            balance=balance,
            block_number=block
        )

    async def get_eth_balance(self, rpc: StarknetRPC, wallet_address: str) -> BalanceInfo:
        """Get ETH balance"""
        # Use starknet_call with empty calldata for ETH balance
        result = await rpc.call(
            contract_address=self.ETH_TOKEN,
            entry_point="0x70a08231000000000000000000000000",
            calldata=[wallet_address]
        )

        balance = self.parse_hex_value(result.get("result", ["0"])[0])
        block = await rpc.get_block_number()

        return BalanceInfo(
            address=wallet_address,
            token_address=self.ETH_TOKEN,
            balance=balance,
            block_number=block
        )


async def main():
    """Test RPC connection"""
    rpc = StarknetRPC("https://starknet-mainnet.g.alchemy.com/v2/demo")

    try:
        block = await rpc.get_block_number()
        print(f"Current block: {block}")

        nonce = await rpc.get_nonce(
            "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004d7"
        )
        print(f"ETH holder nonce: {nonce}")
    finally:
        await rpc.close()


if __name__ == "__main__":
    asyncio.run(main())
