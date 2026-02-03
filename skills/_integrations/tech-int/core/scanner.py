#!/usr/bin/env python3
"""
Tech-Int Core Scanner
Orchestrates detection modules and collects results
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import json
import random
import time
from typing import Dict, List, Optional
from pathlib import Path

from utils.stealth import StealthClient
from utils.browser_fetcher import BrowserFetcher
from db.models import Target, Technology


class Scanner:
    """Main scanner orchestrator"""
    
    DETECTORS = []
    
    def __init__(self, db, threads: int = 1, stealth: bool = False, browser: bool = False):
        self.db = db
        self.threads = threads
        self.stealth = stealth
        self.browser_mode = browser
        self.client = StealthClient() if stealth else None
        self.browser_fetcher = BrowserFetcher() if browser else None
        self._load_detectors()
    
    def _load_detectors(self):
        """Load all detector modules"""
        detectors_path = Path(__file__).parent.parent / "detectors"
        for detector_file in detectors_path.rglob("*.py"):
            if detector_file.name.startswith("_"):
                continue
            # Import and register detector
            name = detector_file.stem
            # Detectors will be imported dynamically
    
    def scan_single(self, target: str) -> Target:
        """Scan a single target"""
        result = Target(domain=target)
        
        # Parse URL
        parsed = urlparse(target)
        if not parsed.scheme:
            url = f"https://{target}"
        else:
            url = target
        
        try:
            # Fetch homepage
            data = self._fetch(url)
            if data:
                result.status_code = data.get("status")
                result.headers = data.get("headers", {})
                result.url = url
                
                # Parse HTML
                text = data.get("text", "")
                soup = BeautifulSoup(text, "lxml")
                
                # Run built-in detectors
                server_techs = self.detect_server(data.get("headers", {}))
                cms_techs = self.detect_cms(soup, data.get("headers", {}), text)
                js_techs = self.detect_js(soup)
                
                result.technologies.extend(server_techs)
                result.technologies.extend(cms_techs)
                result.technologies.extend(js_techs)
                
                # Save to DB
                self.db.save_target(result)
        
        except Exception as e:
            import traceback
            result.error = str(e)
        
        return result
    
    def scan_multiple(self, targets: List[str]):
        """Scan multiple targets"""
        for target in targets:
            self.scan_single(target)
        return []
    
    def _fetch(self, url: str):
        """Fetch URL and return content using curl (works in sandbox)"""
        import subprocess
        
        # Try curl first (works in sandbox)
        try:
            # Get headers
            result = subprocess.run(
                ["curl", "-sI", "-L", "-m", "10", url],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                headers = {}
                status_code = 200
                
                # Parse headers
                in_body = False
                for line in result.stdout.split("\n"):
                    if line == "":
                        in_body = True
                        continue
                    if not in_body:
                        if ":" in line:
                            key, value = line.split(":", 1)
                            headers[key.strip().lower()] = value.strip()
                
                # Get body
                body_result = subprocess.run(
                    ["curl", "-sS", "-m", "10", url],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                text = body_result.stdout
                
                return {"text": text, "headers": headers, "status": status_code}
        
        except Exception as e:
            pass
        
        return None
    
    def detect_cms(self, soup, headers, text) -> List[Technology]:
        """Detect CMS from HTML patterns"""
        techs = []
        
        # WordPress
        if 'wp-content' in text or 'wp-includes' in text:
            techs.append(Technology(name="WordPress", type="cms", confidence=0.9))
            # Try to get version from meta tag
            version = soup.find("meta", {"name": "generator"})
            if version and "wordpress" in version.get("content", "").lower():
                techs[-1].version = version["content"].split()[-1]
        
        # Drupal
        if 'drupal' in text.lower() or 'Drupal' in text:
            techs.append(Technology(name="Drupal", type="cms", confidence=0.9))
        
        # Joomla
        if 'joomla' in text.lower():
            techs.append(Technology(name="Joomla", type="cms", confidence=0.9))
        
        return techs
    
    def detect_server(self, headers) -> List[Technology]:
        """Detect web server from headers"""
        techs = []
        
        server = headers.get("Server", "")
        x_powered_by = headers.get("X-Powered-By", "")
        
        if "nginx" in server.lower():
            techs.append(Technology(name="Nginx", type="server", confidence=1.0, version=self._extract_version(server)))
        elif "apache" in server.lower():
            techs.append(Technology(name="Apache", type="server", confidence=1.0, version=self._extract_version(server)))
        elif "caddy" in server.lower():
            techs.append(Technology(name="Caddy", type="server", confidence=1.0))
        elif "openresty" in server.lower():
            techs.append(Technology(name="OpenResty", type="server", confidence=1.0))
        elif "cloudflare" in server.lower():
            techs.append(Technology(name="Cloudflare", type="cdn", confidence=1.0))
        elif "iis" in server.lower() or "microsoft" in server.lower():
            techs.append(Technology(name="IIS", type="server", confidence=0.9))
        elif "lighttpd" in server.lower():
            techs.append(Technology(name="Lighttpd", type="server", confidence=1.0))
        
        if "php" in x_powered_by.lower():
            techs.append(Technology(name="PHP", type="language", confidence=0.9))
        elif "asp.net" in x_powered_by.lower():
            techs.append(Technology(name="ASP.NET", type="framework", confidence=0.9))
        elif "express" in x_powered_by.lower():
            techs.append(Technology(name="Express", type="framework", confidence=0.9))
        
        return techs
    
    def detect_js(self, soup) -> List[Technology]:
        """Detect JavaScript libraries from script src"""
        techs = []
        
        scripts = [s.get("src", "") for s in soup.find_all("script")]
        scripts_text = " ".join(scripts)
        
        js_libs = {
            "jquery": r"jquery[.-]?(\d+\.\d+)",
            "react": r"react[.-]?(\d+\.\d+)",
            "vue": r"vue[.-]?(\d+\.\d+)",
            "bootstrap": r"bootstrap[.-]?(\d+\.\d+)",
            "angular": r"angular[.-]?(\d+\.\d+)",
        }
        
        for lib, pattern in js_libs.items():
            match = re.search(pattern, scripts_text, re.I)
            if match:
                techs.append(Technology(name=lib.capitalize(), type="js", confidence=0.8, version=match.group(1)))
        
        return techs
    
    def _extract_version(self, header: str) -> Optional[str]:
        """Extract version from header string"""
        match = re.search(r"/?v?(\d+\.\d+\.?\d*)", header)
        return match.group(1) if match else None
