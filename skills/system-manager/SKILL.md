# system-manager

System administration skill for Clawdbot. Manages skills, memory, and services.

## Overview

Provides voice/text commands for system administration:
- Skill management (enable/disable/status)
- Memory operations (backup/restore/clean)
- Service control (restart/status)
- System status and diagnostics

## Quick Start

```bash
# Skill management
python3 scripts/main.py skills list
python3 scripts/main.py skills enable research
python3 scripts/main.py skills disable research

# Memory operations
python3 scripts/main.py memory backup
python3 scripts/main.py memory restore latest
python3 scripts/main.py memory clean

# Service control
python3 scripts/main.py service restart gateway
python3 scripts/main.py service status

# System info
python3 scripts/main.py system status
python3 scripts/main.py system health
```

## Voice Commands

| Command | Action |
|---------|--------|
| "включи скилл research" | Enable research skill |
| "выключи скилл prices" | Disable prices skill |
| "статус скиллов" | List all skills with status |
| "забэкапь память" | Backup memory directory |
| "перезагрузи память" | Reload memory files |
| "очисти память" | Remove old memory files |
| "статус системы" | Show system health |
| "перезапусти гейтвей" | Restart Clawdbot gateway |

## Configuration

Skills are enabled/disabled via `~/.clawdbot/clawdbot.json`:

```json
{
  "skills": {
    "enabled": ["prices", "research", "post-generator"],
    "disabled": ["camsnap", "songsee"]
  }
}
```

## Files

- `scripts/main.py` - Main entry point
