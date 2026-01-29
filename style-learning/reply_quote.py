#!/usr/bin/env python3
"""
Reply & Quote Generator with Approve Step
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

PROFILE_FILE = Path("/home/wner/clawdbot/skills/style-learner/data/profiles/style_profile.json")
OUTPUT_DIR = Path("/home/wner/clawd/style-learning")


def load_profile():
    with open(PROFILE_FILE) as f:
        return json.load(f)


def load_tweet(url: str) -> Dict:
    """Load tweet content via bird"""
    result = subprocess.run(
        ["bird", url, "--json"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        try:
            return json.loads(result.stdout)
        except:
            return {"content": "Tweet content", "author": "unknown"}
    return {"content": "Tweet content", "author": "unknown"}


def like_tweet(url: str) -> bool:
    """Like tweet via bird"""
    # Bird doesn't have direct like, use browser or API
    print(f"⚠️  Like via bird not implemented. URL: {url}")
    return False


def generate_replies(tweet_content: str, author: str) -> List[str]:
    """Generate 2 reply options in SefirotWatch style"""
    profile = load_profile()
    vocab = profile.get("vocabulary", {})
    style = profile.get("style", {})
    
    replies = [
        f"这。",
        f"同意 {author}。",
        f"值得关注。",
        f"正在分析。",
        f"关键点。",
        f"理解。",
        f"好的观察。",
        f"�狼",  # wolf emoji
    ]
    
    # Pick 2 unique
    import random
    selected = random.sample(replies, 2)
    
    # Add signature if style allows
    if style.get("emoji_frequency", 0) > 0:
        emojis = vocab.get("signature_phrases", ["🐺"])
        selected = [r + f" {emojis[0]}" for r in selected]
    
    return selected


def generate_quotes(tweet_content: str, author: str) -> List[str]:
    """Generate 2 quote options"""
    profile = load_profile()
    vocab = profile.get("vocabulary", {})
    style = profile.get("style", {})
    
    quotes = [
        "重点。",
        "记住。",
        "这很关键。",
        "理解。",
        "同意。",
        "�狼",  # wolf
    ]
    
    import random
    selected = random.sample(quotes, 2)
    
    if style.get("emoji_frequency", 0) > 0:
        emojis = vocab.get("signature_phrases", ["🐺"])
        selected = [q + f" {emojis[0]}" for q in selected]
    
    return selected


def approve_step(replies: List[str], quotes: List[str]):
    """Show options for approval"""
    print("\n" + "="*60)
    print("📝 OPTIONS FOR APPROVAL")
    print("="*60)
    
    print("\n🔹 REPLIES (2 варианта):")
    for i, r in enumerate(replies, 1):
        print(f"  [{i}] {r}")
    
    print("\n🔹 QUOTES (2 варианта):")
    for i, q in enumerate(quotes, 1):
        print(f"  [{i}] {q}")
    
    print("\n" + "-"*60)
    print("Commands: 'r1' = reply #1, 'q2' = quote #2, 'rq12' = both, 'skip' = none")
    print("-"*60)
    
    # For automation, auto-return first option of each
    return {"reply": replies[0] if replies else None, "quote": quotes[0] if quotes else None}


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Reply & Quote Generator")
    parser.add_argument("url", help="Tweet URL")
    parser.add_argument("--like", action="store_true", help="Like the tweet")
    parser.add_argument("--dry-run", action="store_true", help="Show options only")
    
    args = parser.parse_args()
    
    print(f"🔗 Processing: {args.url}")
    
    # Load tweet
    tweet = load_tweet(args.url)
    content = tweet.get("content", "Tweet content")
    author = tweet.get("author", "unknown")
    
    print(f"👤 Author: {author}")
    print(f"📄 Content: {content[:100]}...")
    
    # Like if requested
    if args.like:
        like_tweet(args.url)
    
    # Generate options
    replies = generate_replies(content, author)
    quotes = generate_quotes(content, author)
    
    if args.dry_run:
        approve_step(replies, quotes)
    else:
        # Auto-approve first option of each
        approved = approve_step(replies, quotes)
        print(f"\n✅ Approved: reply='{approved['reply']}', quote='{approved['quote']}'")
        return approved


if __name__ == "__main__":
    main()
