# Style Learner Skill (Bird-based)

Behavior cloning system that learns user's Twitter style and acts via **bird CLI**.

## Overview

Uses bird (X/Twitter CLI) instead of nodriver for all operations:
- **Observer**: Fetches tweets/likes via bird API
- **Analyzer**: Builds style profile from collected data
- **Generator**: Creates content matching user's voice
- **Executor**: Posts/replies via bird CLI

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Style Learner Orchestrator                │
│  main.py — manages modes and coordinates components         │
└─────────────────────────┬───────────────────────────────────┘
                          │
    ┌─────────┬─────────┬─┴─────────┬─────────┐
    ▼         ▼         ▼           ▼         ▼
┌───────┐ ┌───────┐ ┌───────┐ ┌───────────┐ ┌───────────┐
│Observer│ │Analyzer│ │Generator│ │ Executor  │ │  Profile  │
│(bird)  │ │(stats) │ │(templates)│ │ (bird)   │ │  Storage  │
└───────┘ └───────┘ └─────────┘ └───────────┘ └───────────┘
```

## Requirements

- **bird** CLI (already installed)
- **Python 3.10+**
- Twitter cookies in environment (`AUTH_TOKEN`, `CT0`)

## Quick Start

```bash
# Set cookies (if not in ~/.bashrc)
export AUTH_TOKEN="..."
export CT0="..."

# Learn from your tweets
cd ~/clawd/skills/style-learner
python3 scripts/main.py learn --hours 4

# Build profile
python3 scripts/main.py analyze

# Generate content
python3 scripts/main.py generate --type gm

# Assist mode (drafts for approval)
python3 scripts/main.py assist --hours 4
```

## Commands

| Command | Description |
|---------|-------------|
| `learn --hours N` | Fetch tweets/likes via bird and save observations |
| `analyze` | Build style profile from observations |
| `generate --type <type>` | Generate content in your style |
| `assist --hours N` | Generate drafts for approval |
| `post --content "..."` | Post content via bird |
| `reply --tweet <url> --content "..."` | Reply via bird |

## Content Types

- `gm` - Good morning posts
- `price` - Price updates
- `news` - News reactions
- `insight` - Thoughts/opinions
- `reply` - Replies to tweets
- `thread` - Multi-tweet threads

## Data Structure

```
style-learner/
├── scripts/
│   ├── main.py      # Orchestrator
│   ├── observer.py  # Data collection (via bird)
│   ├── analyzer.py  # Profile building
│   ├── generator.py # Content creation
│   └── executor.py  # Bird actions
├── data/
│   └── observations/  # Raw observations (.jsonl)
└── profiles/
    └── style_profile.json  # Learned profile
```

## Style Profile Schema

```json
{
  "persona": {
    "name": "SefirotWatch",
    "tone": ["minimal", "cryptic", "confident"],
    "emoji_style": "sparse",
    "caps_usage": "rare"
  },
  "vocabulary": {
    "frequent": {"higher": 15, "zk": 10, "execution": 8},
    "signature_phrases": ["execution > narratives", "higher 🐺"],
    "emoji_usage": {"🐺": 20, "🔥": 15, "💀": 8},
    "avg_word_count": 12
  },
  "timing": {
    "peak_hours": [8, 9, 13, 21],
    "avg_posts_per_day": 15
  },
  "engagement": {
    "priority_accounts": ["@StarkWareLtd", "@Starknet"],
    "liked_topics": ["starknet", "zk", "defi"]
  }
}
```

## Integration with x-algorithm-optimizer

```bash
# Score your generated content
cd ~/clawd/skills/x-algorithm-optimizer
python3 algorithm_scorer.py --compare

# Get optimal posting strategy
python3 algorithm_scorer.py --strategy
```

## Advantages of Bird-based Approach

| Aspect | Bird-based | Nodriver-based |
|--------|------------|----------------|
| Dependencies | None | Chrome, nodriver |
| Stealth | High | Medium |
| Speed | Fast | Slower |
| Reliability | High | Variable |
| Cookies | Manual setup | Automatic |

## Troubleshooting

### Bird not authenticated
```bash
bird whoami  # Should show your account
# If not, set AUTH_TOKEN and CT0 env vars
```

### No observations found
```bash
# Check data directory
ls -la ~/clawd/skills/style-learner/data/observations/

# Run learn again
python3 scripts/main.py learn --hours 1
```

### Profile not generating
```bash
# Check profile file exists
cat ~/clawd/skills/style-learner/profiles/style_profile.json

# Rebuild profile
python3 scripts/main.py analyze
```

## Files

- `scripts/main.py` - Main entry point
- `scripts/observer.py` - Bird-based data collection
- `scripts/analyzer.py` - Style profile builder
- `scripts/generator.py` - Content generator
- `scripts/executor.py` - Bird CLI wrapper

## Version

- v1.0.0 (2026-01-17): Initial release

