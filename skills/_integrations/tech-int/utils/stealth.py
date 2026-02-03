#!/usr/bin/env python3
"""
Tech-Int Stealth Client
Randomized User-Agents, delays, and proxy support
"""

import asyncio
import aiohttp
import random
import time
from typing import Optional
from pathlib import Path


class StealthClient:
    """Stealth HTTP client with anti-detection features"""
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]
    
    def __init__(
        self,
        min_delay: float = 1.0,
        max_delay: float = 5.0,
        proxy_file: Optional[str] = None,
        verify_ssl: bool = True
    ):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.proxy_list = self._load_proxies(proxy_file) if proxy_file else []
        self.session: Optional[aiohttp.ClientSession] = None
        self.verify_ssl = verify_ssl
        self.last_request_time = 0
    
    def _load_proxies(self, proxy_file: str) -> list:
        """Load proxies from file"""
        proxies = []
        path = Path(proxy_file)
        if path.exists():
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        proxies.append(line)
        return proxies
    
    def _get_headers(self) -> dict:
        """Generate random headers"""
        return {
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0"
        }
    
    def _get_proxy(self) -> Optional[str]:
        """Get random proxy"""
        if self.proxy_list:
            return random.choice(self.proxy_list)
        return None
    
    async def _delay(self):
        """Apply random delay between requests"""
        now = time.time()
        elapsed = now - self.last_request_time
        
        if elapsed < self.min_delay:
            await asyncio.sleep(self.min_delay - elapsed)
        
        # Random additional delay
        await asyncio.sleep(random.uniform(0, self.max_delay - self.min_delay))
        self.last_request_time = time.time()
    
    async def fetch(self, url: str) -> aiohttp.ClientResponse:
        """Fetch URL with stealth features"""
        await self._delay()
        
        proxy = self._get_proxy()
        headers = self._get_headers()
        
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=timeout,
                ssl=self.verify_ssl
            )
        
        try:
            resp = await self.session.get(url, proxy=proxy)
            return resp
        except Exception as e:
            # Try without proxy on failure
            if proxy:
                resp = await self.session.get(url)
                return resp
            raise
    
    async def close(self):
        """Close session"""
        if self.session:
            await self.session.close()
            self.session = None
