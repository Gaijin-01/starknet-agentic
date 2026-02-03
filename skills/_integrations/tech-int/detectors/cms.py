#!/usr/bin/env python3
"""
CMS Detector — detects WordPress, Drupal, Joomla, etc.
"""

from typing import Dict, Optional
from bs4 import BeautifulSoup
import re

class CMSDetector:
    """Detect content management systems"""
    
    SIGNATURES = {
        'wordpress': {
            'paths': ['/wp-content/', '/wp-admin/', '/wp-includes/'],
            'markers': ['wp-content', 'wordpress', 'wp-json'],
            'generator': [r'WordPress[\s\d\.]*']
        },
        'drupal': {
            'paths': ['/sites/default/', '/modules/', '/themes/'],
            'markers': ['drupal', 'Drupal'],
            'generator': [r'Drupal[\s\d\.]*']
        },
        'joomla': {
            'paths': ['/templates/', '/media/', '/components/'],
            'markers': ['joomla', 'Joomla'],
            'generator': [r'Joomla![\s\d\.]*']
        },
        'wordpress': {
            'generator': [r'<meta name="generator" content="WordPress[^"]*"']
        }
    }
    
    async def detect(self, html: str, headers: dict, url: str) -> Optional[Dict]:
        """Detect CMS from response"""
        soup = BeautifulSoup(html, 'lxml')
        
        # Check meta generator
        meta_gen = soup.find('meta', {'name': 'generator'})
        if meta_gen and meta_gen.get('content'):
            content = meta_gen['content'].lower()
            for cms, sigs in self.SIGNATURES.items():
                for pattern in sigs.get('generator', []):
                    if re.search(pattern, content, re.I):
                        return {'type': cms, 'confidence': 95}
        
        # Check URL paths
        for cms, sigs in self.SIGNATURES.items():
            for path in sigs.get('paths', []):
                if path in url.lower():
                    return {'type': cms, 'confidence': 85}
        
        # Check HTML content
        for cms, sigs in self.SIGNATURES.items():
            for marker in sigs.get('markers', []):
                if marker.lower() in html.lower():
                    return {'type': cms, 'confidence': 75}
        
        return None
