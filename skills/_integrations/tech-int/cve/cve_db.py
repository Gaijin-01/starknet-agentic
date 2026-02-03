#!/usr/bin/env python3
"""
Tech-Int CVE Database
Sync and query NVD CVE database
"""

import sqlite3
import json
import requests
import time
from datetime import datetime
from typing import Optional


class CVEdb:
    """CVE database management"""
    
    NVD_API = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    
    def __init__(self, db_path: str = "cve.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._init_db()
    
    def _init_db(self):
        """Initialize CVE database schema"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cves (
                id TEXT PRIMARY KEY,
                description TEXT,
                cvss REAL,
                severity TEXT,
                affected TEXT,
                published DATE,
                modified DATE,
                references TEXT,
                raw_data TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_cve_id ON cves(id);
            CREATE INDEX IF NOT EXISTS idx_cvss ON cvss DESC;
            CREATE INDEX IF NOT EXISTS idx_published ON cves(published);
        """)
        
        self.conn.commit()
    
    def update_from_nvd(self, api_key: Optional[str] = None):
        """Update CVE database from NVD API"""
        # This is a simplified version - full implementation would use NVD API
        print("[*] CVE update requires NVD API key for production use")
        print("[*] Using local CVE cache for demonstration")
        
        # Add some common CVEs for demo
        self._add_demo_cves()
    
    def _add_demo_cves(self):
        """Add demo CVEs for testing"""
        demo_cves = [
            ("CVE-2021-44228", "Log4Shell", 10.0, "CRITICAL", "Apache Log4j 2.0-beta9 to 2.15.0"),
            ("CVE-2023-44487", "HTTP/2 Rapid Reset", 7.5, "HIGH", "HTTP/2 protocol"),
            ("CVE-2024-3400", "Palo Alto Networks", 10.0, "CRITICAL", "Palo Alto Networks PAN-OS"),
            ("CVE-2023-36884", "Windows Jul", 8.8, "HIGH", "Microsoft Windows"),
        ]
        
        cursor = self.conn.cursor()
        for cve_id, desc, cvss, severity, affected in demo_cves:
            cursor.execute("""
                INSERT OR IGNORE INTO cves (id, description, cvss, severity, affected, published)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (cve_id, desc, cvss, severity, affected, datetime.now().date()))
        
        self.conn.commit()
        print(f"[+] Added {len(demo_cves)} demo CVEs")
    
    def search(self, query: str, limit: int = 100) -> list:
        """Search CVEs"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM cves
            WHERE id LIKE ? OR description LIKE ?
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", limit))
        
        return cursor.fetchall()
    
    def check_tech_cve(self, technology: str, version: Optional[str] = None) -> list:
        """Check CVEs for specific technology"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM cves
            WHERE description LIKE ? AND affected LIKE ?
            ORDER BY cvss DESC
        """, (f"%{technology}%", f"%{version or ''}%"))
        
        return cursor.fetchall()
    
    def count(self) -> int:
        """Get total CVE count"""
        cursor = self.conn.cursor()
        return cursor.execute("SELECT COUNT(*) FROM cves").fetchone()[0]
    
    def close(self):
        """Close database"""
        self.conn.close()
