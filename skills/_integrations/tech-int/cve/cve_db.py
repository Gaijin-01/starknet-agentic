#!/usr/bin/env python3
"""
CVE Database — simple CVE matching
"""

import json
from pathlib import Path
from typing import List, Dict

class CVEdb:
    """Simple CVE database"""
    
    def __init__(self, db_path: str = "cve.db"):
        self.db_path = db_path
    
    def search(self, query: str) -> List[Dict]:
        """Search CVEs (placeholder)"""
        return []
    
    def get_cve_for_software(self, software: str, version: str = None) -> List[Dict]:
        """Get CVEs for software"""
        return []
