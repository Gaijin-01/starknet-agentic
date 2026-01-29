#!/usr/bin/env python3
"""
Twitter Link Responder
Usage: python3 twitter_responder.py "<link>"

1. Fetch tweet from link
2. Generate comment + quote
3. Add to post_queue for review/posting
"""

import sys
import json
from datetime import datetime
from pathlib import Path

def process_twitter_link(link: str) -> dict:
    """Process a Twitter link and generate responses."""
    
    # Extract tweet ID from link
    tweet_id = link.split("/")[-1]
    if "twitter.com" in link:
        tweet_id = link.split("/")[-1]
    elif "x.com" in link:
        tweet_id = link.split("/")[-1]
    
    # This is a placeholder - in real implementation, use bird CLI
    # bird fetch <tweet_id>
    
    result = {
        "link": link,
        "tweet_id": tweet_id,
        "timestamp": datetime.now().isoformat(),
        "status": "ready_for_review",
        "comment": f"Interesting perspective on this tweet.",
        "quote": f"Great point! Here's my take on this topic.",
        "action": "comment_and_quote"
    }
    
    return result

def add_to_queue(result: dict, queue_dir: Path = Path("/home/wner/clawd/post_queue/ready")):
    """Add generated content to queue."""
    queue_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"twitter_response_{result['timestamp'].replace(':', '-').replace('.', '-')}.txt"
    filepath = queue_dir / filename
    
    with open(filepath, 'w') as f:
        f.write(json.dumps(result, indent=2))
    
    return filepath

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 twitter_responder.py <twitter_link>")
        print("Example: python3 twitter_responder.py https://twitter.com/user/status/123456")
        sys.exit(1)
    
    link = sys.argv[1]
    print(f"Processing: {link}")
    
    # Process link
    result = process_twitter_link(link)
    
    # Add to queue
    filepath = add_to_queue(result)
    
    print(f"\n✅ Generated response saved to:")
    print(f"   {filepath}")
    print(f"\nComment: {result['comment']}")
    print(f"Quote: {result['quote']}")
    print(f"\nTo review: cat {filepath}")
    print(f"To delete: rm {filepath}")

if __name__ == "__main__":
    main()
