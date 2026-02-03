#!/usr/bin/env python3
"""
Stealth Client — rotates User-Agent, handles delays, proxies
"""

import asyncio
import random
from typing import Optional

class StealthClient:
    """Stealth HTTP client with rotation"""
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    ]
    
    def __init__(self, delay: float = 1.0, proxy: str = None):
        self.delay = delay
        self.proxy = proxy
        self.last_request = 0
    
    def get_headers(self) -> dict:
        return {
            'User-Agent': random.choice(self.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    async def get(self, url: str, session) -> tuple:
        """Make stealth request"""
        import time
        time.sleep(self.delay)  # Simple delay
        
        async with session.get(url, headers=self.get_headers(), proxy=self.proxy) as resp:
            html = await resp.text()
            return resp.status, html, dict(resp.headers)
