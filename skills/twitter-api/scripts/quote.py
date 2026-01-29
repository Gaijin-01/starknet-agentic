"""
Quote Tweet Module.

Provides specialized functions for quoting tweets
with custom comments and analysis.
"""

import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from .api import TwitterClient, TwitterAPIError, get_client
from .post import TweetPoster

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QuoteManager:
    """Manages quote tweets with analytics."""
    
    def __init__(self, client: Optional[TwitterClient] = None):
        """Initialize quote manager."""
        self.client = client or get_client()
        self.poster = TweetPoster(self.client)
        self._quote_history_file = "data/quote_history.json"
    
    def quote(
        self,
        tweet_id: str,
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Quote a tweet with optional comment.
        
        Args:
            tweet_id: Tweet to quote
            comment: Additional comment text
            
        Returns:
            Dict with quote info
        """
        logger.info(f"Quoting tweet: {tweet_id}")
        
        result = self.poster.quote_tweet(tweet_id, comment)
        
        if result.get("success"):
            self._save_quote(result["tweet_id"], tweet_id, comment)
        
        return result
    
    def quote_with_analysis(
        self,
        tweet_id: str,
        analysis: str,
        include_metrics: bool = True
    ) -> Dict[str, Any]:
        """
        Quote with analysis/metrics.
        
        Args:
            tweet_id: Tweet to quote
            analysis: Analysis text to include
            include_metrics: Whether to fetch and include metrics
            
        Returns:
            Dict with quote info
        """
        original = self.client.get_tweet(tweet_id)
        
        metrics_text = ""
        if include_metrics and original.metrics:
            metrics_text = (
                f"📊 {original.metrics.get('retweet_count', 0)} RTs, "
                f"{original.metrics.get('like_count', 0)} likes"
            )
        
        comment = f"{analysis}\n\n{metrics_text}".strip()
        
        return self.quote(tweet_id, comment)
    
    def batch_quote(
        self,
        quotes: List[Dict[str, str]],
        delay_seconds: int = 20
    ) -> Dict[str, Any]:
        """
        Quote multiple tweets.
        
        Args:
            quotes: List of {tweet_id, comment}
            delay_seconds: Delay between quotes
            
        Returns:
            Summary of results
        """
        success = 0
        failed = 0
        
        for quote_data in quotes:
            result = self.quote(
                quote_data["tweet_id"],
                quote_data.get("comment")
            )
            
            if result.get("success"):
                success += 1
            else:
                failed += 1
            
            import time
            time.sleep(delay_seconds)
        
        return {
            "total": len(quotes),
            "success": success,
            "failed": failed
        }
    
    def quote_via_search(
        self,
        query: str,
        comment: str,
        max_results: int = 10,
        delay_seconds: int = 30
    ) -> Dict[str, Any]:
        """
        Search and quote tweets matching query.
        
        Args:
            query: Twitter search query
            comment: Comment to add to quotes
            max_results: Max tweets to quote
            delay_seconds: Delay between quotes
            
        Returns:
            Summary of results
        """
        tweets = self.client.search_recent_tweets(query, max_results=max_results)
        
        success = 0
        failed = 0
        
        for tweet in tweets:
            result = self.quote(tweet.id, comment)
            
            if result.get("success"):
                success += 1
            else:
                failed += 1
            
            import time
            time.sleep(delay_seconds)
        
        return {
            "query": query,
            "total": len(tweets),
            "success": success,
            "failed": failed
        }
    
    def quote_competitor(
        self,
        username: str,
        comment: str,
        max_tweets: int = 5
    ) -> Dict[str, Any]:
        """
        Quote recent tweets from a user.
        
        Args:
            username: Twitter username
            comment: Comment template (can use {tweet_text})
            max_tweets: Max tweets to quote
            
        Returns:
            Summary of results
        """
        try:
            user = self.client.get_user_by_username(username)
            tweets = self.client.get_user_tweets(user["data"]["id"], max_results=max_tweets)
            
            success = 0
            failed = 0
            
            for tweet in tweets:
                formatted_comment = comment.format(
                    tweet_text=tweet.text[:100],
                    tweet_id=tweet.id,
                    author=username
                )
                
                result = self.quote(tweet.id, formatted_comment)
                
                if result.get("success"):
                    success += 1
                else:
                    failed += 1
                
                import time
                time.sleep(20)
            
            return {
                "user": username,
                "total": len(tweets),
                "success": success,
                "failed": failed
            }
            
        except TwitterAPIError as e:
            logger.error(f"Competitor quote failed: {e}")
            return {"success": False, "error": e.message}
    
    def quote_trending(
        self,
        comment: str,
        max_quotes: int = 5,
        delay_seconds: int = 30
    ) -> Dict[str, Any]:
        """
        Quote trending tweets.
        
        Note: Twitter API v2 doesn't expose trending directly.
        This uses search as a workaround.
        
        Args:
            comment: Comment for quotes
            max_quotes: Max quotes to make
            delay_seconds: Delay between quotes
            
        Returns:
            Summary of results
        """
        # Search for trending-like content
        queries = [
            "#trending",
            "#viral",
            "breaking",
        ]
        
        success = 0
        failed = 0
        total_quoted = 0
        
        for query in queries:
            if total_quoted >= max_quotes:
                break
            
            tweets = self.client.search_recent_tweets(
                query,
                max_results=min(max_quotes - total_quoted, 10)
            )
            
            for tweet in tweets:
                if total_quoted >= max_quotes:
                    break
                
                result = self.quote(tweet.id, comment)
                
                if result.get("success"):
                    success += 1
                else:
                    failed += 1
                
                total_quoted += 1
                import time
                time.sleep(delay_seconds)
        
        return {
            "total": total_quoted,
            "success": success,
            "failed": failed
        }
    
    # ============ Analytics ============
    
    def get_quote_analytics(
        self,
        tweet_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get analytics for quotes.
        
        Args:
            tweet_id: Specific tweet ID (optional)
            
        Returns:
            Analytics summary
        """
        history = self._get_quote_history()
        
        if tweet_id:
            history = [h for h in history if h.get("quoted_id") == tweet_id]
        
        total = len(history)
        if total == 0:
            return {"total": 0, "avg_likes": 0, "avg_rts": 0}
        
        return {
            "total": total,
            "with_comments": sum(1 for h in history if h.get("comment")),
            "without_comments": sum(1 for h in history if not h.get("comment")),
            "recent": history[-10:]
        }
    
    def _save_quote(
        self,
        quote_id: str,
        quoted_id: str,
        comment: Optional[str]
    ):
        """Save quote to history."""
        import os
        os.makedirs("data", exist_ok=True)
        
        entry = {
            "quote_id": quote_id,
            "quoted_id": quoted_id,
            "comment": comment,
            "created_at": datetime.now().isoformat()
        }
        
        with open(self._quote_history_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def _get_quote_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get quote history."""
        try:
            with open(self._quote_history_file) as f:
                lines = f.readlines()[-limit:]
                return [json.loads(line) for line in lines]
        except FileNotFoundError:
            return []
    
    def export_quote_history(
        self,
        format: str = "json"
    ) -> str:
        """
        Export quote history.
        
        Args:
            format: "json" or "csv"
            
        Returns:
            Export as string
        """
        history = self._get_quote_history(limit=10000)
        
        if format == "csv":
            lines = ["quote_id,quoted_id,comment,created_at"]
            for h in history:
                lines.append(
                    f"{h['quote_id']},{h['quoted_id']},"
                    f"\"{h.get('comment', '').replace('\"', '\"\"')}\","
                    f"{h['created_at']}"
                )
            return "\n".join(lines)
        
        return json.dumps(history, indent=2)
