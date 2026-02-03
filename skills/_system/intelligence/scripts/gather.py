#!/usr/bin/env python3
"""
gather.py - Multi-source intelligence gathering.

Gathers signals from:
- X/Twitter (via search and tracked accounts)
- Reddit (subreddit posts)
- Hacker News (keyword searches)
- On-chain (DEX screener, Birdeye)
- Whale tracker (existing database)
"""

import os
import sys
import json
import logging
import asyncio
import aiohttp
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import urllib.parse

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import load_config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class IntelligenceSignal:
    """Single intelligence signal."""
    id: str
    source: str
    type: str  # tweet, post, story, transaction, activity
    title: str
    content: str
    url: str
    author: str
    timestamp: str
    engagement: Dict[str, int]  # likes, retweets, comments, etc.
    sentiment: str = "neutral"
    relevance_score: float = 0.5
    tags: List[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class Config:
    """Configuration loader."""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or str(Path(__file__).parent / "config.json")
        self._config = self._load()
    
    def _load(self) -> Dict:
        """Load config from JSON."""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return self._default_config()
    
    def _default_config(self) -> Dict:
        """Default configuration."""
        return {
            "sources": {
                "twitter": {"enabled": False, "accounts": [], "keywords": [], "max_results": 50},
                "reddit": {"enabled": False, "subreddits": [], "max_posts": 20},
                "hacker_news": {"enabled": False, "keywords": [], "max_stories": 15},
                "onchain": {"enabled": False, "dexscreener": True, "birdeye": True, "whale_tracker": True}
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by dot-notation key."""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def is_enabled(self, source: str) -> bool:
        """Check if source is enabled."""
        return self.get(f"sources.{source}.enabled", False)


# ============================================
# TWITTER GATHERING
# ============================================

async def gather_twitter(
    config: Config,
    keywords: List[str] = None,
    accounts: List[str] = None,
    max_results: int = 50
) -> List[IntelligenceSignal]:
    """
    Gather intelligence from Twitter/X.
    
    Args:
        config: Configuration object
        keywords: Keywords to search
        accounts: Accounts to monitor
        max_results: Max results per query
        
    Returns:
        List of IntelligenceSignal objects
    """
    if not config.is_enabled("twitter"):
        logger.info("Twitter source disabled, skipping")
        return []
    
    signals = []
    keywords = keywords or config.get("sources.twitter.keywords", [])
    accounts = accounts or config.get("sources.twitter.accounts", [])
    
    # Check for API credentials
    api_key = os.getenv("TWITTER_API_KEY")
    if not api_key:
        logger.warning("TWITTER_API_KEY not set, using mock data")
        return _mock_twitter_signals(keywords, accounts, max_results)
    
    # For now, return mock data (real implementation would use tweepy)
    logger.info(f"Twitter gathering: {len(keywords)} keywords, {len(accounts)} accounts")
    
    # Simulated gathering (replace with actual tweepy implementation)
    signals.extend(_mock_twitter_signals(keywords, accounts, max_results))
    
    return signals


def _mock_twitter_signals(
    keywords: List[str],
    accounts: List[str],
    max_results: int
) -> List[IntelligenceSignal]:
    """Generate mock Twitter signals for testing."""
    signals = []
    now = datetime.now().isoformat()
    
    # Sample tweets based on keywords
    sample_tweets = [
        {
            "author": "@CryptoHayes",
            "content": "L2 adoption is accelerating faster than expected. Starknet ecosystem growing rapidly.",
            "url": "https://x.com/CryptoHayes/status/12345",
            "engagement": {"likes": 234, "retweets": 45, "replies": 12}
        },
        {
            "author": "@Starknet",
            "content": "New governance proposal is now live for community voting. Your voice matters.",
            "url": "https://x.com/Starknet/status/12346",
            "engagement": {"likes": 567, "retweets": 89, "replies": 34}
        },
        {
            "author": "@VitalikButerin",
            "content": "Exciting to see zero-knowledge proofs enabling new scaling solutions.",
            "url": "https://x.com/VitalikButerin/status/12347",
            "engagement": {"likes": 1200, "retweets": 200, "replies": 67}
        }
    ]
    
    for i, tweet in enumerate(sample_tweets):
        signals.append(IntelligenceSignal(
            id=f"tw_{i}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            source="twitter",
            type="tweet",
            title=f"Tweet by {tweet['author']}",
            content=tweet['content'],
            url=tweet['url'],
            author=tweet['author'],
            timestamp=now,
            engagement=tweet['engagement'],
            sentiment="bullish",
            relevance_score=0.85,
            tags=keywords[:2]
        ))
    
    return signals


# ============================================
# REDDIT GATHERING
# ============================================

async def gather_reddit(
    config: Config,
    subreddits: List[str] = None,
    keywords: List[str] = None,
    max_posts: int = 20
) -> List[IntelligenceSignal]:
    """
    Gather intelligence from Reddit.
    
    Args:
        config: Configuration object
        subreddits: Subreddits to monitor
        keywords: Keywords to search
        max_posts: Max posts per subreddit
        
    Returns:
        List of IntelligenceSignal objects
    """
    if not config.is_enabled("reddit"):
        logger.info("Reddit source disabled, skipping")
        return []
    
    signals = []
    subreddits = subreddits or config.get("sources.reddit.subreddits", [])
    
    # Check for API credentials
    client_id = os.getenv("REDDIT_CLIENT_ID")
    if not client_id:
        logger.warning("REDDIT_CLIENT_ID not set, using mock data")
        return _mock_reddit_signals(subreddits, keywords, max_posts)
    
    # Simulated gathering (replace with praw implementation)
    signals.extend(_mock_reddit_signals(subreddits, keywords, max_posts))
    
    return signals


def _mock_reddit_signals(
    subreddits: List[str],
    keywords: List[str],
    max_posts: int
) -> List[IntelligenceSignal]:
    """Generate mock Reddit signals for testing."""
    signals = []
    now = datetime.now().isoformat()
    
    sample_posts = [
        {
            "author": "u/crypto_trader_123",
            "subreddit": "ethfinance",
            "title": "Starknet governance proposal discussion",
            "content": "The new governance proposal is interesting. It addresses several key concerns...",
            "url": "https://reddit.com/r/ethfinance/comments/12345",
            "score": 156,
            "comments": 45
        },
        {
            "author": "u/starknet_fan",
            "subreddit": "Starknet",
            "title": "New defi protocol launching on Starknet",
            "content": "Just discovered this new dex protocol. Low fees and fast transactions!",
            "url": "https://reddit.com/r/Starknet/comments/12346",
            "score": 89,
            "comments": 23
        }
    ]
    
    for i, post in enumerate(sample_posts):
        signals.append(IntelligenceSignal(
            id=f"rd_{i}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            source="reddit",
            type="post",
            title=post['title'],
            content=post['content'],
            url=post['url'],
            author=post['author'],
            timestamp=now,
            engagement={"score": post['score'], "comments": post['comments']},
            sentiment="neutral",
            relevance_score=0.78,
            tags=keywords[:2]
        ))
    
    return signals


# ============================================
# HACKER NEWS GATHERING
# ============================================

async def gather_hacker_news(
    config: Config,
    keywords: List[str] = None,
    max_stories: int = 15
) -> List[IntelligenceSignal]:
    """
    Gather intelligence from Hacker News.
    
    Args:
        config: Configuration object
        keywords: Keywords to search
        max_stories: Max stories to return
        
    Returns:
        List of IntelligenceSignal objects
    """
    if not config.is_enabled("hacker_news"):
        logger.info("Hacker News source disabled, skipping")
        return []
    
    signals = []
    keywords = keywords or config.get("sources.hacker_news.keywords", [])
    
    try:
        async with aiohttp.ClientSession() as session:
            # Fetch top stories
            async with session.get("https://hacker-news.firebaseio.com/v0/topstories.json") as resp:
                story_ids = (await resp.json())[:max_stories]
            
            for story_id in story_ids:
                async with session.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json") as resp:
                    story = await resp.json()
                    
                    if story and story.get('url'):
                        # Check if story matches keywords
                        title_lower = story.get('title', '').lower()
                        if any(kw.lower() in title_lower for kw in keywords):
                            signals.append(IntelligenceSignal(
                                id=f"hn_{story_id}",
                                source="hacker_news",
                                type="story",
                                title=story['title'],
                                content=story.get('text', '')[:500] if story.get('text') else story['title'],
                                url=story['url'],
                                author=story.get('by', 'unknown'),
                                timestamp=datetime.fromtimestamp(story.get('time', 0)).isoformat(),
                                engagement={"score": story.get('score', 0), "descendants": story.get('descendants', 0)},
                                relevance_score=_calculate_hn_relevance(story, keywords),
                                tags=[kw for kw in keywords if kw.lower() in title_lower]
                            ))
    except Exception as e:
        logger.error(f"HN gathering error: {e}")
        # Fall back to mock data
        signals.extend(_mock_hn_signals(keywords, max_stories))
    
    return signals


def _mock_hn_signals(
    keywords: List[str],
    max_stories: int
) -> List[IntelligenceSignal]:
    """Generate mock HN signals for testing."""
    signals = []
    now = datetime.now().isoformat()
    
    sample_stories = [
        {
            "title": "Starknet's Approach to MEV Protection",
            "url": "https://example.com/starknet-mev",
            "author": "cryptographer",
            "score": 245,
            "descendants": 67
        },
        {
            "title": "Understanding Cairo: A Language for Proving",
            "url": "https://example.com/cairo-guide",
            "author": "starkware_insider",
            "score": 189,
            "descendants": 34
        }
    ]
    
    for i, story in enumerate(sample_stories):
        signals.append(IntelligenceSignal(
            id=f"hn_mock_{i}",
            source="hacker_news",
            type="story",
            title=story['title'],
            content=story['title'],
            url=story['url'],
            author=story['author'],
            timestamp=now,
            engagement={"score": story['score'], "descendants": story['descendants']},
            relevance_score=0.82,
            tags=keywords[:1]
        ))
    
    return signals


def _calculate_hn_relevance(story: Dict, keywords: List[str]) -> float:
    """Calculate relevance score for HN story."""
    title = story.get('title', '').lower()
    score = story.get('score', 0)
    
    # Base score from keyword matches
    kw_matches = sum(1 for kw in keywords if kw.lower() in title)
    base_score = min(kw_matches * 0.25, 0.75)
    
    # Boost from engagement
    engagement_boost = min(score / 500, 0.25)
    
    return min(base_score + engagement_boost, 1.0)


# ============================================
# ON-CHAIN GATHERING
# ============================================

async def gather_onchain(
    config: Config,
    dexscreener: bool = True,
    birdeye: bool = True,
    whale_tracker: bool = True
) -> List[IntelligenceSignal]:
    """
    Gather on-chain intelligence.
    
    Args:
        config: Configuration object
        dexscreener: Include DEX screener data
        birdeye: Include Birdeye data
        whale_tracker: Include whale tracker data
        
    Returns:
        List of IntelligenceSignal objects
    """
    if not config.get("sources.onchain.enabled", False):
        logger.info("On-chain source disabled, skipping")
        return []
    
    signals = []
    
    # Gather from each enabled source
    if dexscreener and config.get("sources.onchain.dexscreener.enabled", False):
        signals.extend(await _gather_dexscreener(config))
    
    if birdeye and config.get("sources.onchain.birdeye.enabled", False):
        signals.extend(await _gather_birdeye(config))
    
    if whale_tracker and config.get("sources.onchain.whale_tracker.enabled", False):
        signals.extend(await _gather_whale_tracker(config))
    
    return signals


async def _gather_dexscreener(config: Config) -> List[IntelligenceSignal]:
    """Gather data from DEX Screener."""
    signals = []
    chains = config.get("sources.onchain.dexscreener.chains", ["starknet"])
    max_pools = config.get("sources.onchain.dexscreener.max_pools", 20)
    
    try:
        async with aiohttp.ClientSession() as session:
            for chain in chains:
                url = f"https://api.dexscreener.com/latest/dex/pairs/{chain}"
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        pairs = data.get('pairs', [])[:max_pools]
                        
                        for pair in pairs:
                            # Check for unusual activity
                            price_change = pair.get('priceChange', {}).get('h24', 0)
                            if abs(price_change) > 20:  # Significant move
                                signals.append(IntelligenceSignal(
                                    id=f"dex_{pair['pairAddress'][:8]}",
                                    source="dexscreener",
                                    type="pair",
                                    title=f"{pair['baseToken']['symbol']}/{pair['quoteToken']['symbol']}",
                                    content=f"24h change: {price_change:+.2f}% | TVL: ${pair.get('liquidity', {}).get('usd', 0):,.0f}",
                                    url=f"https://dexscreener.com/{chain}/{pair['pairAddress']}",
                                    author="system",
                                    timestamp=datetime.now().isoformat(),
                                    engagement={"liquidity": pair.get('liquidity', {}).get('usd', 0)},
                                    relevance_score=0.75 if abs(price_change) > 50 else 0.6,
                                    tags=[chain, "dex"]
                                ))
    except Exception as e:
        logger.error(f"DEX Screener error: {e}")
    
    return signals


async def _gather_birdeye(config: Config) -> List[IntelligenceSignal]:
    """Gather data from Birdeye."""
    # Birdeye API requires key, use mock for now
    logger.info("Birdeye gathering (placeholder)")
    return []


async def _gather_whale_tracker(config: Config) -> List[IntelligenceSignal]:
    """
    Gather from whale tracker database.
    
    Integrates with starknet-whale-tracker skill.
    """
    signals = []
    
    db_path = config.get("sources.onchain.whale_tracker.db_path", 
                        "../starknet-whale-tracker/data/whales.db")
    min_value = config.get("sources.onchain.whale_tracker.min_value_strk", 10000)
    hours = config.get("sources.onchain.whale_tracker.activity_hours", 24)
    
    # Try to connect to whale tracker database
    full_db_path = Path(__file__).parent.parent / db_path
    
    if not full_db_path.exists():
        logger.warning(f"Whale tracker DB not found: {full_db_path}")
        # Return mock whale data
        return _mock_whale_signals()
    
    try:
        import sqlite3
        
        conn = sqlite3.connect(str(full_db_path))
        cursor = conn.cursor()
        
        # Get recent activity
        cursor.execute("""
            SELECT a.*, w.tags, w.notes
            FROM activity a
            JOIN whales w ON a.wallet_address = w.address
            WHERE a.timestamp >= datetime('now', '-' || ? || ' hours')
            ORDER BY a.timestamp DESC
            LIMIT 50
        """, (hours,))
        
        rows = cursor.fetchall()
        conn.close()
        
        for row in rows:
            activity_id, wallet, event_type, details, block, timestamp, tx_hash, tags, notes = row
            details_dict = json.loads(details) if details else {}
            
            signals.append(IntelligenceSignal(
                id=f"whale_{activity_id}",
                source="whale_tracker",
                type=event_type,
                title=f"Whale Activity: {event_type}",
                content=notes or f"{event_type} - {details_dict.get('value', 'N/A')}",
                url=f"https://voyager.online/tx/{tx_hash}" if tx_hash else "",
                author=wallet[:16] + "...",
                timestamp=timestamp,
                engagement={"block": block},
                relevance_score=0.85 if "large" in event_type else 0.7,
                tags=json.loads(tags) if tags else ["whale"]
            ))
            
    except Exception as e:
        logger.error(f"Whale tracker error: {e}")
        signals.extend(_mock_whale_signals())
    
    return signals


def _mock_whale_signals() -> List[IntelligenceSignal]:
    """Generate mock whale signals."""
    signals = []
    now = datetime.now().isoformat()
    
    whale_activities = [
        {
            "address": "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004d7",
            "event_type": "large_transfer",
            "notes": "Starknet Foundation wallet",
            "value": "50,000 STRK"
        },
        {
            "address": "0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d",
            "event_type": "new_position",
            "notes": "STRK Token Contract",
            "value": "100,000 STRK"
        }
    ]
    
    for i, activity in enumerate(whale_activities):
        signals.append(IntelligenceSignal(
            id=f"whale_mock_{i}",
            source="whale_tracker",
            type=activity['event_type'],
            title=f"Whale Activity: {activity['event_type']}",
            content=f"{activity['notes']} - {activity['value']}",
            url="",
            author=activity['address'][:16] + "...",
            timestamp=now,
            engagement={"value_strk": activity['value']},
            relevance_score=0.88,
            tags=["whale", activity['event_type']]
        ))
    
    return signals


# ============================================
# GATHER ALL
# ============================================

async def gather_all(config: Config = None) -> List[IntelligenceSignal]:
    """
    Gather intelligence from all enabled sources.
    
    Args:
        config: Optional configuration object
        
    Returns:
        Combined list of IntelligenceSignal objects
    """
    if config is None:
        config = Config()
    
    logger.info("Starting intelligence gathering from all sources...")
    
    # Gather from all sources concurrently
    tasks = []
    
    if config.is_enabled("twitter"):
        tasks.append(gather_twitter(config))
    
    if config.is_enabled("reddit"):
        tasks.append(gather_reddit(config))
    
    if config.is_enabled("hacker_news"):
        tasks.append(gather_hacker_news(config))
    
    if config.get("sources.onchain.enabled", False):
        tasks.append(gather_onchain(config))
    
    # Execute all gathering tasks
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Combine results
    all_signals = []
    for result in results:
        if isinstance(result, list):
            all_signals.extend(result)
        elif isinstance(result, Exception):
            logger.error(f"Gathering error: {result}")
    
    # Save raw data
    _save_raw_data(all_signals, config)
    
    logger.info(f"Gathering complete: {len(all_signals)} signals collected")
    
    return all_signals


def _save_raw_data(signals: List[IntelligenceSignal], config: Config):
    """Save raw gathered data to file."""
    raw_dir = Path(config.get("output.raw_dir", "data/raw"))
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = raw_dir / f"{timestamp}.json"
    
    data = {
        "timestamp": datetime.now().isoformat(),
        "count": len(signals),
        "signals": [s.to_dict() for s in signals]
    }
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"Saved raw data to: {filepath}")


# ============================================
# CLI
# ============================================

def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Gather intelligence from multiple sources")
    parser.add_argument("--all", action="store_true", help="Gather from all enabled sources")
    parser.add_argument("--twitter", action="store_true", help="Gather from Twitter/X")
    parser.add_argument("--reddit", action="store_true", help="Gather from Reddit")
    parser.add_argument("--hn", action="store_true", help="Gather from Hacker News")
    parser.add_argument("--onchain", action="store_true", help="Gather on-chain data")
    parser.add_argument("--output", "-o", help="Output file path (JSON)")
    
    args = parser.parse_args()
    
    config = Config()
    
    async def run():
        if args.all or not any([args.twitter, args.reddit, args.hn, args.onchain]):
            signals = await gather_all(config)
        else:
            signals = []
            
            if args.twitter:
                signals.extend(await gather_twitter(config))
            if args.reddit:
                signals.extend(await gather_reddit(config))
            if args.hn:
                signals.extend(await gather_hacker_news(config))
            if args.onchain:
                signals.extend(await gather_onchain(config))
        
        # Output
        if args.output:
            with open(args.output, 'w') as f:
                json.dump([s.to_dict() for s in signals], f, indent=2)
            print(f"Saved {len(signals)} signals to {args.output}")
        else:
            print(f"Collected {len(signals)} signals:")
            for s in signals[:10]:
                print(f"  [{s.source}] {s.title[:50]}...")
    
    asyncio.run(run())


if __name__ == "__main__":
    main()
