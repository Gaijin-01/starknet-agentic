"""
Competitor Tracking Module.

Monitors competitor accounts, tracks their content,
and analyzes their performance metrics.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict

import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CompetitorProfile:
    """Profile for a tracked competitor."""
    username: str
    display_name: str
    bio: str
    followers: int
    following: int
    tweets: int
    verified: bool
    created_at: str
    last_tweet_at: Optional[datetime] = None
    engagement_rate: float = 0.0
    avg_likes: float = 0.0
    avg_retweets: float = 0.0
    top_topics: List[str] = field(default_factory=list)


@dataclass
class CompetitorTweet:
    """Tweet from a competitor."""
    id: str
    text: str
    created_at: datetime
    likes: int
    retweets: int
    replies: int
    quote_tweets: int
    url: str
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)


class CompetitorTracker:
    """Tracks competitor accounts and their content."""
    
    def __init__(
        self,
        twitter_api_key: Optional[str] = None,
        data_dir: str = "data"
    ):
        """
        Initialize competitor tracker.
        
        Args:
            twitter_api_key: Twitter API bearer token
            data_dir: Directory for storing competitor data
        """
        self.api_key = twitter_api_key or os.getenv("TWITTER_BEARER_TOKEN")
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Competitor registry
        self._competitors: Dict[str, CompetitorProfile] = {}
        self._load_competitors()
    
    async def close(self):
        """Close async client."""
        await self.client.aclose()
    
    # ============ Competitor Management ============
    
    def add_competitor(self, username: str, track: bool = True):
        """
        Add a competitor to track.
        
        Args:
            username: Twitter username (without @)
            track: Whether to start tracking immediately
        """
        if username not in self._competitors:
            self._competitors[username] = None  # Will be populated on update
            self._save_competitors()
            logger.info(f"Added competitor: {username}")
            
            if track:
                import asyncio
                asyncio.create_task(self.update_competitor(username))
    
    def remove_competitor(self, username: str):
        """Remove a competitor from tracking."""
        if username in self._competitors:
            del self._competitors[username]
            self._save_competitors()
            logger.info(f"Removed competitor: {username}")
    
    def list_competitors(self) -> List[str]:
        """List all tracked competitors."""
        return list(self._competitors.keys())
    
    # ============ Profile Updates ============
    
    async def update_competitor(self, username: str) -> Optional[CompetitorProfile]:
        """
        Update competitor profile and recent tweets.
        
        Args:
            username: Twitter username
            
        Returns:
            Updated CompetitorProfile
        """
        try:
            # Get user info
            user_data = await self._get_user_by_username(username)
            if not user_data:
                logger.warning(f"User not found: {username}")
                return None
            
            profile = self._parse_user_data(user_data)
            
            # Get recent tweets for engagement metrics
            tweets = await self._get_user_tweets(user_data["id"], limit=50)
            if tweets:
                self._calculate_engagement(profile, tweets)
                profile.top_topics = self._extract_topics(tweets)
            
            self._competitors[username] = profile
            self._save_competitors()
            
            logger.info(f"Updated competitor: {username}")
            return profile
            
        except Exception as e:
            logger.error(f"Failed to update {username}: {e}")
            return None
    
    async def update_all_competitors(self) -> Dict[str, CompetitorProfile]:
        """
        Update all tracked competitors.
        
        Returns:
            Dict of username -> CompetitorProfile
        """
        updated = {}
        
        for username in self._competitors:
            profile = await self.update_competitor(username)
            if profile:
                updated[username] = profile
        
        return updated
    
    # ============ Content Analysis ============
    
    async def get_competitor_tweets(
        self,
        username: str,
        limit: int = 50,
        since_days: int = 7
    ) -> List[CompetitorTweet]:
        """
        Get recent tweets from a competitor.
        
        Args:
            username: Twitter username
            limit: Max tweets
            since_days: Only tweets from last N days
            
        Returns:
            List of CompetitorTweet
        """
        try:
            user_data = await self._get_user_by_username(username)
            if not user_data:
                return []
            
            return await self._get_user_tweets(user_data["id"], limit)
            
        except Exception as e:
            logger.error(f"Failed to get tweets from {username}: {e}")
            return []
    
    async def compare_engagement(
        self,
        usernames: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Compare engagement metrics across competitors.
        
        Args:
            usernames: Competitors to compare (all if None)
            
        Returns:
            Comparison analysis
        """
        competitors = usernames or self.list_competitors()
        
        comparison = {
            "timestamp": datetime.now().isoformat(),
            "competitors": {},
            "rankings": {}
        }
        
        for username in competitors:
            profile = self._competitors.get(username)
            if profile:
                comparison["competitors"][username] = {
                    "followers": profile.followers,
                    "engagement_rate": profile.engagement_rate,
                    "avg_likes": profile.avg_likes,
                    "avg_retweets": profile.avg_retweets,
                    "tweets_per_day": profile.tweets / max(1, (datetime.now() - datetime.strptime(profile.created_at, "%Y-%m-%dT%H:%M:%S.%fZ")).days)
                }
        
        # Rankings
        if comparison["competitors"]:
            by_engagement = sorted(
                comparison["competitors"].items(),
                key=lambda x: x[1]["engagement_rate"],
                reverse=True
            )
            by_followers = sorted(
                comparison["competitors"].items(),
                key=lambda x: x[1]["followers"],
                reverse=True
            )
            
            comparison["rankings"] = {
                "by_engagement": [c[0] for c in by_engagement],
                "by_followers": [c[0] for c in by_followers]
            }
        
        return comparison
    
    async def get_content_strategy(
        self,
        username: str
    ) -> Dict[str, Any]:
        """
        Analyze a competitor's content strategy.
        
        Args:
            username: Twitter username
            
        Returns:
            Content strategy analysis
        """
        tweets = await self.get_competitor_tweets(username, limit=100)
        
        if not tweets:
            return {"error": "No tweets available"}
        
        # Analyze posting patterns
        hours = [t.created_at.hour for t in tweets]
        days = [t.created_at.weekday() for t in tweets]
        
        hour_counts = defaultdict(int)
        day_counts = defaultdict(int)
        for h in hours:
            hour_counts[h] += 1
        for d in days:
            day_counts[d] += 1
        
        best_hour = max(hour_counts, key=hour_counts.get)
        best_day = max(day_counts, key=day_counts.get)
        
        # Content analysis
        avg_length = sum(len(t.text) for t in tweets) / len(tweets)
        has_media = sum(1 for t in tweets if t.url) / len(tweets)
        has_hashtags = sum(1 for t in tweets if t.hashtags) / len(tweets)
        
        # Top tweets
        top_by_likes = sorted(tweets, key=lambda t: t.likes, reverse=True)[:5]
        top_by_rts = sorted(tweets, key=lambda t: t.retweets, reverse=True)[:5]
        
        return {
            "username": username,
            "posting_pattern": {
                "best_hour": best_hour,
                "best_day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][best_day],
                "avg_tweets_per_day": len(tweets) / 7
            },
            "content_format": {
                "avg_length": avg_length,
                "media_percentage": has_media * 100,
                "hashtag_percentage": has_hashtags * 100
            },
            "top_performing": {
                "by_likes": [{"text": t.text[:100], "likes": t.likes} for t in top_by_likes],
                "by_retweets": [{"text": t.text[:100], "retweets": t.retweets} for t in top_by_rts]
            }
        }
    
    async def detect_competitor_movements(
        self,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Detect recent competitor activities.
        
        Args:
            hours: Lookback period
            
        Returns:
            List of detected movements
        """
        movements = []
        cutoff = datetime.now() - timedelta(hours=hours)
        
        for username in self._competitors:
            tweets = await self.get_competitor_tweets(username, limit=20)
            
            for tweet in tweets:
                if tweet.created_at < cutoff:
                    continue
                
                # Detect significant activity
                if tweet.likes > 100 or tweet.retweets > 50:
                    movements.append({
                        "username": username,
                        "type": "viral_tweet",
                        "tweet_id": tweet.id,
                        "text": tweet.text[:100],
                        "engagement": {
                            "likes": tweet.likes,
                            "retweets": tweet.retweets,
                            "replies": tweet.replies
                        },
                        "created_at": tweet.created_at.isoformat()
                    })
        
        # Sort by total engagement
        movements.sort(
            key=lambda m: m["engagement"]["likes"] + m["engagement"]["retweets"],
            reverse=True
        )
        
        return movements
    
    # ============ Helper Methods ============
    
    async def _get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user data by username."""
        if not self.api_key:
            logger.warning("No Twitter API key configured")
            return None
        
        url = f"https://api.twitter.com/2/users/by/username/{username}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        response = await self.client.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json().get("data")
        return None
    
    async def _get_user_tweets(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[CompetitorTweet]:
        """Get tweets from a user."""
        if not self.api_key:
            return []
        
        url = f"https://api.twitter.com/2/users/{user_id}/tweets"
        params = {"max_results": min(limit, 100)}
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        response = await self.client.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            tweets = []
            
            for t in data.get("data", []):
                tweet = CompetitorTweet(
                    id=t["id"],
                    text=t["text"],
                    created_at=datetime.fromisoformat(
                        t.get("created_at", datetime.now().isoformat())
                    ),
                    likes=t.get("public_metrics", {}).get("like_count", 0),
                    retweets=t.get("public_metrics", {}).get("retweet_count", 0),
                    replies=t.get("public_metrics", {}).get("reply_count", 0),
                    quote_tweets=t.get("public_metrics", {}).get("quote_count", 0),
                    url=f"https://twitter.com/i/status/{t['id']}",
                    hashtags=self._extract_hashtags(t["text"]),
                    mentions=self._extract_mentions(t["text"])
                )
                tweets.append(tweet)
            
            return tweets
        
        return []
    
    def _parse_user_data(self, data: Dict) -> CompetitorProfile:
        """Parse Twitter user data to CompetitorProfile."""
        return CompetitorProfile(
            username=data.get("username", ""),
            display_name=data.get("name", ""),
            bio=data.get("description", ""),
            followers=data.get("public_metrics", {}).get("followers_count", 0),
            following=data.get("public_metrics", {}).get("following_count", 0),
            tweets=data.get("public_metrics", {}).get("tweet_count", 0),
            verified=data.get("verified", False),
            created_at=data.get("created_at", ""),
            last_tweet_at=None
        )
    
    def _calculate_engagement(self, profile: CompetitorProfile, tweets: List[CompetitorTweet]):
        """Calculate engagement metrics from tweets."""
        if not tweets:
            return
        
        total_likes = sum(t.likes for t in tweets)
        total_rts = sum(t.retweets for t in tweets)
        total_replies = sum(t.replies for t in tweets)
        total_engagement = total_likes + total_rts + total_replies
        
        profile.avg_likes = total_likes / len(tweets)
        profile.avg_retweets = total_rts / len(tweets)
        
        if profile.followers > 0:
            profile.engagement_rate = (total_engagement / len(tweets) / profile.followers) * 100
    
    def _extract_topics(self, tweets: List[CompetitorTweet]) -> List[str]:
        """Extract common topics from tweets."""
        all_hashtags = []
        for tweet in tweets:
            all_hashtags.extend(tweet.hashtags)
        
        # Count hashtag frequency
        from collections import Counter
        tag_counts = Counter(all_hashtags)
        
        return [tag for tag, count in tag_counts.most_common(10)]
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text."""
        import re
        return re.findall(r"#(\w+)", text)
    
    def _extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from text."""
        import re
        return re.findall(r"@(\w+)", text)
    
    # ============ Data Persistence ============
    
    def _load_competitors(self):
        """Load tracked competitors from file."""
        path = os.path.join(self.data_dir, "competitors.json")
        if os.path.exists(path):
            try:
                with open(path) as f:
                    data = json.load(f)
                    for username in data:
                        self._competitors[username] = None
            except Exception as e:
                logger.error(f"Failed to load competitors: {e}")
    
    def _save_competitors(self):
        """Save tracked competitors to file."""
        path = os.path.join(self.data_dir, "competitors.json")
        with open(path, "w") as f:
            json.dump(list(self._competitors.keys()), f)


# Synchronous wrapper
class SyncCompetitorTracker:
    """Synchronous wrapper for CompetitorTracker."""
    
    def __init__(self, api_key: str = None, data_dir: str = "data"):
        self._async = CompetitorTracker(twitter_api_key=api_key, data_dir=data_dir)
    
    def add_competitor(self, username: str, track: bool = True):
        """Add competitor."""
        self._async.add_competitor(username, track)
    
    def list_competitors(self):
        """List competitors."""
        return self._async.list_competitors()
    
    def compare_engagement(self, usernames: List[str] = None):
        """Compare engagement."""
        return asyncio.run(self._async.compare_engagement(usernames))
    
    def get_content_strategy(self, username: str):
        """Get content strategy."""
        return asyncio.run(self._async.get_content_strategy(username))
    
    def detect_movements(self, hours: int = 24):
        """Detect movements."""
        return asyncio.run(self._async.detect_competitor_movements(hours))
    
    def close(self):
        """Close async resources."""
        asyncio.run(self._async.close())
