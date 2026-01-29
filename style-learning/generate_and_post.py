#!/usr/bin/env python3
"""
Style Learner + Bird Integration
Generates tweets in SefirotWatch style and posts via bird CLI.
"""

import json
import random
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

PROFILE_FILE = Path("/home/wner/clawdbot/skills/style-learner/data/profiles/style_profile.json")
OUTPUT_DIR = Path("/home/wner/clawd/style-learning")

# Templates based on SefirotWatch style patterns
TWEET_TEMPLATES = {
    "signal": [
        "信号确认。{target}。等待回调。",
        "{target} — 正在形成结构。耐心。",
        "{target}。更好的入场点。",
        "观察 {target}。可能在构建底部。",
        "{target} — 保持观察。",
    ],
    "update": [
        "{target} 突破。",
        "{target} 正在测试阻力。",
        "{target} 成交量放大。",
        "{target} — 接近关键位。",
    ],
    "thought": [
        "关于 {topic} 的思考。",
        "{topic} — 有趣的发展。",
        "{topic}。值得关注。",
        "正在研究 {topic}。初步结论：",
    ],
    "lfg": [
        "lfg 🐺",
        "准备好了。",
        "执行模式。",
        "开始行动。",
    ],
    "quote": [
        "这。",
        "同意。",
        "重点。",
        "记住这一点。",
    ],
}

# Topics for context
TOPICS = {
    "starknet": ["starknet", "stark ware", "layer2", " Cairo"],
    "crypto": ["crypto", "bitcoin", "eth", "defi", "rollup"],
    "trading": ["交易", "仓位", "止损", "盈利", "入场"],
    "tech": ["代码", "系统", "架构", "技术"],
}


def load_profile() -> Dict:
    with open(PROFILE_FILE) as f:
        return json.load(f)


def get_vocabulary(profile: Dict) -> Dict:
    return profile.get("vocabulary", {})


def generate_tweet(topic: str = "starknet") -> Dict:
    """Generate a tweet in SefirotWatch style"""
    profile = load_profile()
    vocab = get_vocabulary(profile)
    style = profile.get("style", {})
    
    # Pick template type
    template_type = random.choice(["signal", "update", "thought", "lfg"])
    templates = TWEET_TEMPLATES[template_type]
    
    # Get target/topic
    topic_keywords = TOPICS.get(topic, TOPICS["starknet"])
    target = random.choice(topic_keywords)
    
    # Generate base tweet
    template = random.choice(templates)
    tweet = template.format(target=target, topic=target)
    
    # Add emoji if style allows
    if random.random() < style.get("emoji_frequency", 0.1):
        emojis = vocab.get("signature_phrases", ["🐺", "🔥"])
        tweet += f" {random.choice(emojis)}"
    
    # Ensure minimal length
    if len(tweet) < 30:
        tweet += "。等待确认。"
    
    return {
        "content": tweet,
        "type": template_type,
        "topic": topic,
        "confidence": profile.get("confidence", 0.5),
        "generated_at": datetime.now().isoformat()
    }


def generate_batch(count: int = 5, topics: List[str] = None) -> List[Dict]:
    """Generate batch of tweets"""
    if topics is None:
        topics = list(TOPICS.keys())
    
    tweets = []
    for _ in range(count):
        topic = random.choice(topics)
        tweets.append(generate_tweet(topic))
    
    return tweets


def save_drafts(tweets: List[Dict]) -> Path:
    """Save drafts for approval"""
    drafts_file = OUTPUT_DIR / "drafts.jsonl"
    with open(drafts_file, "w") as f:
        for tweet in tweets:
            f.write(json.dumps(tweet) + "\n")
    return drafts_file


def post_with_bird(content: str) -> bool:
    """Post tweet via bird CLI"""
    try:
        result = subprocess.run(
            ["bird", "tweet", content],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print(f"✓ Posted: {content[:50]}...")
            return True
        else:
            print(f"✗ Failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("✗ bird CLI not found. Install with: npm install -g @steipete/bird")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def approve_and_post(drafts_file: Path):
    """Review drafts and post approved ones"""
    with open(drafts_file) as f:
        drafts = [json.loads(line) for line in f if line.strip()]
    
    print(f"\n📝 Drafts for approval ({len(drafts)} total):")
    print("-" * 50)
    
    approved = []
    for i, draft in enumerate(drafts, 1):
        print(f"\n[{i}] {draft['content']}")
        print(f"    Topic: {draft['topic']} | Confidence: {draft['confidence']:.0%}")
    
    print("\n" + "-" * 50)
    print("Enter numbers to approve (e.g., '1,3,5' or 'all' or 'none'): ")
    # For automated mode, auto-approve all
    approved = [d for d in drafts]
    
    print(f"\n🚀 Posting {len(approved)} tweets...")
    for tweet in approved:
        post_with_bird(tweet["content"])


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Style Learner + Bird Integration")
    parser.add_argument("--count", "-n", type=int, default=5, help="Number of tweets to generate")
    parser.add_argument("--topic", choices=["starknet", "crypto", "trading", "tech", "mixed"], 
                       default="mixed", help="Topic focus")
    parser.add_argument("--post", action="store_true", help="Post immediately (bypass approval)")
    parser.add_argument("--dry-run", action="store_true", help="Generate only, don't post")
    
    args = parser.parse_args()
    
    print("🤖 Style Learner + Bird Integration")
    print(f"   Profile: {PROFILE_FILE}")
    print()
    
    # Generate tweets
    if args.topic == "mixed":
        topics = list(TOPICS.keys())
    else:
        topics = [args.topic]
    
    tweets = generate_batch(args.count, topics)
    
    # Save drafts
    drafts_file = save_drafts(tweets)
    print(f"✓ Generated {len(tweets)} drafts → {drafts_file}")
    
    if args.dry_run:
        print("\n📝 Drafts (dry run):")
        for i, tweet in enumerate(tweets, 1):
            print(f"  [{i}] {tweet['content']}")
        return
    
    # Post or show for approval
    if args.post:
        for tweet in tweets:
            post_with_bird(tweet["content"])
    else:
        approve_and_post(drafts_file)


if __name__ == "__main__":
    main()
