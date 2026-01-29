---
name: ct-intelligence
description: Competitor tracking, trend detection, and sentiment analysis for Crypto Twitter (CT) using X API and NLP.
homepage: https://github.com
metadata: {"clawdbot":{"emoji":"🕵️","requires":{"python":["httpx"]},"install":[{"id":"pip","kind":"pip","package":"httpx","bins":["python3 scripts/main.py"],"label":"Install deps (pip)"}]}}
---

# ct-intelligence

## Overview

CT Intelligence provides competitor tracking, trend detection, and sentiment analysis for Crypto Twitter. Monitor key accounts, detect emerging trends, and analyze market sentiment.

**Key Capabilities:**
- **Account Tracking:** Monitor competitor accounts and influencers
- **Trend Detection:** Identify emerging keywords and topics
- **Sentiment Analysis:** Analyze tweet sentiment (positive/negative/neutral)
- **Alert System:** Get notified of important events
- **Competitor Monitoring:** Track and compare competitor activity

**Data Sources:**
- X API v2 (via twitter-api skill)
- Keyword analysis and NLP
- Custom sentiment classifiers

## Requirements

- Python 3.10+
- httpx for async HTTP
- twitter-api skill (for X API access)

### Environment Variables

```bash
# Optional rate limit bypass
export TWITTER_BEARER_TOKEN="..."

# Data directory
export CT_DATA_DIR="/home/wner/clawd/skills/ct-intelligence/data"
```

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                 CT Intelligence Workflow                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Account Setup                                           │
│     - Add competitor accounts to track                      │
│     - Configure monitoring frequency                        │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Data Collection                                         │
│     - Fetch tweets via twitter-api                          │
│     - Store in local data/ directory                        │
│     - Track historical activity                             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Analysis                                                │
│     ┌─────────────────────────────────────────────────────┐ │
│     │  TRENDS          │  SENTIMENT     │  COMPETITORS   │ │
│     │  Keywords        │  Positive/Neg  │  Comparison    │ │
│     │  Volume          │  Keywords      │  Activity      │ │
│     └─────────────────────────────────────────────────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Alerts                                                  │
│     - Slack/Telegram notifications                          │
│     - Trend detection                                       │
│     - Sentiment shifts                                      │
└─────────────────────────────────────────────────────────────┘
```

## Installation

```bash
# Clone skill
cd ~/clawd/skills/ct-intelligence

# Install dependencies
pip install httpx

# Configure (optional)
export TWITTER_BEARER_TOKEN="..."

# Test setup
python3 scripts/main.py status
```

## Usage

### CLI Commands

```bash
# Account Management
python3 scripts/main.py track --add VitalikButerin    # Add account
python3 scripts/main.py track --remove zhusu           # Remove account
python3 scripts/main.py track --list                   # List tracked
python3 scripts/main.py track --fetch VitalikButerin   # Fetch tweets

# Trend Detection
python3 scripts/main.py trends --hours 24              # Detect trends (24h)
python3 scripts/main.py trends --limit 20              # Top 20 trends

# Sentiment Analysis
python3 scripts/main.py sentiment --text "Bitcoin moon!"  # Analyze text
python3 scripts/main.py sentiment --text "Another rug..." --json  # JSON output

# Alert Management
python3 scripts/main.py alert --type trend --message "AI agents trending"  # Send alert
python3 scripts/main.py alert --list                                           # List alerts

# Status
python3 scripts/main.py status  # Show system status
```

### Python API

```python
from scripts.tracker import Tracker
from scripts.sentiment import SentimentAnalyzer
from scripts.alerts import AlertManager, AlertType

# Track accounts
tracker = Tracker()
tracker.add_account("VitalikButerin")
tracker.add_account("zhusu")
tracker.add_account("CryptoHayes")

accounts = tracker.get_accounts()
print(f"Tracking {len(accounts)} accounts")

# Fetch tweets
tweets = tracker.fetch_tweets("VitalikButerin", limit=10)
print(f"Fetched {len(tweets)} tweets")

# Detect trends
trends = tracker.detect_trends(hours=24)
print("Top trends:")
for trend in trends[:5]:
    print(f"  - {trend.keyword}: {trend.count}")

# Sentiment analysis
analyzer = SentimentAnalyzer()
result = analyzer.analyze_text("Bitcoin is going to the moon! 🚀")
print(f"Sentiment: {result.sentiment} ({result.score:+.2f})")

# Analyze account sentiment
account_sentiment = analyzer.get_account_sentiment("VitalikButerin", tweets)
print(f"Account sentiment: {account_sentiment['sentiment']}")

# Alert management
alerts = AlertManager()
alerts.register_handler(AlertType.TREND, lambda a: print(f"Alert: {a.message}"))
alerts.send_alert(AlertType.TREND, "AI agents trending!", priority=4)
```

## Sentiment Analysis

### Keywords

**Positive:**
- moon, lambo, profit, win, gain, bullish
- great, amazing, love, best, awesome, excited

**Negative:**
- dump, rug, scam, loss, fail, bearish
- bad, terrible, hate, worst, worried

### Example Output

```json
{
  "sentiment": "positive",
  "score": 0.75,
  "keywords": ["moon", "bullish", "gain"],
  "confidence": 0.8
}
```

## Alert Types

| Type | Description | Priority |
|------|-------------|----------|
| mention | New mention detected | 3 |
| trend | Trending keyword detected | 4 |
| competitor | Competitor activity | 3 |
| sentiment | Sentiment shift | 4 |
| volume | Unusual activity volume | 5 |

## File Structure

```
ct-intelligence/
├── __init__.py
├── scripts/
│   ├── main.py          # CLI entry point
│   ├── tracker.py       # Account tracking
│   ├── sentiment.py     # Sentiment analysis
│   └── alerts.py        # Alert management
└── data/
    └── tracked_accounts.json
```

## Integration with twitter-api

```python
# Combined workflow
from scripts.tracker import Tracker
from scripts.sentiment import SentimentAnalyzer
from scripts.alerts import AlertManager, AlertType

tracker = Tracker()
analyzer = SentimentAnalyzer()
alerts = AlertManager()

# Fetch and analyze
tweets = tracker.fetch_tweets("competitor_account", limit=20)
sentiment = analyzer.analyze_tweets(tweets)

# Alert on negative sentiment shift
if sentiment["sentiment"] == "negative" and sentiment["score"] < -0.3:
    alerts.send_alert(
        AlertType.SENTIMENT,
        f"Negative sentiment detected for competitor: {sentiment['score']}",
        priority=5
    )
```

## Troubleshooting

### No Tweets Fetched

```bash
# Check twitter-api setup
cd ../twitter-api && python3 scripts/main.py whoami

# Verify credentials
echo $TWITTER_BEARER_TOKEN
```

### Sentiment Not Detected

```bash
# Check text length (minimum 10 chars)
python3 scripts/main.py sentiment --text "Short"

# Try with more text
python3 scripts/main.py sentiment --text "This is a detailed analysis of the market sentiment"
```

### Alert Not Received

```bash
# Check handler registration
python3 scripts/main.py alert --list

# Verify alert type matches handler
```

## Examples

### Daily Competitor Report

```bash
#!/bin/bash
# daily_report.sh
cd ~/clawd/skills/ct-intelligence

echo "=== CT Intelligence Report ==="
echo "Tracked accounts:"
python3 scripts/main.py track --list

echo -e "\nTop trends:"
python3 scripts/main.py trends --hours 24 --limit 5
```

### Auto-Alert on Sentiment Shift

```python
from scripts.tracker import Tracker
from scripts.sentiment import SentimentAnalyzer
from scripts.alerts import AlertManager, AlertType

tracker = Tracker()
analyzer = SentimentAnalyzer()
alerts = AlertManager()

# Setup alert handler
def on_sentiment_alert(alert):
    print(f"🚨 {alert.message}")
    # Could also send to Slack/Telegram

alerts.register_handler(AlertType.SENTIMENT, on_sentiment_alert)

# Monitor competitors
for account in tracker.get_accounts():
    tweets = tracker.fetch_tweets(account, limit=50)
    sentiment = analyzer.analyze_tweets(tweets)
    
    # Alert on significant negative sentiment
    if sentiment["score"] < -0.5:
        alerts.send_alert(
            AlertType.SENTIMENT,
            f"Negative sentiment spike for @{account}: {sentiment['score']}",
            priority=5
        )
```

## Version

- v1.0.0 (2026-01-29): Initial release
