"""
Starknet Whale Tracker - Main Module
Combines RPC, whale database, mempool, and arbitrage detection
"""
import asyncio
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

from config import Config, DEFAULT_CONFIG
from starknet_rpc import StarknetRPC
from whale_db import WhaleDatabase, WhaleWallet, WhaleActivity
from mempool_monitor import MempoolMonitor, MempoolEvent, EventType
from arbitrage import ArbitrageScanner, ArbitrageOpportunity


@dataclass
class TrackerConfig:
    """Configuration for the tracker"""
    db_path: str = "./data/whales.db"
    rpc_url: str = ""
    min_whale_balance: int = 10000  # STRK
    alert_min_value: int = 1000  # STRK
    scan_interval: int = 15  # seconds
    telegram_token: str = ""
    telegram_chat_id: str = ""


class StarknetWhaleTracker:
    """
    Main whale tracking system

    Combines:
    - Whale database management
    - Mempool monitoring
    - Arbitrage detection
    - Alert system
    """

    def __init__(self, config: TrackerConfig = None):
        self.config = config or TrackerConfig()
        self.rpc = StarknetRPC(self.config.rpc_url)
        self.db = WhaleDatabase(self.config.db_path)
        self.mempool: Optional[MempoolMonitor] = None
        self.arbitrage = ArbitrageScanner()
        self.running = False
        self.alert_callbacks: List[Callable] = []

    async def connect(self):
        """Initialize connections"""
        await self.rpc.connect()

    async def close(self):
        """Close connections"""
        if self.running:
            self.stop()
        await self.rpc.close()

    # === Whale Management ===

    def add_whale(
        self,
        address: str,
        tags: List[str] = None,
        notes: str = "",
        alert_on: List[str] = None
    ) -> bool:
        """Add a whale to tracking"""
        whale = WhaleWallet(
            address=address,
            tags=tags or ["whale"],
            notes=notes,
            alert_on=alert_on or ["large_transfer", "new_position"]
        )
        return self.db.add_whale(whale)

    def get_whales(self, tag: str = None) -> List[WhaleWallet]:
        """Get tracked whales"""
        if tag:
            return self.db.get_by_tag(tag)
        return self.db.get_all_whales()

    def remove_whale(self, address: str) -> bool:
        """Remove whale from tracking"""
        return self.db.delete_whale(address)

    # === Activity Tracking ===

    async def track_wallet(
        self,
        address: str,
        tags: List[str] = None,
        alert_on: List[str] = None
    ):
        """Start tracking a wallet"""
        self.add_whale(address, tags, alert_on=alert_on)

        # Add to mempool monitor if running
        if self.mempool:
            self.mempool.known_whales.add(address)

    async def log_activity(
        self,
        wallet_address: str,
        event_type: str,
        details: Dict,
        block_number: int,
        tx_hash: str = ""
    ):
        """Log whale activity"""
        activity = WhaleActivity(
            id=0,
            wallet_address=wallet_address,
            event_type=event_type,
            details=details,
            block_number=block_number,
            timestamp=datetime.utcnow().isoformat(),
            tx_hash=tx_hash
        )

        self.db.add_activity(activity)

        # Trigger alerts
        whale = self.db.get_whale(wallet_address)
        if whale and event_type in whale.alert_on:
            await self._send_alert(activity, whale)

    # === Monitoring ===

    async def start(self, mode: str = "all"):
        """
        Start monitoring

        Args:
            mode: "mempool", "arbitrage", "all"
        """
        self.running = True
        await self.connect()

        print(f"🚀 Starting tracker (mode: {mode})")

        tasks = []

        if mode in ["all", "mempool"]:
            whales = [w.address for w in self.get_whales()]

            self.mempool = MempoolMonitor(
                rpc=self.rpc,
                min_value_strk=self.config.alert_min_value,
                alert_threshold_strk=self.config.alert_min_value * 5,
                alert_callback=self._handle_mempool_event,
                known_whales=whales
            )
            tasks.append(asyncio.create_task(self.mempool.start(self.config.scan_interval)))

        if mode in ["all", "arbitrage"]:
            tasks.append(asyncio.create_task(self._monitor_arbitrage()))

        # Wait for all tasks
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _monitor_arbitrage(self):
        """Monitor arbitrage opportunities"""
        print("📊 Arbitrage monitor started")

        async for opp in self.arbitrage.stream_opportunities(interval=30):
            if opp.profit_percent > self.arbitrage.min_profit:
                await self._send_arbitrage_alert(opp)

    async def stop(self):
        """Stop all monitoring"""
        self.running = False

        if self.mempool:
            self.mempool.stop()

        print("🛑 Tracker stopped")

    # === Alerts ===

    def on_alert(self, callback: Callable):
        """Register alert callback"""
        self.alert_callbacks.append(callback)

    async def _handle_mempool_event(self, event: MempoolEvent):
        """Handle mempool event"""
        await self.log_activity(
            wallet_address=event.from_address,
            event_type=event.type.value,
            details=event.data,
            block_number=event.block_number,
            tx_hash=event.tx_hash
        )

    async def _send_alert(self, activity: WhaleActivity, whale: WhaleWallet):
        """Send alert for whale activity with Voyager link"""
        tx_link = f"https://voyager.online/tx/{activity.tx_hash}" if activity.tx_hash else ""
        message = f"🐋 Whale Alert\n"
        message += f"{whale.notes or whale.address[:16]}...\n"
        message += f"{activity.event_type}\n"
        message += f"{activity.details}\n"
        if tx_link:
            message += f"🔗 {tx_link}"

        for callback in self.alert_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(message, activity)
                else:
                    callback(message, activity)
            except Exception as e:
                print(f"Alert callback error: {e}")

        # Telegram (if configured)
        if self.config.telegram_token and self.config.telegram_chat_id:
            await self._send_telegram(message)

    async def _send_arbitrage_alert(self, opp: ArbitrageOpportunity):
        """Send arbitrage opportunity alert"""
        message = (
            f"💰 Arbitrage Alert\n"
            f"{opp.dex_from} → {opp.dex_to}\n"
            f"Profit: ${opp.estimated_profit:.2f} ({opp.profit_percent:.2f}%)\n"
            f"Path: {' → '.join(opp.token_path)}\n"
            f"Confidence: {opp.confidence * 100:.0f}%\n"
            f"Volume: ${opp.volume_optimal:.0f}"
        )

        for callback in self.alert_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(message, opp)
                else:
                    callback(message, opp)
            except Exception as e:
                print(f"Arbitrage alert error: {e}")

    async def _send_telegram(self, message: str):
        """Send Telegram message via Bot API"""
        import os
        from aiohttp import ClientSession

        token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

        if not token or not chat_id:
            return

        url = f"https://api.telegram.org/bot{token}/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }

        try:
            async with ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status != 200:
                        error = await response.text()
                        print(f"❌ Telegram error: {error}")
        except Exception as e:
            print(f"❌ Telegram send failed: {e}")

    # === Queries ===

    async def get_activity(
        self,
        address: str = None,
        hours: int = 24
    ) -> List[WhaleActivity]:
        """Get recent activity"""
        return self.db.get_recent_activity(hours=hours)

    async def get_arbitrage_opportunities(self) -> List[ArbitrageOpportunity]:
        """Get current arbitrage opportunities"""
        return await self.arbitrage.scan()

    async def get_portfolio(self, address: str) -> Dict:
        """Get whale portfolio"""
        history = self.db.get_portfolio_history(address)
        return {
            "address": address,
            "snapshots": history,
            "current_value": history[0]["balance"] if history else 0
        }

    def get_stats(self) -> Dict:
        """Get tracker statistics"""
        db_stats = self.db.get_whale_stats()

        return {
            "whales": db_stats["total_whales"],
            "activity_today": db_stats["activity_today"],
            "mempool_stats": self.mempool.get_stats() if self.mempool else {},
            "arbitrage_stats": self.arbitrage.get_stats(),
            "running": self.running
        }

    # === Stream Events ===

    async def stream(self):
        """Stream whale events"""
        while self.running:
            activity = self.db.get_recent_activity(hours=1, limit=1)
            if activity:
                yield activity[0]
            await asyncio.sleep(5)


# === Factory Functions ===

def create_tracker(
    rpc_url: str,
    db_path: str = "./data/whales.db",
    telegram_token: str = "",
    telegram_chat_id: str = ""
) -> StarknetWhaleTracker:
    """Create and configure tracker"""
    config = TrackerConfig(
        rpc_url=rpc_url,
        db_path=db_path,
        telegram_token=telegram_token,
        telegram_chat_id=telegram_chat_id
    )
    return StarknetWhaleTracker(config)


async def demo():
    """Demonstrate tracker functionality"""

    print("🐋 Starknet Whale Tracker Demo")
    print("=" * 40)

    tracker = create_tracker(
        rpc_url="https://starknet-mainnet.g.alchemy.com/v2/demo",
        db_path="./data/demo.db"
    )

    try:
        await tracker.connect()

        # Add a test whale
        print("\n📝 Adding test whale...")
        tracker.add_whale(
            address="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            tags=["test", "deployer"],
            notes="Demo whale"
        )

        # Get all whales
        print("\n🐋 Tracked whales:")
        for whale in tracker.get_whales():
            print(f"  {whale.address[:20]}... [{', '.join(whale.tags)}]")

        # Get stats
        print("\n📊 Tracker stats:")
        print(tracker.get_stats())

        # Quick activity check
        print("\n📜 Recent activity:")
        activities = await tracker.get_activity(hours=24)
        print(f"  {len(activities)} activities found")

        # Arbitrage scan
        print("\n💰 Scanning arbitrage...")
        opps = await tracker.get_arbitrage_opportunities()
        print(f"  {len(opps)} opportunities found")

    finally:
        await tracker.close()


if __name__ == "__main__":
    asyncio.run(demo())
