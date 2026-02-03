#!/usr/bin/env python3
"""
style-learner/executor.py - Bird-based Execution

Uses bird CLI for all X/Twitter operations.
"""

import subprocess
import json
import re
from typing import Dict, List, Optional
from datetime import datetime


class BirdExecutor:
    """Execute X/Twitter actions via bird CLI"""
    
    def __init__(self):
        self.last_action_time = None
        self.min_delay_seconds = 5
    
    def _run(self, cmd: List[str]) -> Dict:
        """Run bird command"""
        try:
            result = subprocess.run(
                ["bird"] + cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return {"success": True, "output": result.stdout}
            else:
                return {"success": False, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _extract_id(self, url: str) -> str:
        """Extract tweet ID from URL"""
        # https://x.com/user/status/1234567890
        match = re.search(r'status/(\d+)', url)
        if match:
            return match.group(1)
        return url
    
    def post(self, content: str) -> Dict:
        """Post a new tweet"""
        print(f"  🐦 Posting: {content[:50]}...")
        return self._run(["tweet", content])
    
    def reply(self, tweet_url: str, content: str) -> Dict:
        """Reply to a tweet"""
        print(f"  💬 Replying to {tweet_url}: {content[:50]}...")
        return self._run(["reply", tweet_url, content])
    
    def like(self, tweet_url: str) -> Dict:
        """Like a tweet"""
        print(f"  ❤️ Liking {tweet_url}...")
        # Bird doesn't have native like command, use bookmarks or raw API
        # For now, we'll skip likes via bird
        return {"success": False, "error": "Bird doesn't support likes yet"}
    
    def retweet(self, tweet_url: str) -> Dict:
        """Retweet a tweet"""
        print(f"  🔄 Retweeting {tweet_url}...")
        return self._run(["retweet", tweet_url])
    
    def quote(self, tweet_url: str, content: str) -> Dict:
        """Quote tweet with commentary"""
        print(f"  📌 Quoting {tweet_url}: {content[:50]}...")
        return self._run(["tweet", f"{content} {tweet_url}"])
    
    def follow(self, handle: str) -> Dict:
        """Follow a user"""
        print(f"  👤 Following @{handle}...")
        return self._run(["follow", handle])
    
    def unfollow(self, handle: str) -> Dict:
        """Unfollow a user"""
        print(f"  👋 Unfollowing @{handle}...")
        return self._run(["unfollow", handle])
    
    def get_tweet(self, tweet_url: str) -> Dict:
        """Get tweet content"""
        tweet_id = self._extract_id(tweet_url)
        result = self._run(["read", tweet_id])
        if result["success"]:
            try:
                return json.loads(result["output"])
            except:
                return {"text": result["output"]}
        return {}
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Search tweets"""
        result = self._run(["search", query, "-n", str(limit), "--json"])
        if result["success"]:
            try:
                return json.loads(result["output"])
            except:
                return []
        return []
    
    def get_user_tweets(self, handle: str, limit: int = 20) -> List[Dict]:
        """Get user's recent tweets"""
        result = self._run(["user-tweets", handle, "-n", str(limit), "--json"])
        if result["success"]:
            try:
                return json.loads(result["output"])
            except:
                return []
        return []
    
    def get_likes(self, handle: str, limit: int = 20) -> List[Dict]:
        """Get user's likes"""
        result = self._run(["likes", handle, "-n", str(limit), "--json"])
        if result["success"]:
            try:
                return json.loads(result["output"])
            except:
                return []
        return []
    
    def get_mentions(self, handle: str = None, limit: int = 20) -> List[Dict]:
        """Get mentions"""
        cmd = ["mentions", "-n", str(limit), "--json"]
        if handle:
            cmd.extend(["--user", handle])
        
        result = self._run(cmd)
        if result["success"]:
            try:
                return json.loads(result["output"])
            except:
                return []
        return []
    
    def get_home_timeline(self, limit: int = 20) -> List[Dict]:
        """Get home timeline"""
        result = self._run(["home", "-n", str(limit), "--json"])
        if result["success"]:
            try:
                return json.loads(result["output"])
            except:
                return []
        return []
    
    def whoami(self) -> Dict:
        """Get current user info"""
        result = self._run(["whoami", "--json"])
        if result["success"]:
            try:
                return json.loads(result["output"])
            except:
                return {}
        return {}


# CLI shortcuts
if __name__ == "__main__":
    import sys
    
    executor = BirdExecutor()
    
    if len(sys.argv) < 2:
        print("Usage: executor.py <command> [args]")
        print("Commands: post, reply, like, retweet, quote, follow, search")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "post":
        content = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else input("Content: ")
        executor.post(content)
    elif cmd == "reply":
        url = sys.argv[2] if len(sys.argv) > 2 else input("Tweet URL: ")
        content = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else input("Reply: ")
        executor.reply(url, content)
    elif cmd == "like":
        url = sys.argv[2] if len(sys.argv) > 2 else input("Tweet URL: ")
        executor.like(url)
    elif cmd == "search":
        query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else input("Query: ")
        results = executor.search(query)
        for r in results:
            print(f"  - {r.get('text', '')[:100]}")
    else:
        print(f"Unknown command: {cmd}")
