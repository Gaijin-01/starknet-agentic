"""
Whale Database - Track and manage known whale wallets
"""
import json
import sqlite3
import asyncio
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from pathlib import Path


@dataclass
class WhaleWallet:
    """Represent a tracked whale wallet"""
    address: str
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    created_at: str = ""
    last_seen: str = ""
    alert_on: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
        if not self.alert_on:
            self.alert_on = ["large_transfer", "new_position"]


@dataclass
class WhaleActivity:
    """Activity record for a whale wallet"""
    id: int
    wallet_address: str
    event_type: str
    details: Dict
    block_number: int
    timestamp: str
    tx_hash: str = ""


class WhaleDatabase:
    """SQLite database for whale tracking"""

    def __init__(self, db_path: str = "./data/whales.db"):
        self.db_path = db_path
        self.path = Path(db_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Whales table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS whales (
                address TEXT PRIMARY KEY,
                tags TEXT,
                notes TEXT,
                created_at TEXT,
                last_seen TEXT,
                alert_on TEXT
            )
        """)

        # Activity table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wallet_address TEXT,
                event_type TEXT,
                details TEXT,
                block_number INTEGER,
                timestamp TEXT,
                tx_hash TEXT,
                FOREIGN KEY (wallet_address) REFERENCES whales(address)
            )
        """)

        # Indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_activity_wallet
            ON activity(wallet_address)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_activity_time
            ON activity(timestamp)
        """)

        # Portfolio snapshots
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wallet_address TEXT,
                token_address TEXT,
                balance REAL,
                block_number INTEGER,
                timestamp TEXT,
                FOREIGN KEY (wallet_address) REFERENCES whales(address)
            )
        """)

        conn.commit()
        conn.close()

    def _row_to_whale(self, row: Tuple) -> WhaleWallet:
        """Convert database row to WhaleWallet"""
        return WhaleWallet(
            address=row[0],
            tags=json.loads(row[1]) if row[1] else [],
            notes=row[2] or "",
            created_at=row[3] or "",
            last_seen=row[4] or "",
            alert_on=json.loads(row[5]) if row[5] else []
        )

    # === CRUD Operations ===

    def add_whale(self, whale: WhaleWallet) -> bool:
        """Add a new whale to tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO whales
                (address, tags, notes, created_at, last_seen, alert_on)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                whale.address,
                json.dumps(whale.tags),
                whale.notes,
                whale.created_at,
                whale.last_seen,
                json.dumps(whale.alert_on)
            ))
            conn.commit()
            return True
        except sqlite3.Error:
            return False
        finally:
            conn.close()

    def get_whale(self, address: str) -> Optional[WhaleWallet]:
        """Get whale by address"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM whales WHERE address = ?", (address,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return self._row_to_whale(row)
        return None

    def get_all_whales(self) -> List[WhaleWallet]:
        """Get all tracked whales"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM whales ORDER BY last_seen DESC")
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_whale(row) for row in rows]

    def get_by_tag(self, tag: str) -> List[WhaleWallet]:
        """Get whales with specific tag"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM whales WHERE tags LIKE ?", (f'%"{tag}"%',))
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_whale(row) for row in rows]

    def update_whale(self, address: str, **kwargs) -> bool:
        """Update whale fields"""
        allowed_fields = {"tags", "notes", "last_seen", "alert_on"}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not updates:
            return False

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for key, value in updates.items():
            if isinstance(value, list):
                value = json.dumps(value)
            cursor.execute(f"UPDATE whales SET {key} = ? WHERE address = ?", (value, address))

        conn.commit()
        conn.close()
        return True

    def delete_whale(self, address: str) -> bool:
        """Remove whale from tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM whales WHERE address = ?", (address,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return deleted

    # === Activity Tracking ===

    def add_activity(self, activity: WhaleActivity) -> int:
        """Log whale activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO activity
            (wallet_address, event_type, details, block_number, timestamp, tx_hash)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            activity.wallet_address,
            activity.event_type,
            json.dumps(activity.details),
            activity.block_number,
            activity.timestamp,
            activity.tx_hash
        ))

        activity_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Update last_seen
        self.update_whale(activity.wallet_address, last_seen=activity.timestamp)

        return activity_id

    def get_activity(
        self,
        address: str = None,
        event_type: str = None,
        since_hours: int = None,
        limit: int = 100
    ) -> List[WhaleActivity]:
        """Get activity records"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM activity WHERE 1=1"
        params = []

        if address:
            query += " AND wallet_address = ?"
            params.append(address)

        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)

        if since_hours:
            since = (datetime.utcnow() - timedelta(hours=since_hours)).isoformat()
            query += " AND timestamp >= ?"
            params.append(since)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [
            WhaleActivity(
                id=row[0],
                wallet_address=row[1],
                event_type=row[2],
                details=json.loads(row[3]),
                block_number=row[4],
                timestamp=row[5],
                tx_hash=row[6]
            )
            for row in rows
        ]

    def get_recent_activity(self, hours: int = 24, limit: int = 50) -> List[WhaleActivity]:
        """Get recent activity across all whales"""
        return self.get_activity(since_hours=hours, limit=limit)

    # === Portfolio Tracking ===

    def snapshot_portfolio(
        self,
        wallet_address: str,
        token_address: str,
        balance: float,
        block_number: int
    ):
        """Take portfolio snapshot"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO portfolio_snapshots
            (wallet_address, token_address, balance, block_number, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (
            wallet_address,
            token_address,
            balance,
            block_number,
            datetime.utcnow().isoformat()
        ))

        conn.commit()
        conn.close()

    def get_portfolio_history(
        self,
        wallet_address: str,
        token_address: str = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get portfolio history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT * FROM portfolio_snapshots
            WHERE wallet_address = ?
        """
        params = [wallet_address]

        if token_address:
            query += " AND token_address = ?"
            params.append(token_address)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "wallet_address": row[1],
                "token_address": row[2],
                "balance": row[3],
                "block_number": row[4],
                "timestamp": row[5]
            }
            for row in rows
        ]

    # === Analytics ===

    def get_whale_stats(self) -> Dict:
        """Get whale database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {}

        # Total whales
        cursor.execute("SELECT COUNT(*) FROM whales")
        stats["total_whales"] = cursor.fetchone()[0]

        # Whales by tag
        cursor.execute("SELECT tags FROM whales")
        tag_counts = {}
        for row in cursor.fetchall():
            tags = json.loads(row[0]) if row[0] else []
            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        stats["by_tag"] = tag_counts

        # Activity today
        today = datetime.utcnow().replace(hour=0, minute=0, second=0).isoformat()
        cursor.execute("SELECT COUNT(*) FROM activity WHERE timestamp >= ?", (today,))
        stats["activity_today"] = cursor.fetchone()[0]

        conn.close()
        return stats

    def get_active_whales(self, hours: int = 24) -> List[WhaleWallet]:
        """Get whales with recent activity"""
        since = (datetime.utcnow() - timedelta(hours=hours)).isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT w.* FROM whales w
            INNER JOIN activity a ON w.address = a.wallet_address
            WHERE a.timestamp >= ?
            ORDER BY a.timestamp DESC
        """, (since,))

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_whale(row) for row in rows]

    # === Import/Export ===

    def import_from_csv(self, filepath: str):
        """Import whales from CSV file"""
        import csv

        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                whale = WhaleWallet(
                    address=row['address'],
                    tags=row.get('tags', '').split(','),
                    notes=row.get('notes', ''),
                    alert_on=row.get('alert_on', '').split(',')
                )
                self.add_whale(whale)

    def export_to_csv(self, filepath: str):
        """Export whales to CSV file"""
        import csv

        whales = self.get_all_whales()

        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['address', 'tags', 'notes', 'created_at', 'last_seen', 'alert_on'])

            for whale in whales:
                writer.writerow([
                    whale.address,
                    ','.join(whale.tags),
                    whale.notes,
                    whale.created_at,
                    whale.last_seen,
                    ','.join(whale.alert_on)
                ])


# === Convenience Functions ===

def create_default_whales(db: WhaleDatabase):
    """Add some known Starknet whales"""

    whales = [
        WhaleWallet(
            address="0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004d7",
            tags=["foundation", "eth_holder", "large_holder"],
            notes="Starknet Foundation / Ethereum Foundation"
        ),
        WhaleWallet(
            address="0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d",
            tags=["strk_holder", "large_holder"],
            notes="STRK Token Contract (for reference)"
        ),
        WhaleWallet(
            address="0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8",
            tags=["usdc_holder", "large_holder"],
            notes="USDC Token Contract (for reference)"
        ),
    ]

    for whale in whales:
        db.add_whale(whale)

    print(f"Added {len(whales)} default whales")


if __name__ == "__main__":
    # Demo usage
    db = WhaleDatabase("./data/whales.db")

    # Add a test whale
    test_whale = WhaleWallet(
        address="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        tags=["test", "deployer"],
        notes="Test wallet for development"
    )
    db.add_whale(test_whale)

    # Get all whales
    print("\nAll tracked whales:")
    for whale in db.get_all_whales():
        print(f"  {whale.address[:20]}... [{', '.join(whale.tags)}]")

    # Get stats
    print("\nDatabase stats:")
    print(db.get_whale_stats())

    # Get recent activity
    print("\nRecent activity:")
    for activity in db.get_recent_activity(hours=24):
        print(f"  {activity.event_type}: {activity.wallet_address[:20]}...")
