#!/usr/bin/env python3
"""
Browser Fetcher — uses requests for simple fetching
"""

class BrowserFetcher:
    """Simple browser-like fetcher"""
    
    async def fetch(self, url: str, session) -> tuple:
        """Fetch URL"""
        async with session.get(url) as resp:
            return resp.status, await resp.text(), dict(resp.headers)
