#!/usr/bin/env python3
"""
Server Detector — detects Nginx, Apache, IIS, etc.
"""

from typing import Dict, Optional

class ServerDetector:
    """Detect web servers from headers"""
    
    SIGNATURES = {
        'nginx': {'header': 'server', 'patterns': ['nginx']},
        'apache': {'header': 'server', 'patterns': ['apache', 'httpd']},
        'iis': {'header': 'server', 'patterns': ['iis', 'microsoft']},
        'caddy': {'header': 'server', 'patterns': ['caddy']},
        'openresty': {'header': 'server', 'patterns': ['openresty']},
        'cloudflare': {'header': 'server', 'patterns': ['cloudflare']},
        'fastly': {'header': 'server', 'patterns': ['fastly']},
    }
    
    def detect(self, headers: dict) -> Optional[Dict]:
        """Detect server from headers"""
        server = headers.get('server', '').lower() or headers.get('x-powered-by', '').lower()
        
        for name, sig in self.SIGNATURES.items():
            for pattern in sig['patterns']:
                if pattern.lower() in server.lower():
                    return {'type': name, 'server': server, 'confidence': 90}
        
        return None
