#!/usr/bin/env python3
"""
Framework Detector — detects React, Vue, Django, Flask, etc.
"""

from typing import Dict, Optional
from bs4 import BeautifulSoup
import re

class FrameworkDetector:
    """Detect JavaScript frameworks and backend frameworks"""
    
    SIGNATURES = {
        'react': {
            'markers': ['react', '__react', '_react'],
            'scripts': ['react', 'react.'],
            'meta': [r'react\d*\.min\.js', r'react.production']
        },
        'vue': {
            'markers': ['vue', '__vue'],
            'scripts': ['vue.js', 'vue.min.js'],
            'meta': [r'vue\d*\.min\.js']
        },
        'angular': {
            'markers': ['angular', 'ng-'],
            'scripts': ['angular.js', 'angular.min.js'],
            'meta': [r'angular[\d\.]*\.js']
        },
        'next.js': {
            'markers': ['next', '_next'],
            'paths': ['/_next/', '/_nextjs/']
        },
        'django': {
            'markers': ['django', 'csrftoken'],
            'cookies': ['csrftoken', 'sessionid']
        },
        'flask': {
            'markers': ['flask', 'csrf_token'],
            'cookies': ['session']
        },
        'laravel': {
            'markers': ['laravel', 'XSRF-TOKEN'],
            'cookies': ['XSRF-TOKEN', 'laravel_session']
        }
    }
    
    async def detect(self, html: str, headers: dict, cookies: dict = None) -> Optional[Dict]:
        """Detect frameworks"""
        soup = BeautifulSoup(html, 'lxml')
        cookies = cookies or {}
        
        # Check scripts
        scripts = [s.get('src', '') for s in soup.find_all('script')]
        scripts_str = ' '.join(scripts)
        
        for fw, sig in self.SIGNATURES.items():
            # Check scripts
            for pattern in sig.get('scripts', []):
                if pattern.lower() in scripts_str.lower():
                    return {'type': fw, 'confidence': 85}
            
            # Check markers in HTML
            for marker in sig.get('markers', []):
                if marker.lower() in html.lower():
                    return {'type': fw, 'confidence': 80}
            
            # Check cookies
            if 'cookies' in sig:
                for cookie in sig['cookies']:
                    if cookie.lower() in [c.lower() for c in cookies.keys()]:
                        return {'type': fw, 'confidence': 70}
        
        return None
