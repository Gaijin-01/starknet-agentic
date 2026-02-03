#!/usr/bin/env python3
"""
Tech-Int Browser Fetcher
Uses OpenClaw browser tool for JavaScript rendering
"""

import subprocess
import json
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any


class BrowserFetcher:
    """Fetch pages using OpenClaw browser tool"""
    
    def __init__(self):
        self.browser_path = None
    
    def find_browser(self) -> Optional[str]:
        """Find OpenClaw browser executable"""
        # Check common locations
        candidates = [
            "/home/wner/clawd/.openclaw/browser/openclaw-browser",
            "/usr/local/bin/openclaw-browser",
            "/usr/bin/openclaw-browser",
        ]
        
        for path in candidates:
            if Path(path).exists():
                self.browser_path = path
                return path
        
        return None
    
    async def fetch_with_browser(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch URL using browser tool"""
        try:
            # Use subprocess to call browser tool
            result = subprocess.run(
                [
                    "python3", "-c",
                    f"""
import json
import sys
sys.path.insert(0, '/home/wner/clawd')
from tools.browser import browser
import asyncio

async def fetch():
    try:
        await browser(action="navigate", targetUrl="{url}")
        await browser(action="snapshot", fullPage=True)
        return {{"status": "success"}}
    except Exception as e:
        return {{"status": "error", "error": str(e)}}

result = asyncio.run(fetch())
print(json.dumps(result))
"""
                ],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
        
        except Exception as e:
            pass
        
        return None
    
    def fetch_screenshot(self, url: str) -> Optional[str]:
        """Get screenshot of page"""
        try:
            result = subprocess.run(
                [
                    "python3", "-c",
                    f"""
import json
import sys
sys.path.insert(0, '/home/wner/clawd')
from tools.browser import browser
import asyncio

async def get_screenshot():
    try:
        await browser(action="navigate", targetUrl="{url}")
        await browser(action="screenshot", path="/tmp/tech-int-screenshot.png")
        return {{"status": "success", "path": "/tmp/tech-int-screenshot.png"}}
    except Exception as e:
        return {{"status": "error", "error": str(e)}}

result = asyncio.run(get_screenshot())
print(json.dumps(result))
"""
                ],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if data.get("status") == "success":
                    return data.get("path")
        
        except Exception as e:
            pass
        
        return None
    
    def get_page_source(self, url: str) -> Optional[str]:
        """Get rendered HTML source"""
        try:
            result = subprocess.run(
                [
                    "python3", "-c",
                    f"""
import json
import sys
sys.path.insert(0, '/home/wner/clawd')
from tools.browser import browser
import asyncio

async def get_source():
    try:
        await browser(action="navigate", targetUrl="{url}")
        # Wait for page to load
        await browser(action="wait", timeMs=3000)
        await browser(action="snapshot", snapshotFormat="text")
        return {{"status": "success"}}
    except Exception as e:
        return {{"status": "error", "error": str(e)}}

result = asyncio.run(get_source())
print(json.dumps(result))
"""
                ],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                return result.stdout
        
        except Exception as e:
            pass
        
        return None
