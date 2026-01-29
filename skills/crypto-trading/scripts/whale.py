"""
Whale Tracking Module.

Monitors large transactions, wallet movements,
and institutional activity on-chain.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict

import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class WhaleTransaction:
    """Represents a whale transaction."""
    tx_hash: str
    from_address: str
    to_address: str
    value: float
    value_usd: float
    token_symbol: str
    token_address: str
    chain: str
    timestamp: datetime
    block_number: int
    gas_used: Optional[float] = None
    gas_price: Optional[float] = None
    is_smart_contract: bool = False


@dataclass
class WalletProfile:
    """Profile of a tracked wallet."""
    address: str
    label: Optional[str] = None
    total_inflow_24h: float = 0
    total_outflow_24h: float = 0
    net_flow: float = 0
    transaction_count_24h: int = 0
    last_active: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)


class WhaleTracker:
    """Tracks whale activity across chains."""
    
    WHALE_THRESHOLDS = {
        "ethereum": 100000,  # $100K+
        "bsc": 50000,        # $50K+
        "arbitrum": 100000,
        "base": 50000,
        "polygon": 25000,
    }
    
    def __init__(
        self,
        api_keys: Optional[Dict[str, str]] = None,
        data_dir: str = "data"
    ):
        """
        Initialize whale tracker.
        
        Args:
            api_keys: API keys for blockchain explorers
            data_dir: Directory for storing whale data
        """
        self.api_keys = api_keys or {
            "etherscan": os.getenv("ETHERSCAN_API_KEY", ""),
            "bscscan": os.getenv("BSCSCAN_API_KEY", ""),
        }
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Tracked wallets
        self._tracked_wallets: Dict[str, WalletProfile] = {}
        self._load_tracked_wallets()
    
    async def close(self):
        """Close async client."""
        await self.client.aclose()
    
    # ============ Transaction Monitoring ============
    
    async def get_large_transactions(
        self,
        chain: str = "ethereum",
        min_value_usd: float = None,
        limit: int = 100
    ) -> List[WhaleTransaction]:
        """
        Get recent large transactions.
        
        Args:
            chain: Blockchain name
            min_value_usd: Minimum USD value (uses threshold if None)
            limit: Max results
            
        Returns:
            List of whale transactions
        """
        min_value = min_value_usd or self.WHALE_THRESHOLDS.get(chain, 100000)
        
        try:
            if chain == "ethereum":
                transactions = await self._get_etherscan_transactions(min_value, limit)
            elif chain == "bsc":
                transactions = await self._get_bscscan_transactions(min_value, limit)
            else:
                # Generic - try DexScreener
                transactions = await self._get_dex_transactions(chain, min_value)
            
            return transactions
            
        except Exception as e:
            logger.error(f"Failed to get large transactions: {e}")
            return []
    
    async def get_wallet_transactions(
        self,
        address: str,
        chain: str = "ethereum",
        limit: int = 100
    ) -> List[WhaleTransaction]:
        """
        Get transactions for a specific wallet.
        
        Args:
            address: Wallet address
            chain: Blockchain
            limit: Max results
            
        Returns:
            List of transactions
        """
        try:
            if chain == "ethereum":
                return await self._get_etherscan_wallet_tx(address, limit)
            elif chain == "bsc":
                return await self._get_bscscan_wallet_tx(address, limit)
            else:
                return []
                
        except Exception as e:
            logger.error(f"Failed to get wallet transactions: {e}")
            return []
    
    # ============ Wallet Tracking ============
    
    def add_tracked_wallet(
        self,
        address: str,
        label: Optional[str] = None,
        tags: Optional[List[str]] = None
    ):
        """
        Add a wallet to tracking list.
        
        Args:
            address: Wallet address
            label: Human-readable label
            tags: Tags for categorizing
        """
        if address not in self._tracked_wallets:
            self._tracked_wallets[address] = WalletProfile(
                address=address,
                label=label,
                tags=tags or []
            )
            self._save_tracked_wallets()
            logger.info(f"Added tracked wallet: {address}")
    
    def remove_tracked_wallet(self, address: str):
        """Remove wallet from tracking."""
        if address in self._tracked_wallets:
            del self._tracked_wallets[address]
            self._save_tracked_wallets()
    
    def list_tracked_wallets(self) -> List[WalletProfile]:
        """List all tracked wallets."""
        return list(self._tracked_wallets.values())
    
    async def update_tracked_wallets(
        self,
        chains: Optional[List[str]] = None
    ) -> Dict[str, WalletProfile]:
        """
        Update profiles for all tracked wallets.
        
        Args:
            chains: Chains to check
            
        Returns:
            Updated wallet profiles
        """
        chains = chains or ["ethereum", "bsc"]
        
        for address, profile in self._tracked_wallets.items():
            for chain in chains:
                try:
                    txs = await self.get_wallet_transactions(address, chain, limit=50)
                    self._update_profile_from_txs(profile, txs)
                except Exception as e:
                    logger.warning(f"Failed to update {address} on {chain}: {e}")
        
        return self._tracked_wallets
    
    def _update_profile_from_txs(
        self,
        profile: WalletProfile,
        transactions: List[WhaleTransaction]
    ):
        """Update wallet profile from transactions."""
        now = datetime.now()
        cutoff = now - timedelta(hours=24)
        
        inflow = 0.0
        outflow = 0.0
        count = 0
        
        for tx in transactions:
            if tx.timestamp < cutoff:
                continue
            
            count += 1
            
            # Determine if inflow or outflow
            if tx.to_address.lower() == profile.address.lower():
                inflow += tx.value_usd
            elif tx.from_address.lower() == profile.address.lower():
                outflow += tx.value_usd
        
        profile.total_inflow_24h = inflow
        profile.total_outflow_24h = outflow
        profile.net_flow = inflow - outflow
        profile.transaction_count_24h = count
        profile.last_active = now
    
    # ============ Alerting ============
    
    async def watch_for_large_transfers(
        self,
        callback: Callable[[WhaleTransaction], None],
        min_value_usd: float = 100000,
        poll_interval: int = 60
    ):
        """
        Watch for large transfers and call callback.
        
        Args:
            callback: Function to call on large transfer
            min_value_usd: Minimum USD value to trigger
            poll_interval: Seconds between polls
        """
        last_tx_hash = ""
        
        while True:
            try:
                txs = await self.get_large_transactions(
                    min_value_usd=min_value_usd,
                    limit=10
                )
                
                # Process new transactions
                for tx in reversed(txs):
                    if tx.tx_hash != last_tx_hash and tx.value_usd >= min_value_usd:
                        last_tx_hash = tx.tx_hash
                        callback(tx)
                
            except Exception as e:
                logger.error(f"Watch error: {e}")
            
            await asyncio.sleep(poll_interval)
    
    async def watch_wallet(
        self,
        address: str,
        callback: Callable[[WhaleTransaction], None],
        poll_interval: int = 120
    ):
        """
        Watch specific wallet for activity.
        
        Args:
            address: Wallet to watch
            callback: Function to call on activity
            poll_interval: Seconds between polls
        """
        last_tx_hash = ""
        
        while True:
            try:
                txs = await self.get_wallet_transactions(address, limit=5)
                
                for tx in txs:
                    if tx.tx_hash != last_tx_hash:
                        last_tx_hash = tx.tx_hash
                        callback(tx)
                        
            except Exception as e:
                logger.error(f"Wallet watch error: {e}")
            
            await asyncio.sleep(poll_interval)
    
    # ============ Analysis ============
    
    def analyze_flow(
        self,
        transactions: List[WhaleTransaction]
    ) -> Dict[str, Any]:
        """
        Analyze transaction flow patterns.
        
        Args:
            transactions: List of transactions
            
        Returns:
            Analysis results
        """
        total_in = sum(tx.value_usd for tx in transactions if "in" in tx.to_address)
        total_out = sum(tx.value_usd for tx in transactions)
        
        # Group by token
        by_token: Dict[str, float] = defaultdict(float)
        for tx in transactions:
            by_token[tx.token_symbol] += tx.value_usd
        
        # Group by hour
        by_hour: Dict[str, float] = defaultdict(float)
        for tx in transactions:
            hour = tx.timestamp.strftime("%Y-%m-%d %H:00")
            by_hour[hour] += tx.value_usd
        
        return {
            "total_transactions": len(transactions),
            "total_value_usd": total_in + total_out,
            "total_inflow_usd": total_in,
            "total_outflow_usd": total_out,
            "net_flow": total_in - total_out,
            "by_token": dict(by_token),
            "by_hour": dict(by_hour),
            "avg_transaction_value": (total_in + total_out) / len(transactions) if transactions else 0,
            "largest_transaction": max(transactions, key=lambda x: x.value_usd).__dict__ if transactions else None
        }
    
    def get_whale_sentiment(
        self,
        transactions: List[WhaleTransaction]
    ) -> Dict[str, Any]:
        """
        Analyze whale sentiment from transactions.
        
        Args:
            transactions: List of whale transactions
            
        Returns:
            Sentiment analysis
        """
        if not transactions:
            return {"sentiment": "neutral", "confidence": 0}
        
        # Simple heuristics
        buy_count = 0
        sell_count = 0
        
        for tx in transactions:
            # Large inflow with subsequent distribution could indicate accumulation
            # Large outflow could indicate distribution
            if tx.value_usd > 500000:
                if "0x" in tx.to_address and len(tx.to_address) > 42:
                    buy_count += 1
                if "0x" in tx.from_address and len(tx.from_address) > 42:
                    sell_count += 1
        
        total = buy_count + sell_count
        if total == 0:
            return {"sentiment": "neutral", "confidence": 0}
        
        buy_ratio = buy_count / total
        
        if buy_ratio > 0.6:
            sentiment = "bullish"
        elif buy_ratio < 0.4:
            sentiment = "bearish"
        else:
            sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "confidence": abs(buy_ratio - 0.5) * 2,
            "buy_count": buy_count,
            "sell_count": sell_count,
            "buy_ratio": buy_ratio
        }
    
    # ============ Data Persistence ============
    
    def _load_tracked_wallets(self):
        """Load tracked wallets from file."""
        path = os.path.join(self.data_dir, "tracked_wallets.json")
        if os.path.exists(path):
            try:
                with open(path) as f:
                    data = json.load(f)
                    for addr, info in data.items():
                        self._tracked_wallets[addr] = WalletProfile(
                            address=addr,
                            label=info.get("label"),
                            tags=info.get("tags", [])
                        )
            except Exception as e:
                logger.error(f"Failed to load tracked wallets: {e}")
    
    def _save_tracked_wallets(self):
        """Save tracked wallets to file."""
        path = os.path.join(self.data_dir, "tracked_wallets.json")
        data = {
            addr: {
                "label": profile.label,
                "tags": profile.tags
            }
            for addr, profile in self._tracked_wallets.items()
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    
    # ============ API Methods ============
    
    async def _get_etherscan_transactions(
        self,
        min_value_usd: float,
        limit: int
    ) -> List[WhaleTransaction]:
        """Get large transactions from Etherscan."""
        # Note: Etherscan API requires API key and has limits
        # This is a simplified implementation
        return []
    
    async def _get_bscscan_transactions(
        self,
        min_value_usd: float,
        limit: int
    ) -> List[WhaleTransaction]:
        """Get large transactions from BscScan."""
        return []
    
    async def _get_dex_transactions(
        self,
        chain: str,
        min_value_usd: float
    ) -> List[WhaleTransaction]:
        """Get large DEX transactions."""
        return []
    
    async def _get_etherscan_wallet_tx(
        self,
        address: str,
        limit: int
    ) -> List[WhaleTransaction]:
        """Get wallet transactions from Etherscan."""
        return []
    
    async def _get_bscscan_wallet_tx(
        self,
        address: str,
        limit: int
    ) -> List[WhaleTransaction]:
        """Get wallet transactions from BscScan."""
        return []


# Synchronous wrapper
class SyncWhaleTracker:
    """Synchronous wrapper for WhaleTracker."""
    
    def __init__(self, data_dir: str = "data"):
        self._async = WhaleTracker(data_dir=data_dir)
    
    def get_large_transactions(self, chain: str = "ethereum", min_value_usd: float = None):
        """Get large transactions synchronously."""
        return asyncio.run(self._async.get_large_transactions(chain, min_value_usd))
    
    def get_wallet_transactions(self, address: str, chain: str = "ethereum"):
        """Get wallet transactions synchronously."""
        return asyncio.run(self._async.get_wallet_transactions(address, chain))
    
    def add_tracked_wallet(self, address: str, label: str = None, tags: List[str] = None):
        """Add tracked wallet."""
        self._async.add_tracked_wallet(address, label, tags)
    
    def list_tracked_wallets(self):
        """List tracked wallets."""
        return self._async.list_tracked_wallets()
    
    def close(self):
        """Close async resources."""
        asyncio.run(self._async.close())
