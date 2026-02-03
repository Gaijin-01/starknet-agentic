---
name: twitter-api
description: Native X/Twitter API integration for posting, replying, quoting, and analytics using Twitter API v2.
homepage: https://developer.twitter.com
metadata: {"clawdbot":{"emoji":"🐦","requires":{"python":["requests","dotenv"]},"install":[{"id":"pip","kind":"pip","package":"requests dotenv","bins":["python3 scripts/main.py"],"label":"Install deps (pip)"}]}}
---

# twitter-api

## Overview

Native X/Twitter API integration using Twitter API v2. Provides programmatic access to Twitter operations including posting, replying, quoting, and analytics without browser automation.

**Key Capabilities:**
- Post tweets with media, polls, and reply settings
- Reply to tweets with context tracking
- Quote tweets with custom comments
- Search tweets and track trends
- Manage followers and following
- Schedule posts via queue system
- Rate limit monitoring and retry logic

**Compared to bird CLI:**
| Aspect | twitter-api (native) | bird CLI |
|--------|---------------------|----------|
| Rate limits | Direct control | Abstraction |
| Media upload | Native API | Limited |
| Analytics | Full metrics | Basic |
| Setup | API keys required | Cookie-based |

## Requirements

- Twitter Developer Account with API access
- API Key and API Secret (OAuth 1.0a) OR Bearer Token (App-Only)
- Access Token and Access Token Secret (for user actions)

### Environment Variables

```bash
# OAuth 1.0a (full access)
export TWITTER_API_KEY="your_api_key"
export TWITTER_API_SECRET="your_api_secret"
export TWITTER_ACCESS_TOKEN="your_access_token"
export TWITTER_ACCESS_TOKEN_SECRET="your_access_token_secret"

# OR OAuth 2.0 (app-only, read-only)
export TWITTER_BEARER_TOKEN="your_bearer_token"
```

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    Twitter API Workflow                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Authentication                                          │
│     - Set environment variables                             │
│     - Or pass credentials to TwitterClient                  │
│     - Validate with: python main.py whoami                  │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Operation Selection                                     │
│     ┌─────────────────────────────────────────────────────┐│
│     │  post      │  reply    │  quote    │  search      ││
│     │  delete    │  thread   │  schedule │  mentions    ││
│     └─────────────────────────────────────────────────────┘│
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Response Processing                                     │
│     - JSON output by default                                │
│     - Contains tweet_id, url, metrics                       │
│     - Error handling with codes                             │
└─────────────────────────────────────────────────────────────┘
```

## Installation

```bash
# Clone skill
cd ~/clawd/skills/twitter-api

# Install dependencies
pip install requests python-dotenv

# Configure environment
export TWITTER_API_KEY="..."
export TWITTER_API_SECRET="..."
export TWITTER_ACCESS_TOKEN="..."
export TWITTER_ACCESS_TOKEN_SECRET="..."

# Verify setup
python3 scripts/main.py whoami
```

## Usage

### CLI Commands

```bash
# Post a tweet
python3 scripts/main.py post "Hello, Twitter!"

# Reply to a tweet
python3 scripts/main.py reply <tweet_id> "Great point!"

# Quote a tweet
python3 scripts/main.py quote <tweet_id> --comment "My thoughts"

# Delete a tweet
python3 scripts/main.py delete <tweet_id>

# Get tweet details
python3 scripts/main.py get <tweet_id>

# Search tweets
python3 scripts/main.py search "bitcoin" --limit 10

# Get mentions
python3 scripts/main.py mentions --limit 20

# Post a thread (from file)
python3 scripts/main.py thread tweets.txt

# Schedule a post
python3 scripts/main.py schedule "Scheduled tweet" "2024-01-15T14:00:00"

# List scheduled
python3 scripts/main.py scheduled

# Cancel scheduled
python3 scripts/main.py cancel scheduled_20240115_140000.json

# Check rate limits
python3 scripts/main.py rate
```

### Python API

```python
from scripts.api import TwitterClient, get_client
from scripts.post import TweetPoster, post, reply, quote
from scripts.reply import ReplyManager
from scripts.quote import QuoteManager

# Quick functions
result = post("Hello, Twitter!")
result = reply(tweet_id, "Nice tweet!")
result = quote(tweet_id, "My take")

# Full client
client = get_client()
me = client.get_me()

# High-level poster
poster = TweetPoster()
result = poster.post_with_media(
    "Check this out!",
    media_paths=["/path/to/image.jpg"]
)

# Thread posting
results = poster.post_thread([
    "Tweet 1 of my thread",
    "Tweet 2 with more info",
    "Tweet 3 - the conclusion"
])

# Reply with context
reply_mgr = ReplyManager()
result = reply_mgr.reply_with_context(tweet_id, "I agree!")

# Quote with analysis
quote_mgr = QuoteManager()
result = quote_mgr.quote_with_analysis(
    tweet_id,
    "Here's my analysis",
    include_metrics=True
)
```

## Configuration

### Post Queue Directory

```bash
export POST_QUEUE_DIR="/home/wner/clawd/post_queue"
```

### Rate Limits

Twitter API v2 rate limits (typical):
- POST /2/tweets: 17 requests per 24 hours
- GET /2/tweets: 180 requests per 15 minutes
- GET /2/users/me: 15 requests per 15 minutes

### Error Codes

| Code | Meaning |
|------|---------|
| 401 | Unauthorized - Check API keys |
| 403 | Forbidden - Account issues or rate limit |
| 429 | Rate limited - Wait for reset |
| 400 | Bad request - Check parameters |

## Examples

### Daily Thread

```bash
#!/bin/bash
# daily_thread.sh
cd ~/clawd/skills/twitter-api

python3 scripts/main.py post "🧵 $(date +%B) Crypto Analysis $(date +%Y)"

python3 scripts/main.py reply <PREV_TWEET_ID> "1/ Market Overview"
python3 scripts/main.py reply <PREV_TWEET_ID> "2/ Key Metrics"
python3 scripts/main.py reply <PREV_TWEET_ID> "3/ Outlook"
python3 scripts/main.py reply <PREV_TWEET_ID> "End of thread. Follow for more! 📈"
```

### Auto-Reply to Mentions

```python
from scripts.reply import ReplyManager
from datetime import datetime

reply_mgr = ReplyManager()

# Template-based reply
template = "Thanks for the mention, {author}! 🙏"

result = reply_mgr.reply_to_mentions(
    template=template,
    delay_seconds=30
)
print(f"Replied to {result['success']} mentions")
```

### Competitor Tracking

```python
from scripts.quote import QuoteManager

quote_mgr = QuoteManager()

# Quote competitor tweets with analysis
result = quote_mgr.quote_competitor(
    username="CompetitorAccount",
    comment="Interesting approach, but our solution offers: {tweet_text}",
    max_tweets=3
)
print(f"Quoted {result['success']} competitor tweets")
```

### Scheduled Content Calendar

```python
from scripts.post import TweetPoster
from datetime import datetime

poster = TweetPoster()

# Schedule for optimal times
schedule = [
    ("Morning update", "2024-01-15T08:00:00"),
    ("Afternoon insight", "2024-01-15T13:00:00"),
    ("Evening summary", "2024-01-15T18:00:00"),
]

for text, at in schedule:
    post_time = datetime.fromisoformat(at)
    result = poster.schedule_post(text, post_time)
    print(f"Scheduled: {result}")
```

### Sentiment-Based Auto-Reply

```python
from scripts.api import get_client

client = get_client()

def analyze_sentiment(text):
    # Simple keyword-based (replace with actual NLP)
    positive = ["great", "awesome", "love", "amazing"]
    negative = ["bad", "terrible", "hate", "worst"]
    
    text_lower = text.lower()
    if any(w in text_lower for w in positive):
        return "positive"
    if any(w in text_lower for w in negative):
        return "negative"
    return "neutral"

# Auto-reply based on sentiment
mentions = client.get_mentions(max_results=10)
for mention in mentions:
    sentiment = analyze_sentiment(mention["text"])
    if sentiment == "positive":
        reply = "Thanks for the positive feedback! 🙌"
    elif sentiment == "negative":
        reply = "We appreciate your feedback and will improve."
    else:
        reply = "Thanks for reaching out!"
    
    print(f"Replying to: {mention['text'][:50]}...")
```

## File Structure

```
twitter-api/
├── __init__.py
├── scripts/
│   ├── main.py          # CLI entry point
│   ├── api.py           # TwitterClient (core API)
│   ├── post.py          # TweetPoster (posting)
│   ├── reply.py         # ReplyManager (replies)
│   └── quote.py         # QuoteManager (quotes)
├── data/
│   ├── reply_context.jsonl    # Reply tracking
│   └── quote_history.jsonl    # Quote history
└── SKILL.md
```

## Troubleshooting

### Authentication Failed (401)

```bash
# Verify credentials
echo $TWITTER_API_KEY
echo $TWITTER_ACCESS_TOKEN

# Regenerate tokens in Twitter Developer Portal
# Make sure app has read/write permissions
```

### Rate Limited (429)

```bash
# Check rate limit status
python3 scripts/main.py rate

# Wait for reset (shown in output)
# Or reduce request frequency
```

### Tweet Not Found (404)

```bash
# Verify tweet ID
python3 scripts/main.py get <tweet_id>

# Check if tweet was deleted
# Note: Old tweets may require correct ID format
```

### Media Upload Failed

```bash
# Check file exists
ls -la /path/to/image.jpg

# Supported formats: PNG, JPEG, GIF, WEBP
# Max size: 5MB (images), 15MB (video)
```

### Missing Dependencies

```bash
# Install required packages
pip install requests python-dotenv

# Verify installation
python3 -c "import requests; import dotenv"
```

## Integration with Style Learner

```python
# Generate style-aware content
from style_learner.scripts.main import StyleLearner

learner = StyleLearner()
style = learner.get_profile()

# Generate content in your style
content = learner.generate(
    prompt="Crypto market update",
    style_constraints=style
)

# Post via twitter-api
from scripts.post import post
result = post(content)
```

## Version

- v1.0.0 (2025-01-17): Initial release with full API v2 support
