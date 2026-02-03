"""
Reply Module.

Provides specialized functions for replying to tweets
with context tracking and threading support.
"""

import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from .api import TwitterClient, TwitterAPIError, get_client
from .post import TweetPoster

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReplyManager:
    """Manages tweet replies with context tracking."""
    
    def __init__(self, client: Optional[TwitterClient] = None):
        """Initialize reply manager."""
        self.client = client or get_client()
        self.poster = TweetPoster(self.client)
        self._reply_context_file = "data/reply_context.json"
    
    def get_conversation(
        self,
        tweet_id: str,
        max_depth: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get conversation thread for a tweet.
        
        Args:
            tweet_id: Starting tweet ID
            max_depth: How many levels to fetch
            
        Returns:
            List of tweets in conversation order
        """
        conversation = []
        current_id = tweet_id
        
        try:
            for _ in range(max_depth):
                tweet = self.client.get_tweet(current_id)
                conversation.append({
                    "id": tweet.id,
                    "text": tweet.text,
                    "author_id": tweet.author_id,
                    "created_at": tweet.created_at,
                    "in_reply_to": tweet.referenced_tweets[0] if tweet.referenced_tweets else None
                })
                
                if not tweet.referenced_tweets:
                    break
                
                current_id = tweet.referenced_tweets[0]
            
            return conversation
            
        except TwitterAPIError as e:
            logger.error(f"Failed to get conversation: {e}")
            return []
    
    def reply_with_context(
        self,
        tweet_id: str,
        text: str,
        include_context: bool = True
    ) -> Dict[str, Any]:
        """
        Reply with context awareness.
        
        Args:
            tweet_id: Tweet to reply to
            text: Reply content
            include_context: Whether to add context prefix
            
        Returns:
            Dict with reply info
        """
        try:
            original = self.client.get_tweet(tweet_id)
            
            if include_context:
                # Add context prefix (e.g., "@user ")
                context = f"@{original.author_id} "
                if not text.startswith(context):
                    text = context + text
            
            result = self.poster.reply_to(tweet_id, text)
            
            if result.get("success"):
                # Track reply context
                self._save_reply_context(
                    result["tweet_id"],
                    tweet_id,
                    original.text[:100]
                )
            
            return result
            
        except TwitterAPIError as e:
            logger.error(f"Context reply failed: {e}")
            return {"success": False, "error": e.message}
    
    def reply_thread(
        self,
        tweets: List[Dict[str, str]],
        initial_tweet_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Create a reply thread.
        
        Args:
            tweets: List of reply texts
            initial_tweet_id: First tweet to reply to (optional)
            
        Returns:
            List of result dicts
        """
        results = []
        current_id = initial_tweet_id
        
        for i, tweet_data in enumerate(tweets):
            if current_id:
                result = self.poster.reply_to(
                    current_id,
                    tweet_data["text"],
                    quote_tweet_id=tweet_data.get("quote")
                )
            else:
                result = self.poster.post(tweet_data["text"])
            
            results.append(result)
            
            if result.get("success"):
                current_id = result["tweet_id"]
            else:
                logger.error(f"Thread broken at {i}")
                break
        
        return results
    
    def batch_reply(
        self,
        replies: List[Dict[str, str]],
        delay_seconds: int = 10
    ) -> Dict[str, Any]:
        """
        Reply to multiple tweets.
        
        Args:
            replies: List of {tweet_id, text}
            delay_seconds: Delay between replies
            
        Returns:
            Summary of results
        """
        success = 0
        failed = 0
        
        for reply_data in replies:
            result = self.poster.reply_to(
                reply_data["tweet_id"],
                reply_data["text"]
            )
            
            if result.get("success"):
                success += 1
            else:
                failed += 1
            
            # Rate limit protection
            import time
            time.sleep(delay_seconds)
        
        return {
            "total": len(replies),
            "success": success,
            "failed": failed
        }
    
    def reply_to_user(
        self,
        username: str,
        text: str,
        recent_tweet_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Reply to a user's most recent tweet.
        
        Args:
            username: Twitter username (without @)
            text: Reply content
            recent_tweet_id: Specific tweet ID (optional)
            
        Returns:
            Dict with reply info
        """
        try:
            if not recent_tweet_id:
                user = self.client.get_user_by_username(username)
                tweets = self.client.get_user_tweets(user["data"]["id"], max_results=5)
                
                if not tweets:
                    return {"success": False, "error": "No tweets found"}
                
                recent_tweet_id = tweets[0].id
            
            return self.poster.reply_to(recent_tweet_id, text)
            
        except TwitterAPIError as e:
            logger.error(f"Reply to user failed: {e}")
            return {"success": False, "error": e.message}
    
    def get_mentions(
        self,
        since_id: Optional[str] = None,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get recent mentions.
        
        Args:
            since_id: Only tweets after this ID
            max_results: Max tweets to fetch
            
        Returns:
            List of mention tweets
        """
        try:
            me = self.client.get_me()
            user_id = me["data"]["id"]
            
            params = {"max_results": min(max_results, 100)}
            if since_id:
                params["since_id"] = since_id
            
            data = self.client._request(
                "GET",
                f"/users/{user_id}/mentions",
                params=params
            )
            
            mentions = []
            for tweet_data in data.get("data", []):
                mentions.append({
                    "id": tweet_data["id"],
                    "text": tweet_data["text"],
                    "author_id": tweet_data.get("author_id"),
                    "created_at": tweet_data.get("created_at")
                })
            
            return mentions
            
        except TwitterAPIError as e:
            logger.error(f"Failed to get mentions: {e}")
            return []
    
    def reply_to_mentions(
        self,
        template: str,
        since_id: Optional[str] = None,
        delay_seconds: int = 15
    ) -> Dict[str, Any]:
        """
        Auto-reply to mentions using template.
        
        Args:
            template: Reply template (f-string with {author}, {tweet})
            since_id: Only reply to mentions after this ID
            delay_seconds: Delay between replies
            
        Returns:
            Summary of replies
        """
        mentions = self.get_mentions(since_id)
        success = 0
        failed = 0
        
        for mention in mentions:
            try:
                reply_text = template.format(
                    author=mention["author_id"],
                    tweet=mention["text"][:50]
                )
                
                result = self.poster.reply_to(mention["id"], reply_text)
                
                if result.get("success"):
                    success += 1
                else:
                    failed += 1
                
                import time
                time.sleep(delay_seconds)
                
            except Exception as e:
                logger.error(f"Template reply failed: {e}")
                failed += 1
        
        return {
            "total": len(mentions),
            "success": success,
            "failed": failed
        }
    
    # ============ Context Persistence ============
    
    def _save_reply_context(
        self,
        reply_id: str,
        original_id: str,
        original_preview: str
    ):
        """Save reply context for tracking."""
        import os
        os.makedirs("data", exist_ok=True)
        
        context = {
            "reply_id": reply_id,
            "original_id": original_id,
            "original_preview": original_preview,
            "created_at": datetime.now().isoformat()
        }
        
        with open(self._reply_context_file, "a") as f:
            f.write(json.dumps(context) + "\n")
    
    def get_reply_history(
        self,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get recent reply history."""
        try:
            with open(self._reply_context_file) as f:
                lines = f.readlines()[-limit:]
                return [json.loads(line) for line in lines]
        except FileNotFoundError:
            return []
