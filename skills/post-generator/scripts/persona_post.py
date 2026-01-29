#!/usr/bin/env python3
"""
Post Generator with Persona Vocabulary
Generates posts using learned vocabulary and tone.
"""

import json
from pathlib import Path

# Persona profile
PROFILE = {
    "tone": ["minimal", "cryptic", "confident"],
    "vocabulary": {
        "frequent": ["higher", "execution", "patience"],
        "signature_phrases": []
    },
    "emoji_usage": {"🐺": 3, "🔥": 2},
    "avg_word_count": 10
}

def generate_post(tweet_content, post_type="quote"):
    """Generate post in persona style using learned vocabulary."""
    
    # Extract key info from tweet
    keywords = ["Loot Survivor", "PVP", "Starkware", "Community"]
    
    # Use learned vocabulary
    words = PROFILE["vocabulary"]["frequent"]
    emojis = list(PROFILE["emoji_usage"].keys())
    
    if post_type == "quote":
        # Quote style: short, add value
        templates = [
            f"{words[0].capitalize()} {words[1]}. {emojis[1]}",
            f"Execution {words[2]}. {emojis[0]}",
            f"New development. Thoughts? {emojis[0]}",
            f"{words[0].capitalize()} soon. {emojis[1]}",
        ]
    else:
        # Timeline post style
        templates = [
            f"just in: new development. thoughts? {emojis[0]}",
            f"{words[0].capitalize()} vibes only. {emojis[1]} {emojis[0]}",
            f"Building in silence. {words[1]} {words[2]}. {emojis[0]}",
        ]
    
    return templates[0]  # Return first template for now

def main():
    import sys
    tweet = sys.argv[1] if len(sys.argv) > 1 else "Starknet update"
    post_type = sys.argv[2] if len(sys.argv) > 2 else "quote"
    
    post = generate_post(tweet, post_type)
    
    # Output for queue
    result = {
        "type": post_type,
        "original_tweet": tweet,
        "content": post,
        "persona_used": PROFILE["persona"]["name"] if "persona" in PROFILE else "SefirotWatch"
    }
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
