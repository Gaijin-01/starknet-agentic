"""
Whale Database Client for Starknet Intelligence Colony
======================================================
Tracks and analyzes large transactions and whale movements.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import json
import aiofiles

logger = logging.getLogger(__name__)


@dataclass
class WhaleTransaction:
    """A detected whale transaction"""
    tx_hash: str
    block_number: int
    timestamp: str
    from_address: str
    to_address: str
    token_address: str
    token_symbol: str
    amount: float
    amount_usd: float
    gas_fee: float
    gas_fee_usd: float
    
    def to_dict(self) -> dict:
        return {
            "tx_hash": self.tx_hash,
            "block_number": self.block_number,
            "timestamp": self.timestamp,
            "from_address": self.from_address,
            "to_address": self.to_address,
            "token_address": self.token_address,
            "token_symbol": self.token_symbol,
            "amount": self.amount,
            "amount_usd": self.amount_usd,
            "gas_fee": self.gas_fee,
            "gas_fee_usd": self.gas_fee_usd
        }


@dataclass
class WhaleProfile:
    """Profile of a known whale address"""
    address: str
    label: str  # e.g., "Vitalik", "a16z", "unknown"
    category: str  # "institutional", "retail", "developer", "unknown"
    risk_score: float  # 0-1, higher = more risky
    total_transactions: int
    first_seen: str
    last_seen: str
    total_volume_usd: float
    
    def to_dict(self) -> dict:
        return {
            "address": self.address,
            "label": self.label,
            "category": self.category,
            "risk_score": self.risk_score,
            "total_transactions": self.total_transactions,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "total_volume_usd": self.total_volume_usd
        }


class WhaleDBClient:
    """
    Client for tracking whale activity on Starknet.
    
    Features:
    - Large transaction detection
    - Whale address profiling
    - Historical analysis
    - Alert generation
    """
    
    def __init__(self, storage_path: str = None):
        from config import BASE_DIR
        self.storage_path = storage_path or str(BASE_DIR / "whale_data.json")
        
        # In-memory storage
        self._transactions: List[WhaleTransaction] = []
        self._whale_profiles: Dict[str, WhaleProfile] = {}
        
        # Known whale addresses (sample)
        self._known_whales = {
            "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004d7": WhaleProfile(
                address="0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004d7",
                label="Starknet ETH Bridge",
                category="institutional",
                risk_score=0.1,
                total_transactions=15234,
                first_seen="2022-01-01",
                last_seen=datetime.utcnow().isoformat(),
                total_volume_usd=1_500_000_000
            )
        }
        
        # Sample whale transactions for demonstration
        self._sample_transactions = self._generate_sample_data()
    
    def _generate_sample_data(self) -> List[WhaleTransaction]:
        """Generate sample whale transactions for demonstration"""
        transactions = []
        now = datetime.utcnow()
        
        sample_data = [
            ("0x1234...5678", "0xabcd...efgh", "STRK", 50000, 45_000),
            ("0xabcd...efgh", "0x9876...5432", "ETH", 100, 280_000),
            ("0x5555...6666", "0x7777...8888", "USDC", 500000, 500_000),
            ("0x9999...0000", "0xaaaa...bbbb", "WBTC", 50, 3_200_000),
            ("0xcccc...dddd", "0xeeee...ffff", "STRK", 25000, 22_500),
        ]
        
        for i, (from_addr, to_addr, token, amount, amount_usd) in enumerate(sample_data):
            tx_time = now - timedelta(hours=i, minutes=i*10)
            transactions.append(WhaleTransaction(
                tx_hash=f"0x{hash(str(i)) % (16**64):064x}",
                block_number=100000 + i * 100,
                timestamp=tx_time.isoformat(),
                from_address=from_addr,
                to_address=to_addr,
                token_address=f"0x{token.lower()[:40].zfill(40)}",
                token_symbol=token,
                amount=amount,
                amount_usd=amount_usd,
                gas_fee=0.001 * (i + 1),
                gas_fee_usd=2.5 * (i + 1)
            ))
        
        return transactions
    
    async def load_data(self):
        """Load persisted data"""
        try:
            async with aiofiles.open(self.storage_path, 'r') as f:
                content = await f.read()
                data = json.loads(content)
                
                if "transactions" in data:
                    self._transactions = [
                        WhaleTransaction(**tx) for tx in data["transactions"]
                    ]
                if "profiles" in data:
                    self._whale_profiles = {
                        addr: WhaleProfile(**prof) 
                        for addr, prof in data["profiles"].items()
                    }
        except FileNotFoundError:
            logger.info("No existing whale data found")
        except Exception as e:
            logger.error(f"Error loading whale data: {e}")
    
    async def save_data(self):
        """Persist data to storage"""
        try:
            data = {
                "transactions": [tx.to_dict() for tx in self._transactions],
                "profiles": {
                    addr: prof.to_dict() 
                    for addr, prof in self._whale_profiles.items()
                },
                "saved_at": datetime.utcnow().isoformat()
            }
            
            async with aiofiles.open(self.storage_path, 'w') as f:
                await f.write(json.dumps(data, indent=2, default=str))
        except Exception as e:
            logger.error(f"Error saving whale data: {e}")
    
    # =========================================================================
    # Transaction Tracking
    # =========================================================================
    
    async def add_transaction(self, tx: WhaleTransaction):
        """Add a whale transaction"""
        self._transactions.insert(0, tx)
        # Keep only last 5000 transactions
        self._transactions = self._transactions[:5000]
        
        # Update profile for sender
        await self._update_profile(tx.from_address, tx.amount_usd)
        
        # Update profile for receiver
        await self._update_profile(tx.to_address, tx.amount_usd)
    
    async def get_transactions(self, 
                               since_hours: int = 24,
                               min_amount_usd: float = 0,
                               token: Optional[str] = None,
                               limit: int = 100) -> List[WhaleTransaction]:
        """Get whale transactions with filters"""
        cutoff = datetime.utcnow() - timedelta(hours=since_hours)
        
        filtered = []
        for tx in self._transactions:
            tx_time = datetime.fromisoformat(tx.timestamp)
            
            if tx_time < cutoff:
                continue
            if tx.amount_usd < min_amount_usd:
                continue
            if token and tx.token_symbol != token:
                continue
            
            filtered.append(tx)
        
        return filtered[:limit]
    
    async def get_large_transfers(self, 
                                   threshold_usd: float = 100_000,
                                   limit: int = 50) -> List[WhaleTransaction]:
        """Get large transfers above threshold"""
        return await self.get_transactions(
            since_hours=24,
            min_amount_usd=threshold_usd,
            limit=limit
        )
    
    # =========================================================================
    # Whale Profiles
    # =========================================================================
    
    async def _update_profile(self, address: str, volume_usd: float):
        """Update or create whale profile"""
        if address in self._known_whales:
            profile = self._known_whales[address]
        elif address in self._whale_profiles:
            profile = self._whale_profiles[address]
        else:
            profile = WhaleProfile(
                address=address,
                label="unknown",
                category="unknown",
                risk_score=0.5,
                total_transactions=0,
                first_seen=datetime.utcnow().isoformat(),
                last_seen=datetime.utcnow().isoformat(),
                total_volume_usd=0
            )
            self._whale_profiles[address] = profile
        
        profile.total_transactions += 1
        profile.total_volume_usd += volume_usd
        profile.last_seen = datetime.utcnow().isoformat()
    
    async def get_whale_profile(self, address: str) -> Optional[WhaleProfile]:
        """Get profile for a whale address"""
        return self._known_whales.get(address) or self._whale_profiles.get(address)
    
    async def get_active_whales(self, 
                                 since_hours: int = 24,
                                 limit: int = 20) -> List[Dict]:
        """Get most active whales recently"""
        cutoff = datetime.utcnow() - timedelta(hours=since_hours)
        
        whale_activity: Dict[str, Dict] = {}
        
        for tx in self._transactions:
            tx_time = datetime.fromisoformat(tx.timestamp)
            if tx_time < cutoff:
                continue
            
            for addr in [tx.from_address, tx.to_address]:
                if addr not in whale_activity:
                    whale_activity[addr] = {
                        "address": addr,
                        "tx_count": 0,
                        "volume_usd": 0,
                        "tokens": set()
                    }
                
                whale_activity[addr]["tx_count"] += 1
                whale_activity[addr]["volume_usd"] += tx.amount_usd
                whale_activity[addr]["tokens"].add(tx.token_symbol)
        
        # Convert and sort
        result = [
            {
                "address": data["address"],
                "tx_count": data["tx_count"],
                "volume_usd": data["volume_usd"],
                "tokens": list(data["tokens"]),
                "profile": (await self.get_whale_profile(data["address"])).to_dict() 
                          if await self.get_whale_profile(data["address"]) else None
            }
            for data in whale_activity.values()
        ]
        
        return sorted(result, key=lambda x: x["volume_usd"], reverse=True)[:limit]
    
    # =========================================================================
    # Analysis and Alerts
    # =========================================================================
    
    async def detect_unusual_activity(self, 
                                       address: str,
                                       volume_multiplier: float = 3.0) -> Dict:
        """
        Detect if an address is making unusual movements.
        
        Args:
            address: Wallet address to check
            volume_multiplier: How much above normal to trigger alert
        
        Returns:
            Dict with alert info if unusual, empty dict otherwise
        """
        # Get recent activity
        recent_txs = [
            tx for tx in self._transactions
            if (tx.from_address == address or tx.to_address == address) and
            datetime.fromisoformat(tx.timestamp) > datetime.utcnow() - timedelta(hours=1)
        ]
        
        if not recent_txs:
            return {}
        
        # Calculate average transaction size
        avg_amount = sum(tx.amount_usd for tx in recent_txs) / len(recent_txs)
        
        # Check for large outlier
        for tx in recent_txs:
            if tx.amount_usd > avg_amount * volume_multiplier:
                return {
                    "address": address,
                    "tx_hash": tx.tx_hash,
                    "amount_usd": tx.amount_usd,
                    "average_amount": avg_amount,
                    "multiple": tx.amount_usd / avg_amount if avg_amount > 0 else 0,
                    "type": "unusual_volume"
                }
        
        return {}
    
    async def get_whale_movement_summary(self, 
                                          hours: int = 24) -> Dict[str, Any]:
        """Get summary of whale movements"""
        txs = await self.get_transactions(since_hours=hours)
        
        total_volume = sum(tx.amount_usd for tx in txs)
        tx_count = len(txs)
        
        # Volume by token
        by_token = {}
        for tx in txs:
            token = tx.token_symbol
            if token not in by_token:
                by_token[token] = {"volume": 0, "tx_count": 0}
            by_token[token]["volume"] += tx.amount_usd
            by_token[token]["tx_count"] += 1
        
        # Volume by direction
        inflow = sum(
            tx.amount_usd for tx in txs 
            if tx.to_address and self._is_known_cex(tx.to_address)
        )
        outflow = sum(
            tx.amount_usd for tx in txs 
            if tx.from_address and self._is_known_cex(tx.from_address)
        )
        
        return {
            "period_hours": hours,
            "total_volume_usd": total_volume,
            "transaction_count": tx_count,
            "average_tx_size": total_volume / tx_count if tx_count > 0 else 0,
            "by_token": by_token,
            "inflow_estimate": inflow,
            "outflow_estimate": outflow,
            "large_transfers": len([tx for tx in txs if tx.amount_usd >= 100_000]),
            "whales_detected": len(set(
                tx.from_address for tx in txs
            ).union(set(tx.to_address for tx in txs))),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _is_known_cex(self, address: str) -> bool:
        """Check if address is a known CEX"""
        # Simplified - in production, maintain a list of known CEX addresses
        cex_patterns = ["0xcex", "0xexchange"]
        return any(pattern in address.lower() for pattern in cex_patterns)
    
    async def get_sample_transactions(self, limit: int = 10) -> List[WhaleTransaction]:
        """Get sample whale transactions for demo"""
        return self._sample_transactions[:limit]


# Create global client instance
whale_db_client = WhaleDBClient()
