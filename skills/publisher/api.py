#!/usr/bin/env python3
"""
Twitter API wrapper using curl (bird CLI fallback)
"""

import subprocess
import json
from typing import Dict, Optional
from datetime import datetime


class TwitterAPI:
    """Twitter API client using bird CLI."""
    
    def __init__(self):
        self.bird_path = "bird"
    
    def _run(self, args: list) -> subprocess.CompletedProcess:
        """Run bird command."""
        return subprocess.run(
            [self.bird_path] + args,
            capture_output=True,
            text=True,
            timeout=60
        )
    
    def whoami(self) -> Optional[Dict]:
        """Get current user info."""
        result = self._run(["whoami"])
        if result.returncode == 0:
            return {"username": result.stdout.strip()}
        return None
    
    def post(self, content: str) -> Dict:
        """Post a tweet."""
        result = self._run(["post", content])
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def reply(self, tweet_id: str, content: str) -> Dict:
        """Reply to a tweet."""
        result = self._run(["reply", tweet_id, content])
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def quote(self, tweet_id: str, comment: str) -> Dict:
        """Quote a tweet."""
        result = self._run(["quote", tweet_id, "--comment", comment])
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def get_tweet(self, tweet_id: str) -> Optional[Dict]:
        """Get tweet by ID."""
        result = self._run(["read", tweet_id])
        if result.returncode == 0:
            return {"tweet_id": tweet_id, "content": result.stdout}
        return None
    
    def delete(self, tweet_id: str) -> Dict:
        """Delete a tweet."""
        result = self._run(["delete", tweet_id])
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def search(self, query: str, limit: int = 10) -> list:
        """Search tweets."""
        result = self._run(["search", query, "--limit", str(limit)])
        if result.returncode == 0:
            return [{"content": line} for line in result.stdout.strip().split("\n") if line]
        return []
    
    def rate_limit(self) -> Dict:
        """Check rate limits (bird-specific)."""
        result = self._run(["rate-limit"])
        return {
            "success": result.returncode == 0,
            "output": result.stdout
        }


# Convenience functions
def post(content: str) -> Dict:
    """Quick post."""
    api = TwitterAPI()
    return api.post(content)


def reply(tweet_id: str, content: str) -> Dict:
    """Quick reply."""
    api = TwitterAPI()
    return api.reply(tweet_id, content)


def quote(tweet_id: str, comment: str) -> Dict:
    """Quick quote."""
    api = TwitterAPI()
    return api.quote(tweet_id, comment)
