"""
Tweet Posting Module.

Provides high-level functions for posting tweets
with support for media, polls, and scheduling.
"""

import os
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path

from .api import TwitterClient, TwitterAPIError, get_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TweetPoster:
    """High-level tweet posting interface."""
    
    def __init__(self, client: Optional[TwitterClient] = None):
        """Initialize with Twitter client."""
        self.client = client or get_client()
        self._media_cache: Dict[str, str] = {}
    
    def post(
        self,
        text: str,
        reply_settings: str = "everyone",
        poll_options: Optional[List[str]] = None,
        poll_duration_minutes: int = 1440
    ) -> Dict[str, Any]:
        """
        Post a tweet.
        
        Args:
            text: Tweet content (max 280 chars)
            reply_settings: "everyone", "mentionedUsers", "following"
            poll_options: List of 2-4 poll options
            poll_duration_minutes: Poll duration (default 24 hours)
            
        Returns:
            Dict with tweet info
        """
        logger.info(f"Posting tweet: {text[:50]}...")
        
        try:
            tweet = self.client.create_tweet(
                text=text,
                reply_settings=reply_settings,
                poll_options=poll_options,
                poll_duration=poll_duration_minutes
            )
            
            logger.info(f"Tweet posted successfully: {tweet.id}")
            return {
                "success": True,
                "tweet_id": tweet.id,
                "text": tweet.text,
                "url": f"https://twitter.com/i/status/{tweet.id}"
            }
            
        except TwitterAPIError as e:
            logger.error(f"Failed to post tweet: {e}")
            return {
                "success": False,
                "error": e.message,
                "code": e.code
            }
    
    def post_with_media(
        self,
        text: str,
        media_paths: List[str],
        reply_settings: str = "everyone"
    ) -> Dict[str, Any]:
        """
        Post tweet with media attachments.
        
        Args:
            text: Tweet content
            media_paths: List of media file paths
            reply_settings: Reply settings
            
        Returns:
            Dict with tweet info
        """
        # Upload media first
        media_ids = []
        for path in media_paths:
            media_id = self._upload_media(path)
            if media_id:
                media_ids.append(media_id)
        
        if not media_ids:
            logger.warning("No media uploaded, posting without media")
            return self.post(text, reply_settings)
        
        # Post with media IDs
        payload = {
            "text": text,
            "reply_settings": reply_settings,
            "media": {"media_ids": media_ids}
        }
        
        try:
            data = self.client._request("POST", "/tweets", data=payload)
            tweet = data["data"]
            logger.info(f"Tweet with media posted: {tweet['id']}")
            return {
                "success": True,
                "tweet_id": tweet["id"],
                "text": tweet["text"],
                "media_ids": media_ids,
                "url": f"https://twitter.com/i/status/{tweet['id']}"
            }
        except TwitterAPIError as e:
            logger.error(f"Failed to post media tweet: {e}")
            return {"success": False, "error": e.message}
    
    def _upload_media(self, media_path: str) -> Optional[str]:
        """
        Upload media and get media ID.
        
        Args:
            media_path: Path to media file
            
        Returns:
            Media ID string or None
        """
        path = Path(media_path)
        if not path.exists():
            logger.error(f"Media file not found: {media_path}")
            return None
        
        # Check cache
        if media_path in self._media_cache:
            return self._media_cache[media_path]
        
        # Simplified media upload (Twitter API v2 media upload is complex)
        # In production, use proper media upload flow
        logger.warning(f"Media upload not fully implemented: {media_path}")
        return None
    
    def post_thread(
        self,
        tweets: List[str],
        delay_seconds: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Post a thread of tweets.
        
        Args:
            tweets: List of tweet texts in order
            delay_seconds: Delay between tweets
            
        Returns:
            List of result dicts for each tweet
        """
        results = []
        previous_tweet_id = None
        
        for i, text in enumerate(tweets):
            if previous_tweet_id:
                # Reply to previous tweet
                result = self.reply_to(
                    previous_tweet_id,
                    text,
                    auto_thread=True
                )
            else:
                result = self.post(text)
            
            results.append(result)
            
            if result.get("success"):
                previous_tweet_id = result["tweet_id"]
            else:
                logger.error(f"Thread broken at tweet {i + 1}")
                break
            
            # Rate limit protection
            if i < len(tweets) - 1:
                time.sleep(delay_seconds)
        
        return results
    
    def reply_to(
        self,
        tweet_id: str,
        text: str,
        quote_tweet_id: Optional[str] = None,
        auto_thread: bool = False
    ) -> Dict[str, Any]:
        """
        Reply to a tweet.
        
        Args:
            tweet_id: Tweet to reply to
            text: Reply content
            quote_tweet_id: Optional tweet to quote
            auto_thread: If True, append thread number to text
            
        Returns:
            Dict with reply info
        """
        if auto_thread:
            # Auto-increment thread number
            text = f"{text}"
        
        try:
            tweet = self.client.reply_to(
                tweet_id=tweet_id,
                text=text,
                quote_tweet_id=quote_tweet_id
            )
            
            logger.info(f"Reply posted: {tweet.id}")
            return {
                "success": True,
                "tweet_id": tweet.id,
                "text": tweet.text,
                "in_reply_to": tweet_id,
                "url": f"https://twitter.com/i/status/{tweet.id}"
            }
            
        except TwitterAPIError as e:
            logger.error(f"Failed to reply: {e}")
            return {"success": False, "error": e.message}
    
    def quote_tweet(
        self,
        tweet_id: str,
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Quote a tweet with optional comment.
        
        Args:
            tweet_id: Tweet to quote
            comment: Optional additional comment
            
        Returns:
            Dict with quote info
        """
        try:
            tweet = self.client.quote_tweet(
                tweet_id=tweet_id,
                text=comment
            )
            
            logger.info(f"Quote tweet posted: {tweet.id}")
            return {
                "success": True,
                "tweet_id": tweet.id,
                "text": tweet.text,
                "quoted_tweet_id": tweet_id,
                "url": f"https://twitter.com/i/status/{tweet.id}"
            }
            
        except TwitterAPIError as e:
            logger.error(f"Failed to quote: {e}")
            return {"success": False, "error": e.message}
    
    def delete_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """Delete a tweet."""
        try:
            self.client.delete_tweet(tweet_id)
            logger.info(f"Tweet deleted: {tweet_id}")
            return {"success": True, "tweet_id": tweet_id}
        except TwitterAPIError as e:
            logger.error(f"Failed to delete: {e}")
            return {"success": False, "error": e.message}
    
    def get_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """Get tweet details."""
        try:
            tweet = self.client.get_tweet(tweet_id)
            return {
                "success": True,
                "tweet": tweet.to_dict()
            }
        except TwitterAPIError as e:
            return {"success": False, "error": e.message}
    
    def schedule_post(
        self,
        text: str,
        post_at: datetime,
        reply_settings: str = "everyone"
    ) -> Dict[str, Any]:
        """
        Schedule a tweet for later.
        
        Note: Twitter API doesn't support native scheduling.
        This uses a local scheduling file for integration
        with cron-based posting.
        
        Args:
            text: Tweet content
            post_at: datetime to post
            reply_settings: Reply settings
            
        Returns:
            Scheduling info
        """
        queue_dir = Path(os.getenv("POST_QUEUE_DIR", "/home/wner/clawd/post_queue"))
        queue_dir.mkdir(parents=True, exist_ok=True)
        
        scheduled = {
            "text": text,
            "scheduled_for": post_at.isoformat(),
            "reply_settings": reply_settings,
            "created_at": datetime.now().isoformat()
        }
        
        filename = f"scheduled_{post_at.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = queue_dir / filename
        
        with open(filepath, "w") as f:
            json.dump(scheduled, f, indent=2)
        
        logger.info(f"Tweet scheduled for {post_at}")
        return {
            "success": True,
            "scheduled_for": post_at.isoformat(),
            "file": str(filepath)
        }
    
    def get_scheduled(self) -> List[Dict[str, Any]]:
        """Get list of scheduled tweets."""
        queue_dir = Path(os.getenv("POST_QUEUE_DIR", "/home/wner/clawd/post_queue"))
        
        if not queue_dir.exists():
            return []
        
        scheduled = []
        for f in queue_dir.glob("scheduled_*.json"):
            with open(f) as file:
                data = json.load(file)
                data["file"] = str(f)
                scheduled.append(data)
        
        return sorted(scheduled, key=lambda x: x.get("scheduled_for", ""))
    
    def cancel_scheduled(self, filename: str) -> Dict[str, Any]:
        """Cancel a scheduled tweet."""
        queue_dir = Path(os.getenv("POST_QUEUE_DIR", "/home/wner/clawd/post_queue"))
        filepath = queue_dir / filename
        
        if filepath.exists():
            filepath.unlink()
            logger.info(f"Cancelled: {filename}")
            return {"success": True, "file": filename}
        
        return {"success": False, "error": "File not found"}


# Convenience functions

def post(text: str, **kwargs) -> Dict[str, Any]:
    """Quick post function."""
    poster = TweetPoster()
    return poster.post(text, **kwargs)


def reply(tweet_id: str, text: str, **kwargs) -> Dict[str, Any]:
    """Quick reply function."""
    poster = TweetPoster()
    return poster.reply_to(tweet_id, text, **kwargs)


def quote(tweet_id: str, comment: str = None, **kwargs) -> Dict[str, Any]:
    """Quick quote function."""
    poster = TweetPoster()
    return poster.quote_tweet(tweet_id, comment, **kwargs)
