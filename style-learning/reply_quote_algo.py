#!/usr/bin/env python3
"""
Reply & Quote Generator with X-Algorithm Optimization
Integrates style-learner profile + X algorithm scoring.
"""

import json
import subprocess
import random
from pathlib import Path
from datetime import datetime

PROFILE_FILE = Path("/home/wner/clawdbot/skills/style-learner/data/profiles/style_profile.json")
OUTPUT_DIR = Path("/home/wner/clawd/style-learning")

# X-Algorithm Weights (from x-algorithm open source)
ALGO_WEIGHTS = {
    "reply": 30.0,
    "quote": 25.0,
    "repost": 10.0,
    "like": 1.0,
    "follow": 50.0,
}

# Content optimization factors
CONTENT_FACTORS = {
    "question": 1.5,           # Questions trigger replies
    "short": 1.2,              # Short = quick read = more engagement
    "conversational": 1.3,     # Conversational = more replies
    "controversial": 1.4,      # Controversial = discussion (but risky)
    "data_driven": 1.3,        # Data = credibility = shares
    "call_to_action": 1.2,     # CTA = action
}


def load_profile():
    with open(PROFILE_FILE) as f:
        return json.load(f)


def calculate_algorithm_score(text: str, action_type: str) -> float:
    """Calculate X-algorithm score for content"""
    base_weight = ALGO_WEIGHTS.get(action_type, 1.0)
    score = base_weight
    
    text_lower = text.lower()
    
    # Content factors
    if "?" in text:
        score *= CONTENT_FACTORS["question"]
    if len(text) < 80:
        score *= CONTENT_FACTORS["short"]
    if any(word in text_lower for word in ["you", "we", "this", "it"]):
        score *= CONTENT_FACTORS["conversational"]
    if any(word in text_lower for word in ["lfg", "🔥", "🐺", "grab", "observed"]):
        score *= 1.2  # Signature style boost
    
    return round(score, 1)


def generate_reply_options(content: str, author: str) -> List[Dict]:
    """Generate reply options with algorithm scoring"""
    profile = load_profile()
    vocab = profile.get("vocabulary", {})
    signature_words = vocab.get("frequent_words", [])
    
    # Reply templates optimized for engagement
    templates = [
        {"text": "This. 🐺", "type": "short_confirm"},
        {"text": "Lfg", "type": "signal"},
        {"text": "Under the radar.", "type": "insight"},
        {"text": "Grab it.", "type": "cta"},
        {"text": "Good spot.", "type": "confirmation"},
        {"text": "Observed.", "type": "minimal"},
        {"text": "Clear setup.", "type": "analysis"},
        {"text": "Good read.", "type": "approval"},
        {"text": "Yep.", "type": "minimal"},
        {"text": "Standard.", "type": "confident"},
        {"text": "Key level.", "type": "analysis"},
        {"text": "Remember this.", "type": "value"},
        {"text": "Noted.", "type": "minimal"},
    ]
    
    options = []
    for t in templates:
        score = calculate_algorithm_score(t["text"], "reply")
        options.append({
            "text": t["text"],
            "type": t["type"],
            "score": score,
            "action": "reply"
        })
    
    # Sort by score
    options.sort(key=lambda x: x["score"], reverse=True)
    return options[:5]


def generate_quote_options(content: str, author: str) -> List[Dict]:
    """Generate quote options with algorithm scoring"""
    # Quote needs value-add to trigger engagement
    templates = [
        {"text": "Remember this.", "type": "value_add"},
        {"text": "This.", "type": "short_confirm"},
        {"text": "Got it.", "type": "minimal"},
        {"text": "Key level.", "type": "analysis"},
        {"text": "Noted.", "type": "minimal"},
        {"text": "Focus on this.", "type": "cta"},
        {"text": "Important.", "type": "emphasis"},
        {"text": "Context.", "type": "context"},
    ]
    
    options = []
    for t in templates:
        score = calculate_algorithm_score(t["text"], "quote")
        options.append({
            "text": t["text"],
            "type": t["type"],
            "score": score,
            "action": "quote"
        })
    
    options.sort(key=lambda x: x["score"], reverse=True)
    return options[:5]


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
            pass
    return {"content": "Tweet content", "author": "unknown"}


def like_tweet(url: str) -> bool:
    """Like tweet via browser automation (placeholder)"""
    print(f"⚠️  Like not implemented. URL: {url}")
    return False


def show_approval(replies: List[Dict], quotes: List[Dict], tweet_url: str):
    """Show options with scores for approval"""
    print("\n" + "="*60)
    print(f"📝 OPTIONS FOR APPROVAL (Algorithm Optimized)")
    print("="*60)
    
    print(f"\n🔗 Tweet: {tweet_url}")
    
    print(f"\n🔹 REPLIES (score = {ALGO_WEIGHTS['reply']} base × factors):")
    for i, r in enumerate(replies[:3], 1):
        print(f"  [{i}] {r['text']:<20} [score: {r['score']}]")
    
    print(f"\n🔹 QUOTES (score = {ALGO_WEIGHTS['quote']} base × factors):")
    for i, q in enumerate(quotes[:3], 1):
        print(f"  [{i}] {q['text']:<20} [score: {q['score']}]")
    
    print("\n" + "-"*60)
    print("Commands: 'r1', 'r2', 'r3', 'q1', 'q2', 'q3', 'rq11', 'rq12', 'skip'")
    print("-"*60)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Algorithm-Optimized Reply & Quote")
    parser.add_argument("url", help="Tweet URL")
    parser.add_argument("--like", action="store_true", help="Like the tweet")
    parser.add_argument("--dry-run", action="store_true", help="Show options only")
    
    args = parser.parse_args()
    
    print(f"🔗 Processing: {args.url}")
    
    # Load tweet
    tweet = load_tweet(args.url)
    content = tweet.get("content", "Tweet content")
    author = tweet.get("author", "unknown")
    author_name = author.get("username", "unknown") if isinstance(author, dict) else str(author)
    
    print(f"👤 Author: {author_name}")
    print(f"📄 Content: {content[:80]}...")
    
    # Like if requested
    if args.like:
        like_tweet(args.url)
    
    # Generate options with scoring
    replies = generate_reply_options(content, author_name)
    quotes = generate_quote_options(content, author_name)
    
    show_approval(replies, quotes, args.url)
    
    if args.dry_run:
        return
    
    # Auto-approve best reply for now
    best_reply = replies[0] if replies else None
    best_quote = quotes[0] if quotes else None
    
    print(f"\n✅ Best option: reply='{best_reply['text']}' (score: {best_reply['score']})")


if __name__ == "__main__":
    main()
