#!/usr/bin/env python3
"""
research.py - Universal web search skill

Supports multiple search providers via config.yaml
"""

import os
import sys
import json
import logging
import argparse
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from abc import ABC, abstractmethod

# Add parent to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "config"))
from config_loader import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================
# SEARCH PROVIDER INTERFACE
# ============================================

class SearchProvider(ABC):
    """Base class for search providers"""
    
    @abstractmethod
    def search(self, query: str, count: int = 10) -> List[Dict]:
        pass


# ============================================
# BRAVE SEARCH
# ============================================

class BraveSearch(SearchProvider):
    """Brave Search API."""
    
    BASE_URL = "https://api.search.brave.com/res/v1/web/search"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def search(self, query: str, count: int = 10) -> List[Dict]:
        params = urllib.parse.urlencode({
            'q': query,
            'count': count,
            'freshness': 'pw'  # past week
        })
        
        url = f"{self.BASE_URL}?{params}"
        req = urllib.request.Request(
            url,
            headers={
                'Accept': 'application/json',
                'X-Subscription-Token': self.api_key
            }
        )
        
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
            
            results = []
            for item in data.get('web', {}).get('results', []):
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('url', ''),
                    'snippet': item.get('description', ''),
                    'published': item.get('age', '')
                })
            return results
            
        except Exception as e:
            logger.error(f"Brave search failed: {e}")
            return []


# ============================================
# SERPER (Google via serper.dev)
# ============================================

class SerperSearch(SearchProvider):
    """Serper.dev Google Search API."""
    
    BASE_URL = "https://google.serper.dev/search"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def search(self, query: str, count: int = 10) -> List[Dict]:
        payload = json.dumps({
            'q': query,
            'num': count
        }).encode()
        
        req = urllib.request.Request(
            self.BASE_URL,
            data=payload,
            headers={
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }
        )
        
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
            
            results = []
            for item in data.get('organic', []):
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'published': item.get('date', '')
                })
            return results
            
        except Exception as e:
            logger.error(f"Serper search failed: {e}")
            return []


# ============================================
# DUCKDUCKGO (Free, no API key)
# ============================================

class DuckDuckGoSearch(SearchProvider):
    """DuckDuckGo Instant Answers API (free, limited)."""
    
    BASE_URL = "https://api.duckduckgo.com/"
    
    def __init__(self):
        pass
    
    def search(self, query: str, count: int = 10) -> List[Dict]:
        params = urllib.parse.urlencode({
            'q': query,
            'format': 'json',
            'no_redirect': 1,
            'no_html': 1
        })
        
        url = f"{self.BASE_URL}?{params}"
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'ClawdBot/1.0'}
        )
        
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
            
            results = []
            
            # Abstract (main result)
            if data.get('Abstract'):
                results.append({
                    'title': data.get('Heading', 'Result'),
                    'url': data.get('AbstractURL', ''),
                    'snippet': data.get('Abstract', ''),
                    'published': ''
                })
            
            # Related topics
            for item in data.get('RelatedTopics', [])[:count]:
                if isinstance(item, dict) and item.get('Text'):
                    results.append({
                        'title': item.get('Text', '')[:100],
                        'url': item.get('FirstURL', ''),
                        'snippet': item.get('Text', ''),
                        'published': ''
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            return []


# ============================================
# PROVIDER FACTORY
# ============================================

def get_provider(cfg: Config) -> Optional[SearchProvider]:
    """Get search provider based on config."""
    
    provider_name = cfg.get('apis.search.provider', 'duckduckgo')
    api_key = cfg.get_api_key('search')
    
    if provider_name == 'brave':
        if not api_key:
            logger.warning("BRAVE_API_KEY not set, falling back to DuckDuckGo")
            return DuckDuckGoSearch()
        return BraveSearch(api_key)
    
    elif provider_name == 'serper':
        if not api_key:
            logger.warning("SERPER_API_KEY not set, falling back to DuckDuckGo")
            return DuckDuckGoSearch()
        return SerperSearch(api_key)
    
    elif provider_name == 'duckduckgo':
        return DuckDuckGoSearch()
    
    else:
        logger.warning(f"Unknown provider: {provider_name}, using DuckDuckGo")
        return DuckDuckGoSearch()


# ============================================
# MAIN SEARCH FUNCTION
# ============================================

def research(
    query: Optional[str] = None,
    use_topic: bool = False,
    count: int = 10,
    output_file: Optional[str] = None
) -> Dict:
    """
    Execute search and return results
    
    Args:
        query: Search query string
        use_topic: Use random topic from config
        count: Number of results
        output_file: Optional file to save results
    
    Returns:
        Dict with query, provider, timestamp, results
    """
    cfg = Config()
    
    # Build query
    if use_topic or not query:
        topic = cfg.get_random_topic()
        query = f"{topic} news"
    
    logger.info(f"Searching: {query}")
    
    # Get provider and search
    provider = get_provider(cfg)
    provider_name = cfg.get('apis.search.provider', 'duckduckgo')
    
    results = provider.search(query, count)
    
    output = {
        'query': query,
        'provider': provider_name,
        'timestamp': datetime.now().isoformat(),
        'count': len(results),
        'results': results
    }
    
    # Save to file
    if output_file:
        path = Path(output_file).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(output, f, indent=2)
        logger.info(f"Saved to: {path}")
    
    # Log to memory
    memory_dir = cfg.get('memory.base_dir')
    if memory_dir and cfg.get('memory.daily_log', True):
        today = datetime.now().strftime('%Y-%m-%d')
        log_path = Path(memory_dir) / f"{today}.md"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_path, 'a') as f:
            f.write(f"\n## Research [{datetime.now().strftime('%H:%M')}]\n")
            f.write(f"Query: {query}\n")
            f.write(f"Results: {len(results)}\n")
            if results:
                f.write(f"Top: {results[0]['title']}\n")
    
    return output


# ============================================
# CLI
# ============================================

def main():
    parser = argparse.ArgumentParser(description="Universal research skill")
    parser.add_argument("--query", "-q", help="Search query")
    parser.add_argument("--topic", "-t", action="store_true", help="Use random topic from config")
    parser.add_argument("--count", "-n", type=int, default=10, help="Number of results")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--json", action="store_true", help="Output as JSON to stdout")
    
    args = parser.parse_args()
    
    if not args.query and not args.topic:
        parser.error("Either --query or --topic required")
    
    result = research(
        query=args.query,
        use_topic=args.topic,
        count=args.count,
        output_file=args.output
    )
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n📰 Found {result['count']} results for: {result['query']}")
        print(f"Provider: {result['provider']}\n")
        
        for i, r in enumerate(result['results'][:5], 1):
            print(f"{i}. {r['title']}")
            print(f"   {r['url']}")
            if r['snippet']:
                print(f"   {r['snippet'][:100]}...")
            print()


if __name__ == "__main__":
    main()
