#!/usr/bin/env python3
"""
publisher - Unified content publishing skill

Merges: post-generator, queue-manager, twitter-api, x-algorithm-optimizer
"""

import argparse
import json
import yaml
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


class Config:
    """Load and manage publisher configuration."""
    
    def __init__(self, config_path: str = None):
        base = Path(__file__).parent
        self.config_path = config_path or base / "config.yaml"
        self._load()
    
    def _load(self):
        if self.config_path.exists():
            with open(self.config_path) as f:
                self.data = yaml.safe_load(f) or {}
        else:
            self.data = {}
    
    @property
    def persona(self) -> Dict:
        return self.data.get("persona", {})
    
    @property
    def scheduler(self) -> Dict:
        return self.data.get("scheduler", {})
    
    @property
    def optimizer(self) -> Dict:
        return self.data.get("optimizer", {})
    
    @property
    def twitter(self) -> Dict:
        return self.data.get("twitter", {})
    
    @property
    def templates(self) -> Dict:
        return self.data.get("templates", {})


@dataclass
class Post:
    """Represents a post."""
    content: str
    post_type: str = "custom"
    created_at: str = None
    scheduled_at: str = None
    status: str = "draft"


class Publisher:
    """
    Unified publisher for content creation, scheduling, and posting.
    
    Combines functionality from:
    - post-generator: template-based content creation
    - queue-manager: scheduling and queue management
    - twitter-api: X/Twitter API integration
    - x-algorithm-optimizer: timing optimization
    """
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.base_dir = Path.home() / "clawd"
        self.queue_dir = self.base_dir / self.config.scheduler.get("base_dir", "post_queue")
        self._ensure_queue_dir()
    
    def _ensure_queue_dir(self):
        """Create queue directory structure."""
        for subdir in self.config.scheduler.get("subdirs", ["ready", "posted", "failed"]):
            (self.queue_dir / subdir).mkdir(parents=True, exist_ok=True)
    
    # === CONTENT GENERATION (from post-generator) ===
    
    def generate(self, content_type: str = "gm", **kwargs) -> str:
        """Generate content using templates."""
        templates = self.config.templates.get(content_type, ["{content}"])
        template = templates[0]
        
        if content_type == "gm":
            emoji = self.config.persona.get("emoji", ["🔥"])[0]
            topic = kwargs.get("topic", "zk summer loading")
            result = template.format(emoji=emoji, topic=topic)
        elif content_type == "news":
            headline = kwargs.get("headline", "")
            emoji = self.config.persona.get("emoji", ["🔥"])[0]
            result = template.format(headline=headline, emoji=emoji)
        elif content_type == "price":
            token = kwargs.get("token", "BTC")
            direction = kwargs.get("direction", "flat")
            percent = kwargs.get("percent", "0")
            emoji = self.config.persona.get("emoji", ["🔥"])[0]
            result = template.format(token=token, direction=direction, percent=percent, emoji=emoji)
        elif content_type == "custom":
            result = kwargs.get("content", template)
        else:
            result = template.format(**kwargs)
        
        return result
    
    def generate_and_save(self, content_type: str = "gm", **kwargs) -> Path:
        """Generate content and save to queue."""
        content = self.generate(content_type, **kwargs)
        post = Post(
            content=content,
            post_type=content_type,
            created_at=datetime.now().isoformat()
        )
        
        filename = f"{content_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path = self.queue_dir / "drafts" / filename
        
        with open(path, "w") as f:
            json.dump({
                "content": post.content,
                "type": post.post_type,
                "created_at": post.created_at,
                "status": post.status
            }, f, indent=2)
        
        return path
    
    # === QUEUE MANAGEMENT (from queue-manager) ===
    
    def queue_status(self) -> Dict:
        """Get queue status."""
        status = {"ready": 0, "posted": 0, "failed": 0, "drafts": 0}
        for subdir in status.keys():
            count = len(list((self.queue_dir / subdir).glob("*.json")))
            status[subdir] = count
        return status
    
    def list_queue(self, state: str = "ready") -> List[Path]:
        """List posts in queue state."""
        return list((self.queue_dir / state).glob("*.json"))
    
    def move_post(self, filename: str, from_state: str, to_state: str):
        """Move post between states."""
        src = self.queue_dir / from_state / filename
        dst = self.queue_dir / to_state / filename
        if src.exists():
            src.rename(dst)
    
    # === TWITTER API (from twitter-api) ===
    
    def _get_twitter_creds(self) -> Dict:
        """Get Twitter API credentials from environment."""
        import os
        return {
            "api_key": os.environ.get(self.config.twitter.get("api_key_env", "TWITTER_API_KEY"), ""),
            "api_secret": os.environ.get(self.config.twitter.get("api_secret_env", "TWITTER_API_SECRET"), ""),
            "access_token": os.environ.get(self.config.twitter.get("access_token_env", "TWITTER_ACCESS_TOKEN"), ""),
            "access_secret": os.environ.get(self.config.twitter.get("access_secret_env", "TWITTER_ACCESS_TOKEN_SECRET"), "")
        }
    
    def post(self, content: str) -> Dict:
        """Post content to X using bird CLI."""
        try:
            result = subprocess.run(
                ["bird", "post", content],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return {"status": "success", "output": result.stdout}
            else:
                return {"status": "error", "output": result.stderr}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def post_queue_item(self, filename: str) -> Dict:
        """Post item from ready queue."""
        path = self.queue_dir / "ready" / filename
        if not path.exists():
            return {"status": "error", "message": f"File not found: {path}"}
        
        with open(path) as f:
            data = json.load(f)
        
        result = self.post(data["content"])
        
        if result["status"] == "success":
            self.move_post(filename, "ready", "posted")
        else:
            self.move_post(filename, "ready", "failed")
        
        return result
    
    # === OPTIMIZATION (from x-algorithm-optimizer) ===
    
    def get_best_time(self, content_type: str = "post") -> str:
        """Get optimal posting time."""
        peak_hours = self.config.optimizer.get("peak_hours", [8, 9, 13, 21])
        now = datetime.now()
        
        for hour in peak_hours:
            if hour > now.hour:
                return now.replace(hour=hour, minute=0, second=0).isoformat()
        
        # Next day
        return now.replace(hour=peak_hours[0], minute=0, second=0) + timedelta(days=1)
    
    def optimize_schedule(self) -> Dict:
        """Get scheduling recommendations."""
        queue = self.list_queue("ready")
        peak_hours = self.config.optimizer.get("peak_hours", [8, 9, 13, 21])
        
        recommendations = []
        for i, post_file in enumerate(queue[:10]):  # Top 10
            best_hour = peak_hours[i % len(peak_hours)]
            recommendations.append({
                "file": post_file.name,
                "recommended_hour": best_hour
            })
        
        return {
            "queue_size": len(queue),
            "recommendations": recommendations,
            "peak_hours": peak_hours
        }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Publisher - Unified content publishing")
    
    sub = parser.add_subparsers(dest="command", help="Commands")
    
    # Generate
    gen = sub.add_parser("generate", help="Generate content")
    gen.add_argument("--type", default="gm", help="Content type (gm, news, price, custom)")
    gen.add_argument("--content", help="Custom content")
    gen.add_argument("--headline", help="News headline")
    gen.add_argument("--topic", help="Topic for gm")
    gen.add_argument("--token", help="Token for price")
    gen.add_argument("--save", action="store_true", help="Save to queue")
    
    # Queue
    q = sub.add_parser("queue", help="Queue management")
    q.add_argument("--status", action="store_true", help="Show queue status")
    q.add_argument("--list", const="ready", nargs="?", help="List queue items")
    
    # Post
    post = sub.add_parser("post", help="Post to X")
    post.add_argument("content", help="Content to post")
    
    # Post from queue
    post_q = sub.add_parser("post-queue", help="Post from ready queue")
    post_q.add_argument("filename", help="Filename in ready queue")
    
    # Schedule
    sched = sub.add_parser("schedule", help="Schedule post")
    sched.add_argument("content", help="Content to schedule")
    sched.add_argument("at", help="ISO timestamp (YYYY-MM-DDTHH:MM:SS)")
    
    # Optimize
    opt = sub.add_parser("optimize", help="Optimization recommendations")
    opt.add_argument("--best-time", action="store_true", help="Get best posting time")
    
    args = parser.parse_args()
    
    pub = Publisher()
    
    if args.command == "generate":
        content = pub.generate(
            content_type=args.type,
            content=args.content,
            headline=args.headline,
            topic=args.topic,
            token=args.token
        )
        print(f"Generated: {content}")
        if getattr(args, "save", False):
            path = pub.generate_and_save(args.type, content=args.content, headline=args.headline, topic=args.topic)
            print(f"Saved to: {path}")
    
    elif args.command == "queue":
        if getattr(args, "status", False):
            status = pub.queue_status()
            print(f"Queue: {status}")
        elif getattr(args, "list", False):
            items = pub.list_queue(args.list)
            for item in items:
                print(item.name)
    
    elif args.command == "post":
        result = pub.post(args.content)
        print(f"Status: {result['status']}")
        if result["status"] == "success":
            print(f"Output: {result.get('output', 'OK')}")
        else:
            print(f"Error: {result.get('output', result.get('message'))}")
    
    elif args.command == "post-queue":
        result = pub.post_queue_item(args.filename)
        print(f"Status: {result['status']}")
    
    elif args.command == "schedule":
        pub.schedule(args.content, args.at)
        print(f"Scheduled for: {args.at}")
    
    elif args.command == "optimize":
        if getattr(args, "best_time", False):
            best = pub.get_best_time()
            print(f"Best time: {best}")
        else:
            opt = pub.optimize_schedule()
            print(f"Queue size: {opt['queue_size']}")
            print(f"Peak hours: {opt['peak_hours']}")
            print("Recommendations:")
            for rec in opt["recommendations"][:5]:
                print(f"  {rec['file']}: hour {rec['recommended_hour']}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
