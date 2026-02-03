# Intelligence Skill

## Overview
Comprehensive intelligence gathering automation system. Aggregates signals from X (Twitter), Reddit, Hacker News, and on-chain sources. Produces daily pulses, weekly digests, and content plans.

## Features
- **Multi-source aggregation**: X, Reddit, HN, on-chain (DEXs, whale tracking)
- **Smart filtering**: Relevance scoring, deduplication, sentiment analysis
- **Automated digests**: Daily pulse (8:00, 13:00, 18:00), weekly digest (Monday 9:00), weekly wrap (Friday 20:00)
- **Content scheduling**: Auto-generate content plan from gathered intelligence
- **Whale tracker integration**: Sync with starknet-whale-tracker skill

## Sources
| Source | Type | Update Frequency |
|--------|------|------------------|
| X/Twitter | Social | Every 15 min |
| Reddit | Social | Every 30 min |
| Hacker News | Tech news | Every 30 min |
| DEX Screener | On-chain | Every 5 min |
| Birdeye | On-chain | Every 5 min |
| Whale Tracker | On-chain | Real-time |

---

## Architecture

```
intelligence/
├── SKILL.md                 # This file
├── config.json              # Sources and settings
├── scripts/
│   ├── gather.py            # Multi-source data collection
│   ├── process.py           # Filter, rank, summarize
│   ├── daily_pulse.py       # Morning digest generator
│   ├── weekly_digest.py     # Monday + Friday wrap
│   └── content_plan.py      # Content scheduler
└── data/
    ├── raw/                 # Raw gathered data
    ├── processed/           # Filtered/ranked data
    └── outputs/             # Generated digests
```

---

## Configuration

### config.json

```json
{
  "sources": {
    "twitter": {
      "enabled": true,
      "accounts": ["@CryptoHayes", "@Starknet", "@VitalikButerin"],
      "keywords": ["starknet", "strk", "l2", "zk"],
      "max_results": 50
    },
    "reddit": {
      "enabled": true,
      "subreddits": ["ethfinance", "Starknet", "CryptoCurrency"],
      "max_posts": 20
    },
    "hacker_news": {
      "enabled": true,
      "keywords": ["starknet", "l2", "zero-knowledge"],
      "max_stories": 15
    },
    "onchain": {
      "enabled": true,
      "dexscreener": true,
      "birdeye": true,
      "whale_tracker": true
    }
  },
  "filtering": {
    "min_relevance_score": 0.5,
    "max_items_per_digest": 20,
    "deduplicate": true
  },
  "schedules": {
    "daily_pulse": ["08:00", "13:00", "18:00"],
    "weekly_digest": "09:00 Monday",
    "weekly_wrap": "20:00 Friday"
  }
}
```

---

## Usage

### Gather Intelligence

```bash
cd /home/wner/clawd/skills/intelligence
python scripts/gather.py --all              # Gather from all sources
python scripts/gather.py --twitter           # X/Twitter only
python scripts/gather.py --reddit            # Reddit only
python scripts/gather.py --hn                # Hacker News only
python scripts/gather.py --onchain           # On-chain only
```

### Process & Filter

```bash
python scripts/process.py --input raw/latest.json  # Process raw data
python scripts/process.py --rank                   # Rank by relevance
python scripts/process.py --summarize              # Generate summaries
```

### Daily Pulse

```bash
python scripts/daily_pulse.py              # Generate for today
python scripts/daily_pulse.py --preview    # Preview without saving
python scripts/daily_pulse.py --format txt # Text output
```

### Weekly Digest

```bash
python scripts/weekly_digest.py            # Monday digest
python scripts/weekly_digest.py --wrap     # Friday wrap
python scripts/weekly_digest.py --stats    # Include statistics
```

### Content Plan

```bash
python scripts/content_plan.py             # Generate weekly plan
python scripts/content_plan.py --days 7    # 7-day plan
python scripts/content_plan.py --export    # Export to JSON
```

### All-in-One

```bash
python scripts/pipeline.py --daily         # Full daily pipeline
python scripts/pipeline.py --weekly        # Full weekly pipeline
```

---

## Integration

### Whale Tracker Integration

The intelligence skill integrates with `starknet-whale-tracker` skill:

```python
from scripts.gather import gather_whale_activity

# Get recent whale activity
activity = gather_whale_activity(hours=24)
```

### Research Skill Integration

Uses the `research` skill for deep-dive searches:

```python
from scripts.gather import deep_research

# Research a topic from gathered signals
results = deep_research("Starknet L2 adoption", count=10)
```

---

## Output Formats

### Daily Pulse Example

```
🌅 DAILY PULSE | 2026-02-02

📈 TOP SIGNALS
1. [Twitter] @VitalikButerin: "L2 adoption accelerating..."
   Score: 0.92 | Sentiment: Bullish
   
2. [Reddit] r/ethfinance: "Starknet governance proposal..."
   Score: 0.87 | Sentiment: Neutral

3. [HN] "Starknet's approach to MEV protection"
   Score: 0.85 | Sentiment: Positive

🐋 WHALE ACTIVITY
• 0x1234...: Bought 50K STRK ($42K)
• 0x5678...: Transferred 1M USDC

📊 MARKET PULSE
• STRK: $0.84 (+2.3%)
• ETH: $3,240 (+1.1%)
• TVL: $892M (+4.2%)

📅 SCHEDULED CONTENT
• Thread: "L2 adoption metrics"
• Post: "Whale watch update"
```

---

## Cron Jobs

| Job | Schedule | Command |
|-----|----------|---------|
| daily-pulse-morning | 0 8 * * * | `python daily_pulse.py` |
| daily-pulse-noon | 0 13 * * * | `python daily_pulse.py` |
| daily-pulse-evening | 0 18 * * * | `python daily_pulse.py` |
| weekly-digest | 0 9 * * 1 | `python weekly_digest.py` |
| weekly-wrap | 0 20 * * 5 | `python weekly_digest.py --wrap` |
| gather-all | */15 * * * * | `python gather.py --all` |

---

## API Reference

### Gather Module

```python
from scripts.gather import (
    gather_twitter,
    gather_reddit,
    gather_hacker_news,
    gather_onchain,
    gather_all
)

# Gather from specific source
twitter_data = await gather_twitter(accounts=["@CryptoHayes"], keywords=["starknet"])
reddit_data = await gather_reddit(subreddits=["ethfinance"], limit=20)
hn_data = await gather_hacker_news(keywords=["l2", "zk"], limit=15)
onchain_data = await gather_onchain(dexscreener=True, whale_tracker=True)
```

### Process Module

```python
from scripts.process import (
    filter_relevance,
    rank_signals,
    summarize,
    deduplicate
)

# Filter by relevance score
filtered = filter_relevance(data, min_score=0.5)

# Rank by multiple factors
ranked = rank_signals(filtered, weights={"relevance": 0.4, "engagement": 0.3, "recency": 0.3})

# Generate summary
summary = summarize(ranked, max_items=10)
```

### Output Storage

- Raw data: `data/raw/{timestamp}.json`
- Processed data: `data/processed/{timestamp}.json`
- Daily pulse: `data/outputs/daily/{date}.md`
- Weekly digest: `data/outputs/weekly/{year}/{week}.md`
- Content plan: `data/outputs/content/{date}.json`

---

## Troubleshooting

```bash
# Check configuration
python scripts/validate_config.py

# Debug gathering
python scripts/gather.py --all --debug

# Test whale tracker connection
python scripts/gather.py --onchain --debug

# View recent outputs
ls -la data/outputs/daily/
cat data/outputs/daily/2026-02-02.md
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Twitter API errors | Check `TWITTER_API_KEY` env var |
| Whale tracker unavailable | Verify `starknet-whale-tracker` skill is running |
| No data from source | Check source enable flag in config.json |
| Duplicate items | Enable `deduplicate` in filtering config |

---

## Environment Variables

```bash
# Twitter/X API
export TWITTER_API_KEY="your-api-key"
export TWITTER_API_SECRET="your-api-secret"
export TWITTER_ACCESS_TOKEN="your-access-token"
export TWITTER_ACCESS_SECRET="your-access-secret"

# Reddit API
export REDDIT_CLIENT_ID="your-client-id"
export REDDIT_CLIENT_SECRET="your-client-secret"

# Whale Tracker
export WHALE_TRACKER_RPC_URL="https://starknet-mainnet.example.com"
```

---

## Dependencies

```
requirements.txt:
- aiohttp>=3.9.0
- python-dateutil>=2.8.0
- praw>=7.7.0
- tweepy>=4.14.0
- httpx>=0.25.0
```

---

## Version

- v1.0.0 (2026-02-02): Initial release
  - Multi-source gathering (X, Reddit, HN, on-chain)
  - Relevance filtering and ranking
  - Daily pulse and weekly digest generation
  - Content planning automation
  - Whale tracker integration
