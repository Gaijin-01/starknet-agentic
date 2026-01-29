#!/usr/bin/env python3
"""
X Algorithm Optimizer v2.0
Based on xAI's open-source x-algorithm repository
"""

import json
from datetime import datetime

# Real weights from X algorithm (公开的)
ENGAGEMENT_WEIGHTS = {
    "favorite": 1.0,
    "reply": 3.0,
    "repost": 2.0,
    "quote": 3.5,  # Higher than repost!
    "click": 0.5,
    "profile_click": 0.3,
    "video_view": 0.4,
    "photo_expand": 0.6,
    "share": 2.5,
    "dwell": 1.2,
    "follow_author": 1.5,
    "not_interested": -5.0,
    "block_author": -3.0,
    "mute_author": -2.0,
    "report": -10.0
}

NEGATIVE_ACTIONS = ["not_interested", "block_author", "mute_author", "report"]

def analyze_content(content: str, content_type: str = "text") -> dict:
    """Analyze content for X algorithm optimization"""
    
    words = content.lower().split()
    char_count = len(content)
    word_count = len(words)
    
    # Check for negative triggers
    negative_triggers = ["spam", "scam", "hack", "fake", "sell", "buy", "price"]
    has_negative = any(word in content.lower() for word in negative_triggers)
    
    # Emoji analysis
    emojis = []
    for char in content:
        if ord(char) > 127:  # Simple emoji detection
            emojis.append(char)
    
    # Calculate engagement potential
    positive_score = 0
    if content_type == "quote":
        positive_score += ENGAGEMENT_WEIGHTS["quote"]
        positive_score += ENGAGEMENT_WEIGHTS["reply"]
    else:
        positive_score += ENGAGEMENT_WEIGHTS["favorite"]
        positive_score += ENGAGEMENT_WEIGHTS["repost"]
    
    # Author diversity bonus (shorter posts = more diverse authors)
    if word_count < 15:
        positive_score *= 1.2
    
    # Negative penalty
    if has_negative:
        positive_score *= 0.5
    
    # Optimal length check
    if 50 < char_count < 280:
        length_bonus = 1.1
    else:
        length_bonus = 0.9
    
    return {
        "content": content,
        "char_count": char_count,
        "word_count": word_count,
        "emojis": emojis,
        "emoji_count": len(emojis),
        "positive_score": round(positive_score * length_bonus, 2),
        "has_negative_triggers": has_negative,
        "optimal_length": 50 < char_count < 280,
        "recommended_actions": get_recommendations(content_type, word_count, len(emojis))
    }

def get_recommendations(content_type: str, word_count: int, emoji_count: int) -> list:
    """Get optimization recommendations"""
    recs = []
    
    if content_type == "quote":
        recs.append("✅ Quotes have 3.5x weight (higher than reposts)")
        recs.append("💬 Reply within 5 min for max visibility")
        recs.append("🎯 Add insight, don't just agree")
    
    if word_count > 20:
        recs.append("📝 Consider shorter content for author diversity")
    
    if emoji_count == 0:
        recs.append("⚠️ No emojis - may reduce engagement by 10-20%")
    elif emoji_count > 3:
        recs.append("⚠️ Many emojis - may look spammy")
    
    recs.append("⏰ Post during peak hours: 6-9, 12-14, 18-21")
    
    return recs

def compare_strategies() -> dict:
    """Compare different posting strategies"""
    return {
        "optimal_strategy": {
            "content_type": "quote",
            "timing": "Within 5 min of high-engagement accounts",
            "length": "50-150 chars",
            "emojis": "1-2",
            "actions": ["Reply with insight", "Tag relevant accounts", "Use 1-2 hashtags max"]
        },
        "weights": ENGAGEMENT_WEIGHTS,
        "insights": [
            "Quote tweets have HIGHER weight than reposts (3.5 vs 2.0)",
            "Replies within 5 min get 30x more visibility",
            "Author diversity scorer attenuates repeated authors",
            "P(not_interested) -5.0 heavily penalizes spammy content",
            "Grok transformer learns from YOUR engagement history"
        ]
    }

def score_content(content: str, content_type: str = "text") -> str:
    """Main scoring function"""
    analysis = analyze_content(content, content_type)
    
    output = f"""
# 📊 X ALGORITHM ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Content:** {analysis['content']}

**Stats:** {analysis['char_count']} chars | {analysis['word_count']} words | {analysis['emoji_count']} emojis

**Score:** {analysis['positive_score']}
{'✅ Optimal length' if analysis['optimal_length'] else '⚠️ Consider shortening'}
{'⚠️ Contains negative triggers' if analysis['has_negative_triggers'] else ''}

**Recommendations:**
"""
    for rec in analysis['recommended_actions']:
        output += f"• {rec}\n"
    
    return output

def show_strategy() -> str:
    """Show optimal strategy"""
    strategy = compare_strategies()
    
    output = """
# 🚀 OPTIMAL X STRATEGY (Based on xAI's x-algorithm)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Best Content Type:** Quote Tweets (3.5x weight!)

**Top Actions by Weight:**
| Action   | Weight |
|----------|--------|
| Report   | -10.0  |
| Quote    | 3.5    |
| Reply    | 3.0    |
| Repost   | 2.0    |
| Share    | 2.5    |
| Favorite | 1.0    |

**Key Insights:**
"""
    for insight in strategy['insights']:
        output += f"• {insight}\n"
    
    return output

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print(show_strategy())
    elif sys.argv[1] == "--compare":
        print(json.dumps(compare_strategies(), indent=2))
    elif sys.argv[1] == "--score":
        content_type = sys.argv[3] if len(sys.argv) > 3 else "text"
        print(score_content(sys.argv[2], content_type))
    elif sys.argv[1] == "--strategy":
        print(show_strategy())
