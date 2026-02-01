"""
WebSocket Mempool Monitor for Starknet
Real-time monitoring of pending transactions
"""
import asyncio
import json
from typing import Callable, Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TxType(Enum):
    """Transaction types"""
    TRANSFER = "transfer"
    SWAP = "swap"
    CONTRACT_CALL = "contract_call"
    DEPLOY = "deploy"
    LARGE_VALUE = "large_value"


@dataclass
class PendingTx:
    """Pending transaction from mempool"""
    hash: str
    sender: str
    calldata: List[str]
    value: int
    type: TxType
    timestamp: str = ""
    block_number: int = 0
    data: Dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()


class MempoolMonitor:
    """
    Real-time mempool monitoring via RPC WebSocket
    
    Note: Starknet doesn't have public WebSocket for mempool.
    This implementation polls RPC for pending transactions.
    """

    def __init__(
        self,
        rpc_url: str = "https://rpc.starknet.lava.build:443",
        alert_callback: Callable[[PendingTx], None] = None
    ):
        self.rpc_url = rpc_url
        self.alert_callback = alert_callback
        self.running = False
        self.seen_txs: Set[str] = set()
        
        # Thresholds
        self.large_value_threshold = 1000 * 10**18  # 1000 STRK
        self.whale_addresses: Set[str] = set()
        
        # Stats
        self.stats = {
            "total_checked": 0,
            "large_transfers": 0,
            "whale_moves": 0,
            "contract_deploys": 0
        }

    def add_whale_address(self, address: str):
        """Add whale address to watch list"""
        self.whale_addresses.add(address.lower())

    def is_whale(self, address: str) -> bool:
        """Check if address is a tracked whale"""
        return address.lower() in self.whale_addresses

    def detect_tx_type(self, tx: Dict, value: int) -> TxType:
        """Detect transaction type from calldata"""
        calldata = tx.get("calldata", [])
        
        # Large value transfer
        if value >= self.large_value_threshold:
            return TxType.LARGE_VALUE
        
        # Check for common patterns
        if len(calldata) == 0:
            return TxType.TRANSFER
        
        # Transfer selector (approx)
        transfer_selector = "0x70a08231"  # balanceOf
        approve_selector = "0x095ea7b3"  # approve
        
        if calldata[0] == transfer_selector:
            return TxType.TRANSFER
        elif calldata[0] == approve_selector:
            return TxType.CONTRACT_CALL
        
        # Check for DEX interactions
        dex_selectors = ["0x7ff36ab5", "0x38ed1739"]  # Uniswap-like
        if calldata[0] in dex_selectors:
            return TxType.SWAP
        
        return TxType.CONTRACT_CALL

    def parse_value(self, calldata: List[str], has_value_field: bool = True) -> int:
        """Parse transfer value from calldata"""
        if not calldata:
            return 0
        
        try:
            # Common patterns:
            # ETH transfer: [selector, to, value]
            # ERC20: [selector, to, value]
            if len(calldata) >= 3:
                value_str = calldata[-1]
                return int(value_str, 16) if value_str.startswith("0x") else int(value_str)
            elif len(calldata) == 1:
                # Direct ETH transfer
                value_str = calldata[0]
                return int(value_str, 16) if value_str.startswith("0x") else int(value_str)
        except (ValueError, IndexError):
            pass
        
        return 0

    async def get_pending_block(self) -> Dict:
        """Get pending block from RPC"""
        import aiohttp
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "starknet_getPendingTransactions",
            "params": []
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.rpc_url, json=payload) as resp:
                result = await resp.json()
                return result.get("result", {})

    async def scan_mempool(self) -> List[PendingTx]:
        """Scan mempool for significant transactions"""
        events = []
        
        try:
            pending = await self.get_pending_block()
            txs = pending.get("transactions", [])
            
            for tx in txs:
                tx_hash = tx.get("transaction_hash", "")
                
                if tx_hash in self.seen_txs:
                    continue
                
                self.seen_txs.add(tx_hash)
                self.stats["total_checked"] += 1
                
                sender = tx.get("sender_address", "")
                calldata = tx.get("calldata", [])
                value = self.parse_value(calldata)
                tx_type = self.detect_tx_type(tx, value)
                
                pending_tx = PendingTx(
                    hash=tx_hash,
                    sender=sender,
                    calldata=calldata,
                    value=value,
                    type=tx_type,
                    data=tx
                )
                
                # Check thresholds
                is_large = value >= self.large_value_threshold
                is_whale_tx = self.is_whale(sender)
                
                if is_large or is_whale_tx:
                    if is_large:
                        self.stats["large_transfers"] += 1
                    if is_whale_tx:
                        self.stats["whale_moves"] += 1
                    
                    events.append(pending_tx)
                    
                    # Alert
                    if self.alert_callback:
                        self.alert_callback(pending_tx)

        except Exception as e:
            print(f"⚠️ Mempool scan error: {e}")
        
        return events

    async def start(self, interval: int = 5):
        """
        Start continuous monitoring
        
        Args:
            interval: Seconds between scans
        """
        self.running = True
        print(f"🔍 Mempool monitor started (interval: {interval}s)")

        while self.running:
            try:
                events = await self.scan_mempool()
                
                if events:
                    print(f"📊 Found {len(events)} significant transactions")
                    for tx in events[:5]:
                        value_str = f"{tx.value / 10**18:.2f}" if tx.value > 0 else "0"
                        print(f"  {tx.type.value}: {tx.sender[:16]}... → {value_str} STRK")

            except Exception as e:
                print(f"⚠️ Monitor error: {e}")

            await asyncio.sleep(interval)

    def stop(self):
        """Stop monitoring"""
        self.running = False
        print("🛑 Mempool monitor stopped")
        print(f"📊 Final stats: {self.stats}")

    def get_stats(self) -> Dict:
        """Get monitoring statistics"""
        return {
            **self.stats,
            "known_whales": len(self.whale_addresses),
            "seen_txs": len(self.seen_txs),
            "running": self.running
        }


async def demo():
    """Demo mempool monitoring"""
    
    def on_alert(tx: PendingTx):
        print(f"🚨 ALERT: {tx.type.value}")
        print(f"   From: {tx.sender}")
        print(f"   Value: {tx.value / 10**18:.2f} STRK")

    monitor = MempoolMonitor(
        rpc_url="https://rpc.starknet.lava.build:443",
        alert_callback=on_alert
    )
    
    # Add some whale addresses
    monitor.add_whale_address("0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004d7")
    
    # Quick scan
    print("🔍 Scanning mempool...")
    events = await monitor.scan_mempool()
    
    if events:
        print(f"Found {len(events)} events")
    else:
        print("No significant transactions")
    
    print(f"Stats: {monitor.get_stats()}")


if __name__ == "__main__":
    asyncio.run(demo())
