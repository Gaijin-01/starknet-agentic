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

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                 Style Learner Workflow                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 1: Data Collection (Observer)                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ bird fetch-tweets --hours 4                          │    │
│  │ bird fetch-likes --hours 2                           │    │
│  │ → Raw observations saved to data/observations/       │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 2: Profile Building (Analyzer)                       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Parse observations                                    │    │
│  │ Calculate vocabulary frequency                       │    │
│  │ Extract emoji usage patterns                         │    │
│  │ Analyze timing (post times, engagement peaks)        │    │
│  │ → profiles/style_profile.json                        │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 3: Content Generation (Generator)                    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Load profile                                         │    │
│  │ Select template based on content type                │    │
│  │ Apply vocabulary and emoji preferences               │    │
│  │ Match tone (minimal, cryptic, confident, etc.)       │    │
│  │ → Generated content (draft)                          │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 4: Execution (Executor)                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ ASSIST mode: User reviews draft → approves/edits    │    │
│  │ AUTO mode: Direct post via bird CLI                  │    │
│  │ bird post "content"                                  │    │
│  │ bird reply <url> "content"                           │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Step-by-Step Execution Flow

**Step 1: Initialize Learning**
```bash
# Observer fetches data
python3 scripts/main.py learn --hours 4

# What happens:
# 1. bird get-tweets --limit 1000
# 2. bird get-likes --limit 500
# 3. Save to data/observations/tweets_YYYYMMDD.jsonl
# 4. Save to data/observations/likes_YYYYMMDD.jsonl
```

**Step 2: Build Profile**
```bash
# Analyzer processes observations
python3 scripts/main.py analyze

# What happens:
# 1. Load all observations from data/observations/
# 2. Tokenize and count words
# 3. Calculate emoji frequency
# 4. Detect signature phrases
# 5. Analyze posting times
# 6. Output: profiles/style_profile.json
```

**Step 3: Generate Content**
```bash
# Generator creates content
python3 scripts/main.py generate --type gm

# What happens:
# 1. Load profiles/style_profile.json
# 2. Select template for "gm" type
# 3. Replace placeholders with learned vocabulary
# 4. Apply emoji preference (🐺, 🔥)
# 5. Adjust tone (fragmentation, irony, etc.)
# 6. Output: Draft content
```

**Step 4: Post or Assist**
```bash
# Assist mode (review before posting)
python3 scripts/main.py assist --hours 2

# What happens:
# 1. Generate drafts
# 2. Wait for user approval
# 3. bird post approved content

# Auto mode (direct posting)
python3 scripts/main.py auto --hours 4

# What happens:
# 1. Generate content
# 2. bird post immediately
# 3. Log to post_queue/
```

### Configuration Files

```yaml
# config/style-learner.yaml
learn:
  tweets_limit: 1000
  likes_limit: 500
  save_path: data/observations/

profile:
  output_path: profiles/style_profile.json
  min_occurrences: 3  # Min word frequency

generate:
  default_type: gm
  templates_path: assets/templates/
  max_retries: 3

execute:
  mode: assist  # or auto
  require_approval: true
  bird_path: /usr/local/bin/bird
```

### File Processing

```
Input → Processing → Output

tweets.jsonl → observer.py → observations/tweets_YYYYMMDD.jsonl
likes.jsonl  → observer.py → observations/likes_YYYYMMDD.jsonl

observations/*.jsonl → analyzer.py → profiles/style_profile.json

style_profile.json → generator.py → content/drafts/*.txt

drafts/*.txt → executor.py → bird post/reply
```

### Error Handling

| Error | Handling |
|-------|----------|
| Bird not authenticated | Log error, exit with auth instructions |
| No observations found | Exit with learn step required |
| Profile file missing | Exit with analyze step required |
| Generation failed | Fallback to default template |
| Post failed | Retry 3x, then queue for manual |

### Performance Considerations

- **Observer**: ~100 tweets/min (bird rate limits)
- **Analyzer**: < 1s for 1000 tweets
- **Generator**: < 0.5s per content piece
- **Executor**: ~1s per post (bird API limits)

### Integration Points

| Component | Interface |
|-----------|-----------|
| bird CLI | Twitter API access |
| x-algorithm-optimizer | Content scoring, timing |
| post_queue | Queued posts |
| MEMORY.md | Long-term preferences |

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

