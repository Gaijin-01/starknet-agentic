"""
Twitter API v2 Client.

Handles authentication, API requests, and rate limiting
for Twitter/X operations.
"""

#!/usr/bin/env python3
"""Twitter API v2 client for X/Twitter operations."""

import os
import time
import json
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import requests

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Tweet:
    """Represents a Twitter tweet."""
    id: str
    text: str
    author_id: str
    created_at: str
    metrics: Optional[Dict[str, Any]] = None
    referenced_tweets: Optional[List[str]] = None
    reply_settings: Optional[str] = None
    source: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "author_id": self.author_id,
            "created_at": self.created_at,
            "metrics": self.metrics,
            "referenced_tweets": self.referenced_tweets,
            "reply_settings": self.reply_settings,
            "source": self.source
        }


class TwitterAPIError(Exception):
    """Base exception for Twitter API errors."""
    def __init__(self, message: str, code: Optional[int] = None, details: Optional[Dict] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class RateLimitError(TwitterAPIError):
    """Raised when rate limit is exceeded."""
    def __init__(self, reset_time: int):
        self.reset_time = reset_time
        super().__init__(f"Rate limited. Resets at {reset_time}", code=429)


class TwitterClient:
    """Twitter API v2 client with OAuth 2.0 App-Only or OAuth 1.0a."""
    
    API_BASE = "https://api.twitter.com/2"
    UPLOAD_BASE = "https://upload.twitter.com/1.1"
    
    def __init__(
        self,
        bearer_token: Optional[str] = None,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        access_token_secret: Optional[str] = None
    ):
        """
        Initialize Twitter client.
        
        Args:
            bearer_token: OAuth 2.0 Bearer Token (App-Only)
            api_key: API Key (OAuth 1.0a)
            api_secret: API Secret
            access_token: Access Token
            access_token_secret: Access Token Secret
        """
        self.bearer_token = bearer_token or os.getenv("TWITTER_BEARER_TOKEN")
        self.api_key = api_key or os.getenv("TWITTER_API_KEY")
        self.api_secret = api_secret or os.getenv("TWITTER_API_SECRET")
        self.access_token = access_token or os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_token_secret = access_token_secret or os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        
        self._rate_limit_remaining = 0
        self._rate_limit_reset = 0
        
        logger.info("TwitterClient initialized")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers based on auth method."""
        if self.bearer_token:
            return {
                "Authorization": f"Bearer {self.bearer_token}",
                "Content-Type": "application/json"
            }
        elif self.api_key and self.access_token:
            # OAuth 1.0a - in production, use proper OAuth library
            return {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
        else:
            raise TwitterAPIError("No authentication credentials provided")
    
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Make API request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            max_retries: Maximum retry attempts
            
        Returns:
            Response JSON data
            
        Raises:
            TwitterAPIError: On API error
            RateLimitError: When rate limited
        """
        url = f"{self.API_BASE}{endpoint}"
        headers = self._get_headers()
        
        for attempt in range(max_retries):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    params=params,
                    timeout=30
                )
                
                # Update rate limit info
                self._rate_limit_remaining = int(
                    response.headers.get("x-rate-limit-remaining", 0)
                )
                self._rate_limit_reset = int(
                    response.headers.get("x-rate-limit-reset", 0)
                )
                
                if response.status_code == 429:
                    reset_time = int(response.headers.get("x-rate-limit-reset", 0))
                    wait_time = max(reset_time - int(time.time()), 1)
                    logger.warning(f"Rate limited. Waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue
                
                if not response.ok:
                    error_data = response.json() if response.content else {}
                    raise TwitterAPIError(
                        f"API error: {response.status_code}",
                        code=response.status_code,
                        details=error_data
                    )
                
                return response.json()
                
            except requests.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise TwitterAPIError(f"Request failed after {max_retries} attempts")
        
        raise TwitterAPIError("Max retries exceeded")
    
    # ============ User Operations ============
    
    def get_me(self) -> Dict[str, Any]:
        """Get current user (authenticated account)."""
        return self._request("GET", "/users/me")
    
    def get_user_by_username(self, username: str) -> Dict[str, Any]:
        """Get user by username."""
        return self._request("GET", f"/users/by/username/{username}")
    
    def get_user_tweets(self, user_id: str, max_results: int = 100) -> List[Tweet]:
        """Get recent tweets by user ID."""
        params = {"max_results": min(max_results, 100)}
        data = self._request("GET", f"/users/{user_id}/tweets", params=params)
        
        tweets = []
        for tweet_data in data.get("data", []):
            includes = data.get("includes", {}).get("tweets", [])
            tweets.append(self._parse_tweet(tweet_data, includes))
        
        return tweets
    
    # ============ Tweet Operations ============
    
    def create_tweet(
        self,
        text: str,
        reply_settings: str = "everyone",
        poll_options: Optional[List[str]] = None,
        poll_duration: Optional[int] = None
    ) -> Tweet:
        """
        Create a new tweet.
        
        Args:
            text: Tweet content (max 280 chars)
            reply_settings: "everyone", "mentionedUsers", or "following"
            poll_options: List of poll options (2-4)
            poll_duration: Poll duration in minutes (5, 10, 30, 60, 90, 1440, 10080, 43200, 525600)
            
        Returns:
            Created Tweet object
        """
        payload: Dict[str, Any] = {"text": text, "reply_settings": reply_settings}
        
        if poll_options:
            payload["poll"] = {
                "options": poll_options,
                "duration_minutes": poll_duration or 1440
            }
        
        data = self._request("POST", "/tweets", data=payload)
        return self._parse_tweet(data["data"])
    
    def delete_tweet(self, tweet_id: str) -> bool:
        """
        Delete a tweet.
        
        Args:
            tweet_id: Tweet ID to delete
            
        Returns:
            True if successful
        """
        self._request("DELETE", f"/tweets/{tweet_id}")
        return True
    
    def get_tweet(self, tweet_id: str) -> Tweet:
        """Get a single tweet by ID."""
        params = {"tweet.fields": "created_at,public_metrics,source,reply_settings"}
        data = self._request("GET", f"/tweets/{tweet_id}", params=params)
        return self._parse_tweet(data["data"])
    
    def get_tweets(self, tweet_ids: List[str]) -> List[Tweet]:
        """Get multiple tweets by IDs."""
        params = {"ids": ",".join(tweet_ids)}
        params["tweet.fields"] = "created_at,public_metrics,source,reply_settings"
        data = self._request("GET", "/tweets", params=params)
        
        tweets = []
        for tweet_data in data.get("data", []):
            tweets.append(self._parse_tweet(tweet_data))
        
        return tweets
    
    def search_recent_tweets(
        self,
        query: str,
        max_results: int = 100,
        start_time: Optional[str] = None
    ) -> List[Tweet]:
        """
        Search recent tweets.
        
        Args:
            query: Search query (e.g., "bitcoin has:links")
            max_results: Max results (10-100)
            start_time: ISO 8601 datetime (e.g., "2024-01-01T00:00:00Z")
            
        Returns:
            List of matching tweets
        """
        params: Dict[str, Any] = {
            "query": query,
            "max_results": min(max_results, 100)
        }
        if start_time:
            params["start_time"] = start_time
        
        data = self._request("GET", "/tweets/search/recent", params=params)
        
        tweets = []
        for tweet_data in data.get("data", []):
            tweets.append(self._parse_tweet(tweet_data))
        
        return tweets
    
    # ============ Reply Operations ============
    
    def reply_to(
        self,
        tweet_id: str,
        text: str,
        quote_tweet_id: Optional[str] = None
    ) -> Tweet:
        """
        Reply to a tweet.
        
        Args:
            tweet_id: Tweet ID to reply to
            text: Reply content
            quote_tweet_id: Optional quote tweet ID
            
        Returns:
            Created reply Tweet
        """
        payload: Dict[str, Any] = {
            "text": text,
            "reply": {"in_reply_to_tweet_id": tweet_id}
        }
        
        if quote_tweet_id:
            payload["quote_tweet_id"] = quote_tweet_id
        
        data = self._request("POST", "/tweets", data=payload)
        return self._parse_tweet(data["data"])
    
    def quote_tweet(self, tweet_id: str, text: Optional[str] = None) -> Tweet:
        """
        Quote a tweet.
        
        Args:
            tweet_id: Tweet ID to quote
            text: Optional additional text
            
        Returns:
            Created quote tweet
        """
        if text:
            payload = {"text": text, "quote_tweet_id": tweet_id}
            data = self._request("POST", "/tweets", data=payload)
        else:
            data = self._request("POST", "/tweets", data={"quote_tweet_id": tweet_id})
        
        return self._parse_tweet(data["data"])
    
    # ============ Like/Retweet Operations ============
    
    def like_tweet(self, tweet_id: str) -> bool:
        """Like a tweet."""
        user_id = self.get_me()["data"]["id"]
        self._request(
            "POST",
            f"/users/{user_id}/likes",
            data={"tweet_id": tweet_id}
        )
        return True
    
    def unlike_tweet(self, tweet_id: str) -> bool:
        """Unlike a tweet."""
        user_id = self.get_me()["data"]["id"]
        self._request(
            "DELETE",
            f"/users/{user_id}/likes/{tweet_id}"
        )
        return True
    
    def retweet(self, tweet_id: str) -> bool:
        """Retweet a tweet."""
        user_id = self.get_me()["data"]["id"]
        self._request(
            "POST",
            f"/users/{user_id}/retweets",
            data={"tweet_id": tweet_id}
        )
        return True
    
    def unretweet(self, tweet_id: str) -> bool:
        """Unretweet a tweet."""
        user_id = self.get_me()["data"]["id"]
        self._request(
            "DELETE",
            f"/users/{user_id}/retweets/{tweet_id}"
        )
        return True
    
    # ============ Follow Operations ============
    
    def follow_user(self, user_id: str) -> bool:
        """Follow a user."""
        my_id = self.get_me()["data"]["id"]
        self._request("POST", f"/users/{my_id}/following", data={"target_user_id": user_id})
        return True
    
    def unfollow_user(self, user_id: str) -> bool:
        """Unfollow a user."""
        my_id = self.get_me()["data"]["id"]
        self._request("DELETE", f"/users/{my_id}/following/{user_id}")
        return True
    
    def get_followers(self, user_id: str, max_results: int = 100) -> List[Dict]:
        """Get followers of a user."""
        params = {"max_results": min(max_results, 1000)}
        data = self._request("GET", f"/users/{user_id}/followers", params=params)
        return data.get("data", [])
    
    def get_following(self, user_id: str, max_results: int = 100) -> List[Dict]:
        """Get users this user is following."""
        params = {"max_results": min(max_results, 1000)}
        data = self._request("GET", f"/users/{user_id}/following", params=params)
        return data.get("data", [])
    
    # ============ Helper Methods ============
    
    def _parse_tweet(
        self,
        data: Dict[str, Any],
        includes: Optional[List[Dict]] = None
    ) -> Tweet:
        """
        Parse tweet data into Tweet object with safe access.
        
        Args:
            data: Tweet data from API
            includes: Optional included tweets (for references)
            
        Returns:
            Tweet object
            
        Raises:
            ValueError: If required fields missing
        """
        # Safe access for required fields
        tweet_id = data.get("id")
        text = data.get("text")
        
        if not tweet_id:
            raise ValueError("Missing required field: id")
        if not text:
            raise ValueError("Missing required field: text")
        
        # Safe access for optional fields
        metrics = data.get("public_metrics")
        referenced = data.get("referenced_tweets")
        
        # Parse referenced tweets
        referenced_ids = None
        if referenced:
            referenced_ids = []
            for r in referenced:
                if isinstance(r, dict) and r.get("id"):
                    referenced_ids.append(r["id"])
        
        # Build Tweet object
        return Tweet(
            id=tweet_id,
            text=text,
            author_id=data.get("author_id", ""),
            created_at=data.get("created_at", ""),
            metrics=metrics,
            referenced_tweets=referenced_ids,
            reply_settings=data.get("reply_settings"),
            source=data.get("source")
        )
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status."""
        return {
            "remaining": self._rate_limit_remaining,
            "reset_at": self._rate_limit_reset,
            "reset_time_formatted": time.strftime(
                "%Y-%m-%d %H:%M:%S",
                time.localtime(self._rate_limit_reset)
            ) if self._rate_limit_reset else None
        }


# Convenience function for quick access
def get_client() -> TwitterClient:
    """Get configured Twitter client."""
    return TwitterClient()
