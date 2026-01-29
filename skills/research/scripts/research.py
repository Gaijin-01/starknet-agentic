#!/usr/bin/env python3
"""
research.py - Universal web search skill with retry logic

Supports multiple search providers via config.yaml
Features:
- Retry logic with exponential backoff
- Timeout handling
- Multiple providers (Brave, Serper, DuckDuckGo)
- Configurable via config.yaml
"""

import os
import sys
import json
import logging
import time
import argparse
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

# Add parent to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "config"))
from config_loader import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================
# CUSTOM EXCEPTIONS
# ============================================

class SearchError(Exception):
    """Base exception for search errors."""
    def __init__(self, message: str, provider: str = None, recoverable: bool = True):
        super().__init__(message)
        self.message = message
        self.provider = provider
        self.recoverable = recoverable


class RateLimitError(SearchError):
    """Rate limit exceeded."""
    def __init__(self, provider: str = None, retry_after: int = None):
        message = f"Rate limit exceeded{' for ' + provider if provider else ''}"
        super().__init__(message, provider=provider, recoverable=True)
        self.retry_after = retry_after or 60


class TimeoutError(SearchError):
    """Request timed out."""
    def __init__(self, provider: str = None, timeout: int = 30):
        message = f"Request timed out after {timeout}s{' for ' + provider if provider else ''}"
        super().__init__(message, provider=provider, recoverable=True)


class NetworkError(SearchError):
    """Network connectivity error."""
    def __init__(self, message: str, provider: str = None):
        super().__init__(message, provider=provider, recoverable=True)


class ValidationError(SearchError):
    """Invalid input or response."""
    def __init__(self, message: str, provider: str = None):
        super().__init__(message, provider=provider, recoverable=False)


# ============================================
# RESULT DATACLASS
# ============================================

@dataclass
class SearchResult:
    """Single search result."""
    title: str
    url: str
    snippet: str = ""
    published: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "published": self.published
        }


@dataclass
class SearchResponse:
    """Search API response."""
    query: str
    provider: str
    timestamp: str
    count: int
    results: List[SearchResult] = field(default_factory=list)
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "query": self.query,
            "provider": self.provider,
            "timestamp": self.timestamp,
            "count": self.count,
            "results": [r.to_dict() for r in self.results],
            "error": self.error
        }


# ============================================
# SEARCH PROVIDER INTERFACE
# ============================================

class SearchProvider(ABC):
    """Base class for search providers."""
    
    # Default retry settings
    MAX_RETRIES: int = 3
    INITIAL_DELAY: float = 1.0  # seconds
    BACKOFF_MULTIPLIER: float = 2.0
    TIMEOUT: int = 30  # seconds
    
    def __init__(self):
        self._retry_count = 0
    
    @abstractmethod
    def search(self, query: str, count: int = 10) -> List[SearchResult]:
        """
        Execute search and return results.
        
        Args:
            query: Search query string
            count: Number of results to return
            
        Returns:
            List of SearchResult objects
        """
        pass
    
    def _retry(self, func, *args, **kwargs) -> Any:
        """
        Execute function with retry logic.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            SearchError: After all retries exhausted
        """
        last_error = None
        
        for attempt in range(self.MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            
            except RateLimitError as e:
                last_error = e
                wait_time = (e.retry_after or 
                           self.INITIAL_DELAY * (self.BACKOFF_MULTIPLIER ** attempt))
                logger.warning(f"Rate limited (attempt {attempt + 1}/{self.MAX_RETRIES}), "
                             f"waiting {wait_time}s")
                time.sleep(wait_time)
                
            except TimeoutError as e:
                last_error = e
                wait_time = self.INITIAL_DELAY * (self.BACKOFF_MULTIPLIER ** attempt)
                logger.warning(f"Timeout (attempt {attempt + 1}/{self.MAX_RETRIES}), "
                             f"retrying in {wait_time}s")
                time.sleep(wait_time)
                
            except (NetworkError, urllib.error.HTTPError) as e:
                last_error = e
                if attempt < self.MAX_RETRIES - 1:
                    wait_time = self.INITIAL_DELAY * (self.BACKOFF_MULTIPLIER ** attempt)
                    logger.warning(f"Network error (attempt {attempt + 1}/{self.MAX_RETRIES}): "
                                 f"{e}, retrying in {wait_time}s")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Max retries exceeded for {self.__class__.__name__}")
                    
            except Exception as e:
                # Non-retryable errors
                logger.error(f"Unexpected error in {self.__class__.__name__}: {e}")
                raise SearchError(str(e), provider=self.__class__.__name__, recoverable=False)
        
        # All retries exhausted
        if last_error:
            raise last_error
        raise SearchError("Max retries exceeded", provider=self.__class__.__name__)
    
    def _make_request(self, url: str, headers: Dict = None) -> Dict:
        """
        Make HTTP request with error handling.
        
        Args:
            url: Request URL
            headers: Optional headers
            
        Returns:
            Parsed JSON response
            
        Raises:
            NetworkError: On connectivity issues
            TimeoutError: On timeout
            ValidationError: On invalid response
        """
        headers = headers or {}
        req = urllib.request.Request(url, headers=headers)
        
        try:
            with urllib.request.urlopen(req, timeout=self.TIMEOUT) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                return data
                
        except urllib.error.HTTPError as e:
            if e.code == 429:
                raise RateLimitError(provider=self.__class__.__name__)
            elif e.code >= 500:
                raise NetworkError(f"Server error: {e.code}", provider=self.__class__.__name__)
            else:
                raise NetworkError(f"HTTP error: {e.code}", provider=self.__class__.__name__)
                
        except urllib.error.URLError as e:
            raise NetworkError(f"URL error: {e.reason}", provider=self.__class__.__name__)
            
        except TimeoutError:
            raise TimeoutError(provider=self.__class__.__name__, timeout=self.TIMEOUT)
            
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON response: {e}", provider=self.__class__.__name__)


# ============================================
# BRAVE SEARCH
# ============================================

class BraveSearch(SearchProvider):
    """Brave Search API provider."""
    
    BASE_URL = "https://api.search.brave.com/res/v1/web/search"
    
    def __init__(self, api_key: str):
        """
        Initialize Brave Search provider.
        
        Args:
            api_key: Brave API key
        """
        super().__init__()
        self.api_key = api_key
    
    def search(self, query: str, count: int = 10) -> List[SearchResult]:
        """
        Search using Brave Search API.
        
        Args:
            query: Search query
            count: Number of results (max 20)
            
        Returns:
            List of SearchResult objects
        """
        count = min(count, 20)  # Brave limit
        
        params = urllib.parse.urlencode({
            'q': query,
            'count': count,
            'freshness': 'pw'  # past week
        })
        
        url = f"{self.BASE_URL}?{params}"
        headers = {
            'Accept': 'application/json',
            'X-Subscription-Token': self.api_key
        }
        
        try:
            data = self._make_request(url, headers)
            
            results = []
            for item in data.get('web', {}).get('results', []):
                results.append(SearchResult(
                    title=item.get('title', ''),
                    url=item.get('url', ''),
                    snippet=item.get('description', ''),
                    published=item.get('age', '')
                ))
            
            logger.info(f"Brave search returned {len(results)} results")
            return results
            
        except SearchError:
            raise
        except Exception as e:
            logger.error(f"Brave search error: {e}")
            raise SearchError(str(e), provider="BraveSearch")


# ============================================
# SERPER (Google via serper.dev)
# ============================================

class SerperSearch(SearchProvider):
    """Serper.dev Google Search API provider."""
    
    BASE_URL = "https://google.serper.dev/search"
    
    def __init__(self, api_key: str):
        """
        Initialize Serper Search provider.
        
        Args:
            api_key: Serper API key
        """
        super().__init__()
        self.api_key = api_key
    
    def search(self, query: str, count: int = 10) -> List[SearchResult]:
        """
        Search using Serper.dev API.
        
        Args:
            query: Search query
            count: Number of results
            
        Returns:
            List of SearchResult objects
        """
        payload = json.dumps({
            'q': query,
            'num': count
        }).encode('utf-8')
        
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            data = self._make_request(self.BASE_URL, headers)
            
            results = []
            for item in data.get('organic', []):
                results.append(SearchResult(
                    title=item.get('title', ''),
                    url=item.get('link', ''),
                    snippet=item.get('snippet', ''),
                    published=item.get('date', '')
                ))
            
            logger.info(f"Serper search returned {len(results)} results")
            return results
            
        except SearchError:
            raise
        except Exception as e:
            logger.error(f"Serper search error: {e}")
            raise SearchError(str(e), provider="SerperSearch")


# ============================================
# DUCKDUCKGO (Free, no API key)
# ============================================

class DuckDuckGoSearch(SearchProvider):
    """DuckDuckGo Instant Answers API provider (free, limited)."""
    
    BASE_URL = "https://api.duckduckgo.com/"
    
    def __init__(self):
        """Initialize DuckDuckGo provider (no API key required)."""
        super().__init__()
    
    def search(self, query: str, count: int = 10) -> List[SearchResult]:
        """
        Search using DuckDuckGo Instant Answers API.
        
        Args:
            query: Search query
            count: Number of results
            
        Returns:
            List of SearchResult objects
        """
        params = urllib.parse.urlencode({
            'q': query,
            'format': 'json',
            'no_redirect': 1,
            'no_html': 1
        })
        
        url = f"{self.BASE_URL}?{params}"
        headers = {'User-Agent': 'ClawdBot/1.0'}
        
        try:
            data = self._make_request(url, headers)
            
            results = []
            
            # Abstract (main result)
            if data.get('Abstract'):
                results.append(SearchResult(
                    title=data.get('Heading', 'Result'),
                    url=data.get('AbstractURL', ''),
                    snippet=data.get('Abstract', ''),
                    published=''
                ))
            
            # Related topics
            for item in data.get('RelatedTopics', [])[:count]:
                if isinstance(item, dict) and item.get('Text'):
                    results.append(SearchResult(
                        title=item.get('Text', '')[:100],
                        url=item.get('FirstURL', ''),
                        snippet=item.get('Text', ''),
                        published=''
                    ))
            
            logger.info(f"DuckDuckGo search returned {len(results)} results")
            return results
            
        except SearchError:
            raise
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            raise SearchError(str(e), provider="DuckDuckGoSearch")


# ============================================
# PROVIDER FACTORY
# ============================================

def get_provider(cfg: Config) -> SearchProvider:
    """
    Get search provider based on config.
    
    Args:
        cfg: Config object
        
    Returns:
        SearchProvider instance
        
    Raises:
        ValueError: If provider name unknown
    """
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
        raise ValueError(f"Unknown search provider: {provider_name}")


# ============================================
# MAIN SEARCH FUNCTION
# ============================================

def research(
    query: Optional[str] = None,
    use_topic: bool = False,
    count: int = 10,
    output_file: Optional[str] = None,
    provider: Optional[str] = None
) -> SearchResponse:
    """
    Execute search and return results with retry logic.
    
    Args:
        query: Search query string. If None and use_topic=True, 
               uses random topic from config.
        use_topic: If True and query is None, use random topic.
        count: Number of results to return (default 10).
        output_file: Optional file path to save results (JSON).
        provider: Override provider name (optional).
        
    Returns:
        SearchResponse object with results and metadata.
        
    Raises:
        SearchError: If search fails after all retries.
    """
    cfg = Config()
    
    # Build query
    if use_topic or not query:
        topic = cfg.get_random_topic()
        query = f"{topic} news"
    
    logger.info(f"Searching: {query}")
    
    # Get provider
    provider_name = provider or cfg.get('apis.search.provider', 'duckduckgo')
    
    try:
        if provider_name == 'brave':
            api_key = cfg.get_api_key('search')
            if not api_key:
                raise ValueError("BRAVE_API_KEY not configured")
            search_provider = BraveSearch(api_key)
        elif provider_name == 'serper':
            api_key = cfg.get_api_key('search')
            if not api_key:
                raise ValueError("SERPER_API_KEY not configured")
            search_provider = SerperSearch(api_key)
        elif provider_name == 'duckduckgo':
            search_provider = DuckDuckGoSearch()
        else:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        # Execute search with retry
        results = search_provider._retry(
            search_provider.search,
            query,
            count
        )
        
        response = SearchResponse(
            query=query,
            provider=provider_name,
            timestamp=datetime.now().isoformat(),
            count=len(results),
            results=results
        )
        
    except SearchError as e:
        logger.error(f"Search failed: {e}")
        response = SearchResponse(
            query=query,
            provider=provider_name,
            timestamp=datetime.now().isoformat(),
            count=0,
            results=[],
            error=str(e)
        )
    
    # Save to file
    if output_file:
        path = Path(output_file).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(response.to_dict(), f, indent=2, ensure_ascii=False)
        logger.info(f"Saved to: {path}")
    
    # Log to memory
    _log_to_memory(cfg, query, response.count)
    
    return response


def _log_to_memory(cfg: Config, query: str, count: int):
    """
    Log search to daily memory file.
    
    Args:
        cfg: Config object
        query: Search query
        count: Number of results found
    """
    memory_dir = cfg.get('memory.base_dir')
    if not memory_dir or not cfg.get('memory.daily_log', True):
        return
    
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        log_path = Path(memory_dir) / f"{today}.md"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"\n## Research [{datetime.now().strftime('%H:%M')}]\n")
            f.write(f"Query: {query}\n")
            f.write(f"Results: {count}\n")
    except Exception as e:
        logger.warning(f"Failed to log to memory: {e}")


# ============================================
# CLI
# ============================================

def main():
    """CLI entry point for research skill."""
    parser = argparse.ArgumentParser(
        description="Universal research skill with retry logic",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--query", "-q", help="Search query")
    parser.add_argument("--topic", "-t", action="store_true", 
                       help="Use random topic from config")
    parser.add_argument("--count", "-n", type=int, default=10,
                       help="Number of results (default: 10)")
    parser.add_argument("--output", "-o", help="Output file path (JSON)")
    parser.add_argument("--provider", "-p", choices=['brave', 'serper', 'duckduckgo'],
                       help="Override search provider")
    parser.add_argument("--json", action="store_true",
                       help="Output as JSON to stdout")
    
    args = parser.parse_args()
    
    if not args.query and not args.topic:
        parser.error("Either --query or --topic required")
    
    try:
        result = research(
            query=args.query,
            use_topic=args.topic,
            count=args.count,
            output_file=args.output,
            provider=args.provider
        )
        
        if args.json:
            print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
        else:
            if result.error:
                print(f"\n❌ Error: {result.error}")
                return
            
            print(f"\n📰 Found {result.count} results for: {result.query}")
            print(f"Provider: {result.provider}\n")
            
            for i, r in enumerate(result.results[:5], 1):
                print(f"{i}. {r.title}")
                print(f"   {r.url}")
                if r.snippet:
                    print(f"   {r.snippet[:100]}...")
                print()
                
    except Exception as e:
        logger.error(f"Research failed: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
