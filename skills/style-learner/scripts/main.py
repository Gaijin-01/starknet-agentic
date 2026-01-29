#!/usr/bin/env python3
"""
style-learner/main.py - Bird-based Style Learning Orchestrator

Uses bird CLI instead of nodriver for all X/Twitter operations.
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import subprocess
import random

# Add scripts to path
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

from analyzer import StyleAnalyzer
from generator import ContentGenerator
from executor import BirdExecutor

class StyleLearner:
    """Main orchestrator using bird for X operations"""
    
    def __init__(self):
        self.executor = BirdExecutor()
        self.analyzer = StyleAnalyzer()
        self.generator = ContentGenerator()
        # Use absolute paths from script location
        script_dir = Path(__file__).parent.resolve()
        self.data_dir = script_dir.parent / "data"
        self.profiles_dir = script_dir.parent / "profiles"
        self.profiles_dir.mkdir(exist_ok=True)
    
    def run_command(self, cmd: List[str]) -> dict:
        """Execute bird command and return JSON"""
        try:
            result = subprocess.run(
                ["bird"] + cmd + ["--json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                print(f"❌ Bird error: {result.stderr}")
                return {}
        except Exception as e:
            print(f"❌ Error: {e}")
            return {}
    
    def learn(self, hours: int = 4, max_tweets: int = 100):
        """
        Learn user's style by fetching their tweets and engagement.
        Uses bird to fetch data instead of browser watching.
        """
        print(f"📚 Learning style from @SefirotWatch...")
        
        handle = "SefirotWatch"
        
        # Fetch user's tweets
        print("  📥 Fetching tweets...")
        tweets = self.run_command(["user-tweets", handle, "-n", str(max_tweets)])
        
        if not tweets:
            print("  ⚠️ No tweets found")
            return
        
        # Fetch likes
        print("  ❤️ Fetching likes...")
        likes = self.run_command(["likes", "-n", str(max_tweets)])
        
        # Fetch mentions
        print("  📬 Fetching mentions...")
        mentions = self.run_command(["mentions", "-n", str(max_tweets)])
        
        observations = {
            "timestamp": datetime.now().isoformat(),
            "source": "bird",
            "user": handle,
            "tweets_count": len(tweets) if isinstance(tweets, list) else 0,
            "likes_count": len(likes) if isinstance(likes, list) else 0,
            "mentions_count": len(mentions) if isinstance(mentions, list) else 0,
            "tweets": tweets[:50] if isinstance(tweets, list) else [],
            "likes": likes[:50] if isinstance(likes, list) else [],
        }
        
        # Save observations
        obs_file = self.data_dir / "observations" / f"{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        obs_file.parent.mkdir(exist_ok=True)
        with open(obs_file, 'a') as f:
            f.write(json.dumps(observations) + "\n")
        
        print(f"  ✅ Saved {len(observations.get('tweets', []))} tweets")
        
        # Build profile
        self.analyze()
    
    def analyze(self, days: int = 30):
        """Analyze collected data and build style profile"""
        print(f"📊 Analyzing style profile...")
        
        profile = self.analyzer.build_profile()
        
        profile_file = self.profiles_dir / "style_profile.json"
        with open(profile_file, 'w') as f:
            json.dump(profile, f, indent=2)
        
        print(f"  ✅ Profile saved: {profile_file}")
        print(f"  📝 Tone: {', '.join(profile.get('persona', {}).get('tone', []))}")
        print(f"  🔤 Top words: {list(profile.get('vocabulary', {}).get('frequent', {}).keys())[:5]}")
        
        return profile
    
    def generate(self, content_type: str = "gm", context: str = ""):
        """Generate content in user's style"""
        profile_file = self.profiles_dir / "style_profile.json"
        if not profile_file.exists():
            print("❌ No profile. Run 'learn' first.")
            return
        
        with open(profile_file) as f:
            profile = json.load(f)
        
        content = self.generator.generate(content_type, profile, context)
        print(f"🎯 Generated {content_type}:")
        print(f"  {content}")
        return content
    
    def assist(self, hours: int = 4):
        """Semi-autonomous mode: generate drafts for approval"""
        print(f"🤖 Assist mode for {hours} hours...")
        profile = self.analyze()
        
        # Generate some content
        for content_type in ["gm", "news", "insight"]:
            content = self.generate(content_type)
            print(f"  📝 {content_type}: {content[:50]}...")
    
    def auto(self, hours: int = 2):
        """Full autonomous mode using bird for posting"""
        print(f"🚀 Auto mode for {hours} hours (using bird)...")
        profile = self.analyze()
        
        if not profile:
            print("❌ No profile. Run learn first.")
            return
        
        # This would post content using bird
        # For safety, we just generate drafts
        print("  ⚠️ Auto-posting not implemented (use assist mode for drafts)")
    
    def post(self, content: str):
        """Post content using bird"""
        result = self.executor.post(content)
        return result
    
    def reply(self, tweet_url: str, content: str):
        """Reply to tweet using bird"""
        result = self.executor.reply(tweet_url, content)
        return result
    
    def like(self, tweet_url: str):
        """Like tweet using bird"""
        result = self.executor.like(tweet_url)
        return result


def main():
    parser = argparse.ArgumentParser(description="Style Learner - Bird-based")
    parser.add_argument("command", choices=["learn", "analyze", "generate", "assist", "auto", "post", "reply", "like"],
                       help="Command to run")
    parser.add_argument("--hours", type=int, default=4, help="Hours to run")
    parser.add_argument("--type", default="gm", help="Content type for generate")
    parser.add_argument("--context", default="", help="Context for generation")
    parser.add_argument("--tweet", help="Tweet URL for reply/like")
    parser.add_argument("--content", help="Content to post")
    
    args = parser.parse_args()
    
    learner = StyleLearner()
    
    if args.command == "learn":
        learner.learn(hours=args.hours)
    elif args.command == "analyze":
        learner.analyze()
    elif args.command == "generate":
        learner.generate(args.type, args.context)
    elif args.command == "assist":
        learner.assist(hours=args.hours)
    elif args.command == "auto":
        learner.auto(hours=args.hours)
    elif args.command == "post":
        if args.content:
            learner.post(args.content)
        else:
            print("❌ --content required")
    elif args.command == "reply":
        if args.tweet and args.content:
            learner.reply(args.tweet, args.content)
        else:
            print("❌ --tweet and --content required")
    elif args.command == "like":
        if args.tweet:
            learner.like(args.tweet)
        else:
            print("❌ --tweet required")


if __name__ == "__main__":
    main()
