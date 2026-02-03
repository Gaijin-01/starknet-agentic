#!/usr/bin/env python3
"""
Tech-Int Web Fetch Integration
Uses OpenClaw web_fetch tool for sandbox-compatible requests
"""

import subprocess
import json
from typing import Optional, Dict, Any


class WebFetcher:
    """Fetch URLs using OpenClaw web_fetch tool"""
    
    def fetch(self, url: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
        """Fetch URL using web_fetch tool"""
        try:
            result = subprocess.run(
                ["/home/wner/clawd/.env/bin/python", "-c", f"""
import sys
sys.path.insert(0, '/home/wner/clawd')
from tools.web_fetch import web_fetch
import asyncio

async def fetch_url():
    try:
        result = await web_fetch(url="{url}", maxChars=50000, extractMode="text")
        return result
    except Exception as e:
        return {{"error": str(e)}}

result = asyncio.run(fetch_url())
print(json.dumps(result))
"""],
                capture_output=True,
                text=True,
                timeout=timeout + 10
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if "error" not in data:
                    return {
                        "text": data.get("text", data.get("content", "")),
                        "headers": {},
                        "status": data.get("status", 200)
                    }
        
        except Exception as e:
            pass
        
        return None
    
    def fetch_with_headers(self, url: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
        """Fetch URL with headers using curl (fallback for working environments)"""
        import subprocess
        
        try:
            # Get headers with curl
            result = subprocess.run(
                ["/usr/bin/curl", "-sI", "-m", str(timeout), url],
                capture_output=True,
                text=True,
                timeout=timeout + 5
            )
            
            if result.returncode == 0:
                headers = {}
                for line in result.stdout.split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        headers[key.strip().lower()] = value.strip()
                
                return {
                    "text": "",
                    "headers": headers,
                    "status": 200
                }
        
        except Exception as e:
            pass
        
        return None
