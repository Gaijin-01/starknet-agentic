#!/usr/bin/env python3
"""
Twitter Response Copy Generator
Usage: python3 twitter_copy_generator.py "<link>"

Generates comment + quote as copyable text for review.
"""

import sys
import re
from datetime import datetime

def extract_tweet_id(link: str) -> str:
    """Extract tweet ID from Twitter/X link."""
    match = re.search(r'(?:twitter\.com|x\.com)/[a-zA-Z0-9_]+/status/(\d+)', link)
    return match.group(1) if match else "unknown"

def generate_response(link: str) -> str:
    """Generate comment + quote for Twitter link."""
    tweet_id = extract_tweet_id(link)
    
    # Placeholder - in real use, would fetch tweet content via bird
    # For now, generates generic templates
    
    return f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐦 TWITTER RESPONSE (ID: {tweet_id})
📎 {link}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💬 COMMENT:
«Interesting perspective! Here's my take on this topic.»

🔁 QUOTE:
«Great point worth highlighting. This aligns with what I've been thinking about [relevant angle].»

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 Copy the text above and post manually.
⏰ Generated: {datetime.now().strftime('%H:%M')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 twitter_copy_generator.py <twitter_link>")
        print("Example: python3 twitter_copy_generator.py https://twitter.com/user/status/123456")
        sys.exit(1)
    
    link = sys.argv[1]
    print(generate_response(link))

if __name__ == "__main__":
    main()
