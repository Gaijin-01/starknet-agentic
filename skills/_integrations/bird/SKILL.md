---
name: bird
description: X/Twitter CLI for reading, searching, posting, and engagement via cookies.
homepage: https://github.com/your-repo/bird
metadata:
  openclaw:
    emoji: "🐦"
    requires:
      bins: ["python3", "curl"]
      python: ["requests", "tqdm"]
    install:
      - kind: pip
        packages: ["requests", "tqdm", "beautifulsoup4"]
        label: "Install dependencies"
---

# bird 🐦

X/Twitter CLI using Twitter cookies for authentication.

## Overview

bird provides command-line access to Twitter/X operations using browser cookies for authentication (no API keys required).

## Features

- Post tweets with media support
- Search tweets and users
- Read timelines and mentions
- Reply and quote tweets
- Follow/unfollow users
- Like and retweet
- Media upload support

## Usage

```bash
# Post a tweet
bird post "Hello from bird!"

# Search tweets
bird search "starknet"

# Read home timeline
bird timeline

# Read mentions
bird mentions

# Follow user
bird follow username

# Like a tweet
bird like <tweet_id>

# Retweet
bird retweet <tweet_id>
```

## Setup

1. Get Twitter cookies (from browser DevTools)
2. Set cookies in environment:
```bash
export BIRD_COOKIES="auth_token=...; ct0=..."
```

## Files

```
bird/
├── scripts/
│   └── main.py           # Main CLI entry point
├── references/
│   └── config.example   # Example configuration
└── SKILL.md
```

## Requirements

- Python 3.10+
- requests
- tqdm
- beautifulsoup4

## License

MIT
