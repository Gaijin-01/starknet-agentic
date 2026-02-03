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

## Workflow

The system-manager skill operates as follows:

```
1. User issues command (voice or text)
2. Parser determines command type (skills/memory/service/system)
3. SystemManager executes requested operation
4. Result returned to user (text response)
```

### Command Flow

| Input Type | Parser | Handler | Output |
|------------|--------|---------|--------|
| `skills enable research` | argparse | `cmd_skills_enable()` | Status message |
| `забэкапь память` | Voice parser | `cmd_memory_backup()` | Backup confirmation |
| `перезапусти гейтвей` | Voice parser | `cmd_service_restart()` | Restart confirmation |

### Error Handling

- Unknown commands → "Unknown command" message
- Missing files → Descriptive error
- Subprocess failures → Stderr captured and displayed
- All errors logged to console

### Common Patterns

```python
# Adding a new skill to ALL_SKILLS
ALL_SKILLS = [
    "prices", "research", "post-generator", "queue-manager",
    "style-learner", "camsnap", "mcporter", "songsee",
    "adaptive-routing", "claude-proxy", "x-algorithm-optimizer",
    "new-skill"  # <-- Add here
]

# Extending voice commands
if "статус" in cmd and ("систем" in cmd or "состояние" in cmd):
    print(manager.cmd_system_status())
```
