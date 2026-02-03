# Queue Manager Skill

## Overview
100% universal file queue manager. Works for any domain without modification.

## Operations
- `list` - Show queue contents
- `add` - Add item to queue
- `move` - Move item between states (ready → posted → failed)
- `clear` - Clear old items
- `stats` - Queue statistics

## Usage
```bash
# List ready posts
python scripts/queue_manager.py list --state ready

# List all
python scripts/queue_manager.py list --all

# Add content to queue
python scripts/queue_manager.py add --content "your post here"

# Move to posted
python scripts/queue_manager.py move --file post_20260121_1200.txt --to posted

# Clear old (>7 days)
python scripts/queue_manager.py clear --older-than 7

# Stats
python scripts/queue_manager.py stats
```

## Directory Structure
```
~/clawd/post_queue/
├── ready/     # Posts waiting to be published
├── posted/    # Successfully published
├── failed/    # Failed to publish
└── drafts/    # Work in progress
```

## Config
```yaml
queue:
  base_dir: "~/clawd/post_queue"
  subdirs:
    ready: "ready"
    posted: "posted"
    failed: "failed"
```

## Troubleshooting

```bash
# Check queue directories
ls -la ~/clawd/post_queue/

# Debug mode
python scripts/queue_manager.py list --all --debug

# Stats
python scripts/queue_manager.py stats
```

## Version

- v1.0.0 (2026-01-17): Initial release

    drafts: "drafts"
  max_queue_size: 50
  retention_days: 7
```
