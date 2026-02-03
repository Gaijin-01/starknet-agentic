#!/usr/bin/env python3
"""
Tech-Int Database — SQLite storage for scan results
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional


class Database:
    """SQLite database for technology intelligence"""
    
    def __init__(self, db_path: str = "tech_int.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT UNIQUE NOT NULL,
                url TEXT,
                status_code INTEGER,
                headers TEXT,
                tech_stack TEXT,
                technologies TEXT,
                cves TEXT,
                cvss REAL,
                iot_device TEXT,
                error TEXT,
                scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cve_db (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cve_id TEXT UNIQUE NOT NULL,
                description TEXT,
                cvss REAL,
                affected TEXT,
                published DATE,
                modified DATE
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_domain ON targets(domain)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cve ON targets(cves)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cvss ON targets(cvss)")
        
        self.conn.commit()
    
    def save_target(self, target):
        """Save scan result to database"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO targets 
            (domain, url, status_code, headers, tech_stack, technologies, cves, cvss, iot_device, error, scanned_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            target.domain,
            target.url,
            target.status_code,
            json.dumps(target.headers) if target.headers else None,
            target.get_tech_stack_str(),
            json.dumps([t.to_dict() for t in target.technologies]),
            json.dumps(target.cves) if target.cves else None,
            target.get_max_cvss(),
            target.iot_device,
            target.error,
            datetime.now()
        ))
        
        self.conn.commit()
    
    def search(self, query: str, limit: int = 100) -> List[sqlite3.Row]:
        """Search targets by query"""
        cursor = self.conn.cursor()
        
        # Simple text search across columns
        cursor.execute("""
            SELECT * FROM targets
            WHERE domain LIKE ? OR tech_stack LIKE ? OR technologies LIKE ?
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", f"%{query}%", limit))
        
        return cursor.fetchall()
    
    def search_cve(self, cve_query: str, limit: int = 100) -> List[sqlite3.Row]:
        """Search by CVE ID or year"""
        cursor = self.conn.cursor()
        
        if cve_query.isdigit() and len(cve_query) == 4:
            # Search by year
            cursor.execute("""
                SELECT * FROM targets
                WHERE cves LIKE ?
                ORDER BY cvss DESC
                LIMIT ?
            """, (f"%{cve_query}%", limit))
        else:
            # Search by CVE ID
            cursor.execute("""
                SELECT * FROM targets
                WHERE cves LIKE ?
                ORDER BY cvss DESC
                LIMIT ?
            """, (f"%{cve_query}%", limit))
        
        return cursor.fetchall()
    
    def get_all(self, limit: int = 1000) -> List[sqlite3.Row]:
        """Get all targets"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM targets ORDER BY scanned_at DESC LIMIT ?", (limit,))
        return cursor.fetchall()
    
    def get_stats(self) -> dict:
        """Get database statistics"""
        cursor = self.conn.cursor()
        
        total = cursor.execute("SELECT COUNT(*) FROM targets").fetchone()[0]
        with_cve = cursor.execute("SELECT COUNT(*) FROM targets WHERE cves IS NOT NULL").fetchone()[0]
        iot = cursor.execute("SELECT COUNT(*) FROM targets WHERE iot_device IS NOT NULL").fetchone()[0]
        
        return {
            "total_targets": total,
            "with_cve": with_cve,
            "iot_devices": iot
        }
    
    def close(self):
        """Close database connection"""
        self.conn.close()
