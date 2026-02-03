"""
Mempool Monitor - Track pending transactions on Starknet
"""
import asyncio
import json
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from starknet_rpc import StarknetRPC


class EventType(Enum):
    """Types of mempool events"""
    LARGE_TRANSFER = "large_transfer"
    CONTRACT_DEPLOYMENT = "contract_deployment"
    DEX_TRADE = "dex_trade"
    FLASH_LOAN = "flash_loan"
    NEW_POSITION = "new_position"
    ALERT = "alert"


@dataclass
class MempoolEvent:
    """Event from mempool monitoring"""
    type: EventType
    tx_hash: str
    from_address: str
    to_address: str
    value: int
    data: Dict = field(default_factory=dict)
    timestamp: str = ""
    block_number: int = 0
    detected_at: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()
        if not self.detected_at:
            self.detected_at = datetime.utcnow().isoformat()


class MempoolMonitor:
    """
    Monitor Starknet mempool for significant transactions

    Features:
    - Track pending transactions
    - Detect large transfers
    - Identify DEX trades
    - Alert on suspicious activity
    """

    # Known DEX contract addresses (sample)
    DEX_CONTRACTS = {
        "jediswap": "0x05e5f0e40a15d85f5eb3c52f9e1a79c7c7a5a7e9d5e5c5e5d5c5e5f5a5e5d5c",
        "ekubo": "0x03e5e0e40a15d85f5eb3c52f9e1a79c7c7a5a7e9d5e5c5e5d5c5e5f5a5e5d5c",
        "10k": "0x04e5f0e40a15d85f5eb3c52f9e1a79c7c7a5a7e9d5e5c5e5d5c5e5f5a5e5d5c",
    }

    def __init__(
        self,
        rpc: StarknetRPC,
        min_value_strk: int = 100,
        alert_threshold_strk: int = 1000,
        alert_callback: Callable[[MempoolEvent], None] = None,
        known_whales: List[str] = None
    ):
        self.rpc = rpc
        self.min_value = min_value_strk
        self.alert_threshold = alert_threshold_strk
        self.alert_callback = alert_callback
        self.known_whales = set(wh or [] for wh in (known_whales or []))
        self.running = False
        self.seen_txs = set()
        self.last_block = 0

        # Statistics
        self.stats = {
            "total_checked": 0,
            "large_transfers": 0,
            "dex_trades": 0,
            "whale_moves": 0,
            "alerts_sent": 0
        }

    def is_whale(self, address: str) -> bool:
        """Check if address is a known whale"""
        return address.lower() in [w.lower() for w in self.known_whales]

    def is_dex(self, address: str) -> bool:
        """Check if address is a known DEX"""
        return address.lower() in [
            d.lower() for d in self.DEX_CONTRACTS.values()
        ]

    def parse_value(self, calldata: List[str]) -> int:
        """Parse transfer value from calldata"""
        if not calldata:
            return 0

        # Common transfer patterns
        # ERC20 transfer/recipient/amount or direct ETH transfer
        try:
            if len(calldata) >= 3:
                # ERC-20 style: selector, recipient, amount
                amount_hex = calldata[-1]
                return int(amount_hex, 16) if amount_hex.startswith("0x") else int(amount_hex)
            elif len(calldata) == 1:
                # Direct ETH transfer
                amount_hex = calldata[0]
                return int(amount_hex, 16) if amount_hex.startswith("0x") else int(amount_hex)
        except (ValueError, IndexError):
            pass

        return 0

    def format_value(self, value: int, decimals: int = 18) -> float:
        """Format raw value to human readable"""
        return value / (10 ** decimals)

    async def get_pending_txs(self) -> List[Dict]:
        """Get pending transactions from mempool"""
        # Note: Starknet doesn't have a direct mempool API like Ethereum
        # We simulate by tracking recent blocks and detecting patterns

        try:
            current_block = await self.rpc.get_block_number()

            if current_block > self.last_block:
                # New block, check for transactions
                block_data = await self.rpc.get_block_with_txs(current_block)
                txs = block_data.get("transactions", [])
                self.last_block = current_block
                return txs

        except Exception as e:
            print(f"Error getting pending txs: {e}")

        return []

    def analyze_transaction(self, tx: Dict) -> Optional[MempoolEvent]:
        """Analyze a transaction and return event if significant"""

        tx_hash = tx.get("transaction_hash", "")
        if tx_hash in self.seen_txs:
            return None

        self.seen_txs.add(tx_hash)
        self.stats["total_checked"] += 1

        # Parse transaction
        sender = tx.get("sender_address", "")
        calldata = tx.get("calldata", [])
        value = self.parse_value(calldata)

        # Determine transaction type
        if self.is_whale(sender):
            self.stats["whale_moves"] += 1
            return MempoolEvent(
                type=EventType.ALERT,
                tx_hash=tx_hash,
                from_address=sender,
                to_address=tx.get("contract_address", ""),
                value=value,
                data={
                    "is_whale": True,
                    "whale_type": "known"
                }
            )

        if value >= self.min_value * 10**18:
            self.stats["large_transfers"] += 1

            event_type = EventType.LARGE_TRANSFER
            if self.is_dex(sender):
                event_type = EventType.DEX_TRADE
                self.stats["dex_trades"] += 1

            return MempoolEvent(
                type=event_type,
                tx_hash=tx_hash,
                from_address=sender,
                to_address=tx.get("contract_address", ""),
                value=value,
                data={
                    "value_formatted": self.format_value(value),
                    "is_whale": self.is_whale(sender),
                    "is_dex": self.is_dex(sender)
                }
            )

        return None

    async def scan_block(self) -> List[MempoolEvent]:
        """Scan current block for significant transactions"""
        events = []
        txs = await self.get_pending_txs()

        for tx in txs:
            event = self.analyze_transaction(tx)
            if event:
                events.append(event)

                # Send alert if threshold met
                if event.value >= self.alert_threshold * 10**18:
                    self.stats["alerts_sent"] += 1
                    if self.alert_callback:
                        self.alert_callback(event)

        return events

    async def start(self, interval: int = 15):
        """
        Start monitoring loop

        Args:
            interval: Seconds between scans
        """
        self.running = True
        print(f"🔍 Mempool monitor started (interval: {interval}s)")

        while self.running:
            try:
                events = await self.scan_block()

                if events:
                    print(f"📊 Found {len(events)} significant transactions")
                    for event in events[:5]:  # Log first 5
                        print(f"  {event.type.value}: {event.from_address[:16]}... → {event.value / 1e18:.2f} STRK")

            except Exception as e:
                print(f"⚠️ Scan error: {e}")

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
            "known_whales": len(self.known_whales),
            "running": self.running,
            "seen_txs": len(self.seen_txs)
        }


class PendingFilter:
    """
    Filter pending transactions based on criteria
    """

    def __init__(
        self,
        min_value: int = 0,
        from_whitelist: List[str] = None,
        to_blacklist: List[str] = None,
        include_dex: bool = True
    ):
        self.min_value = min_value
        self.from_whitelist = set(from_wh or [] for wh in (from_whitelist or []))
        self.to_blacklist = set(to_bl or [] for bl in (to_blacklist or []))
        self.include_dex = include_dex

    def matches(self, tx: Dict) -> bool:
        """Check if transaction matches filter criteria"""

        # Check sender whitelist
        if self.from_whitelist:
            if tx.get("sender_address") not in self.from_whitelist:
                return False

        # Check recipient blacklist
        to = tx.get("contract_address", "")
        if to in self.to_blacklist:
            return False

        # Check DEX
        if not self.include_dex:
            if self._is_dex(to):
                return False

        return True

    def _is_dex(self, address: str) -> bool:
        """Check if address is a DEX"""
        # Simplified check - in production use full list
        dex_patterns = ["jediswap", "ekubo", "10k", "amm", "swap"]
        return any(p in address.lower() for p in dex_patterns)


async def demo():
    """Demonstrate mempool monitoring"""

    rpc = StarknetRPC("https://starknet-mainnet.g.alchemy.com/v2/demo")

    # Demo callback
    def on_alert(event: MempoolEvent):
        print(f"🚨 ALERT: {event.type.value}")
        print(f"   From: {event.from_address}")
        print(f"   Value: {event.value / 1e18:.2f} STRK")

    monitor = MempoolMonitor(
        rpc=rpc,
        min_value_strk=100,
        alert_threshold_strk=1000,
        alert_callback=on_alert,
        known_whales=[
            "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004d7"
        ]
    )

    # Quick scan
    print("🔍 Scanning current block...")
    events = await monitor.scan_block()

    if events:
        print(f"\n📊 Found {len(events)} events:")
        for event in events:
            print(f"  {event.type.value}: {event.value / 1e18:.2f} STRK")
    else:
        print("No significant transactions found")

    print(f"\n📈 Stats: {monitor.get_stats()}")

    await rpc.close()


if __name__ == "__main__":
    asyncio.run(demo())
