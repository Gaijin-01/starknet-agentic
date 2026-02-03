# system

Unified system management skill. Merges system-manager, skill-evolver, and adaptive-routing.

## Overview

**Merged Skills:**
- `system-manager` → skills, memory, services, system status
- `skill-evolver` → analyze and improve skills
- `adaptive-routing` → route messages to appropriate skills

## Architecture

```
system/
├── SKILL.md           # Documentation
├── config.yaml        # Configuration
└── main.py            # Unified entry point (system, evolve, route)
```

## Usage

### System Management

```bash
# Skills
python3 main.py system skills --list
python3 main.py system skills --enable research
python3 main.py system skills --disable prices

# Memory
python3 main.py system memory --backup
python3 main.py system memory --restore latest
python3 main.py system memory --clean 7

# Service
python3 main.py system service --status
python3 main.py system service --restart gateway

# System status
python3 main.py system status
python3 main.py system health
```

### Skill Evolution

```bash
# Analyze a skill
python3 main.py evolve --skill research --output json

# Analyze all skills
python3 main.py evolve --all

# Apply fixes
python3 main.py evolve --skill research --fix

# List skills
python3 main.py evolve --list
```

### Adaptive Routing

```bash
# Route a message
python3 main.py route "what's the price of bitcoin"

# Batch route
python3 main.py batch --file messages.txt

# Interactive mode
python3 main.py interactive

# List skills
python3 main.py skills
```

### All-in-One

```bash
# Full system check
python3 main.py check

# Health report
python3 main.py health --verbose
```

## API

```python
from system import SystemManager, SkillEvolver, AdaptiveRouter

# System management
system = SystemManager()
print(system.cmd_system_status())

# Skill evolution
evolver = SkillEvolver()
result = evolver.analyze_skill("research")

# Routing
router = AdaptiveRouter()
result = router.route("price of ethereum")
```

## Configuration

`config.yaml`:
```yaml
system:
  skills:
    default_enabled:
      - prices
      - research
      - post-generator
      - queue-manager
    optional:
      - camsnap
      - songsee
      - mcporter
  
  memory:
    backup_days: 7
    max_backup_size_mb: 100
  
  health:
    check_skills: true
    check_orchestrator: true
    check_cron: true

evolve:
  severity_threshold: low  # low, medium, high
  auto_apply: false
  report_path: /home/wner/clawd/memory/

routing:
  confidence_threshold: 0.6
  fallback_skill: default
  cache_ttl_seconds: 300
```

## Sub-modules

### system.py
System administration: skill enable/disable, memory backup/restore, service control, health checks.

### evolve.py
Skill analysis and improvement: code quality, docstrings, error handling, test coverage.

### router.py
Message routing: classify intent, select best skill, manage fallback routing.

## Migration

This skill was consolidated from:
- skills/system-manager (v1.0.0)
- skills/skill-evolver (v1.0.0)
- skills/adaptive-routing (v1.0.0)

Old skills kept as aliases for backward compatibility.

## Voice Commands (Russian)

```
включи скилл research
выключи скилл prices
статус системы
забэкапь память
очисти память
перезапусти гейтвей
здоровье системы
```
