# publisher

Unified content publishing skill. Merges post-generator, queue-manager, twitter-api, and x-algorithm-optimizer.

## Overview

**Merged Skills:**
- `post-generator` → template-based content creation
- `queue-manager` → scheduling and queue management
- `twitter-api` → X/Twitter API integration
- `x-algorithm-optimizer` → timing and scoring optimization

## Architecture

```
publisher/
├── main.py           # Unified entry point
├── templates/        # Content templates
├── scheduler/        # Queue management
├── api/              # Twitter API wrapper
├── optimizer/        # Timing/score optimization
├── config.yaml       # Configuration
└── SKILL.md
```

## Usage

```bash
# Generate post from template
python3 scripts/main.py generate --type gm
python3 scripts/main.py generate --type news --headline "Starknet hits $1B TVL"

# Post to X
python3 scripts/main.py post "gm 🐺 zk summer loading..."

# Schedule post
python3 scripts/main.py schedule "Content" "2026-01-31T09:00:00"

# Check queue
python3 scripts/main.py queue --status

# Optimize timing
python3 scripts/main.py optimize --best-time
```

## API

```python
from publisher import Publisher

pub = Publisher()

# Generate
content = pub.generate(type="gm", context="starknet")

# Post
result = pub.post(content)

# Schedule
pub.schedule(content, at="2026-01-31T09:00:00")
```

## Templates

| Type | Description |
|------|-------------|
| gm | Good morning post |
| news | News reaction |
| price | Price update |
| insight | Deep thought |
| thread | Multi-tweet thread |

## Configuration

`config.yaml`:
```yaml
persona:
  name: "SefirotWatch"
  voice: "minimal"

scheduler:
  max_queue: 50
  auto_post: false

optimizer:
  peak_hours: [8, 9, 13, 21]
  avoid_hours: [2, 3, 4, 5]
```

## Migration

This skill was consolidated from:
- skills/post-generator (v1.0.0)
- skills/queue-manager (v1.0.0)
- skills/twitter-api (v1.0.0)
- skills/x-algorithm-optimizer (v1.0.0)

Old skills kept as aliases for backward compatibility.
