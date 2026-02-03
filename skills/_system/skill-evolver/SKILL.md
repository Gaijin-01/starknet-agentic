# skill-evolver

A self-improving skill system that autonomously analyzes, monitors, and enhances Clawdbot's existing skills.

## Overview

skill-evolver operates as an autonomous improvement agent that:
- Scans and analyzes all skills in the ecosystem
- Identifies gaps, bugs, and optimization opportunities  
- Generates and applies improvements safely
- Tracks metrics and logs all modifications

## Quick Start

```bash
# Run full analysis
python scripts/analyze.py

# Generate improvements
python scripts/evolve.py --mode=suggest

# Apply improvements (with confirmation)
python scripts/evolve.py --mode=apply

# Full autonomous cycle
python scripts/evolve.py --mode=auto --dry-run
```

## Directory Structure

```
skill-evolver/
├── SKILL.md              # This file
├── scripts/
│   ├── analyze.py        # Core analysis engine
│   ├── evolve.py         # Improvement generator
│   └── utils.py          # Shared utilities
├── references/
│   └── config.json       # Configuration
└── assets/
    └── evolution.log     # Change history
```

## Workflow

1. **Analysis** → Scan skills, check completeness, collect metrics
2. **Generation** → Generate improvement patches
3. **Validation** → Backup and verify safety
4. **Application** → Apply changes with logging

## Configuration

Edit `references/config.json`:

```json
{
  "skills_path": "~/clawd/skills/",
  "memory_path": "~/clawd/memory/",
  "backup_path": "~/clawd/backups/",
  "auto_apply": false,
  "dry_run": true,
  "max_changes_per_run": 5,
  "require_confirmation": true,
  "excluded_skills": ["skill-evolver"],
  "metrics": {
    "track_tokens": true,
    "track_errors": true,
    "track_completion": true
  }
}
```

## Analysis Criteria

### Skill Completeness Score (0-100)

| Component | Weight | Criteria |
|-----------|--------|----------|
| SKILL.md exists | 20 | File present and non-empty |
| Documentation quality | 15 | Has overview, workflow, examples |
| Scripts present | 20 | Has executable scripts |
| Error handling | 15 | Try/catch, logging present |
| Dependencies declared | 10 | Requirements listed |
| Examples provided | 10 | Usage examples in docs |
| Version tracking | 10 | Version number present |

### Issue Severity Levels

- **CRITICAL**: Missing SKILL.md, broken scripts
- **HIGH**: No error handling, missing dependencies
- **MEDIUM**: Incomplete documentation, no examples
- **LOW**: Style inconsistencies, minor optimizations

## Safety Constraints

### Hard Rules (Never Violated)
1. **Backup First**: Always create backup before modification
2. **No Deletion**: Never delete skills, only modify
3. **Reversibility**: All changes must be reversible
4. **Logging**: Every change logged with timestamp
5. **Rate Limit**: Max 5 changes per run by default

### Confirmation Required For
- Modifying core workflow logic
- Changes affecting multiple skills
- Adding new dependencies
- Structural changes to SKILL.md

### Auto-Applied Without Confirmation
- Documentation formatting fixes
- Adding missing error handling boilerplate
- Updating version numbers
- Adding missing log statements

## Output Format

### Analysis Report
```markdown
# Skill Evolution Report — 2025-01-17

## Summary
- **Skills Analyzed**: 5
- **Total Score**: 78/100 avg
- **Issues Found**: 12
- **Critical**: 0 | High: 3 | Medium: 6 | Low: 3

## Skill Scores

| Skill | Score | Status |
|-------|-------|--------|
| x-persona-adapter | 92 | ✅ Healthy |
| starknet-research | 85 | ✅ Healthy |
| web-search | 71 | ⚠️ Needs Work |
| tweet-reader | 68 | ⚠️ Needs Work |
| crypto-news-thread | 74 | ⚠️ Needs Work |

## Issues Found

### HIGH Priority
1. **web-search**: Missing retry logic for API failures
2. **tweet-reader**: No rate limit handling
3. **crypto-news-thread**: Hardcoded API keys detected

### MEDIUM Priority
1. **web-search**: No usage examples in SKILL.md
2. **tweet-reader**: Missing error handling in parse_tweet()
...

## Recommendations
1. Add retry decorator to all API calls
2. Implement centralized rate limiting
3. Move credentials to config files
```

### Evolution Report
```markdown
# Evolution Applied — 2025-01-17

## Changes Made: 3

### 1. web-search
**File**: scripts/search.py
**Change**: Added retry decorator with exponential backoff
**Backup**: backups/web-search/search.py.20250117_143022

### 2. tweet-reader  
**File**: SKILL.md
**Change**: Added error handling section to documentation
**Backup**: backups/tweet-reader/SKILL.md.20250117_143025

### 3. crypto-news-thread
**File**: scripts/fetch_news.py
**Change**: Moved API key to environment variable
**Backup**: backups/crypto-news-thread/fetch_news.py.20250117_143028

## Next Actions
- [ ] Review and test web-search retry logic
- [ ] Add rate limiting to tweet-reader
- [ ] Update config documentation
```

## Usage Patterns

### Daily Maintenance
```bash
# Morning check
python scripts/analyze.py --output=report.md

# Review and apply safe changes
python scripts/evolve.py --mode=apply --severity=low
```

### Weekly Deep Analysis
```bash
# Full analysis with metrics
python scripts/analyze.py --include-metrics --include-transcripts

# Generate comprehensive improvements
python scripts/evolve.py --mode=suggest --all
```

### After Adding New Skill
```bash
# Validate new skill
python scripts/analyze.py --skill=new-skill-name

# Apply standard improvements
python scripts/evolve.py --skill=new-skill-name --mode=apply
```

## Integration with Clawdbot

### Cron Schedule
Add to clawdbot cron for automated maintenance:
```json
{
  "name": "skill-evolution-daily",
  "schedule": "0 3 * * *",
  "command": "python ~/clawd/skills/skill-evolver/scripts/evolve.py --mode=auto --dry-run --report"
}
```

### Memory Integration
Evolution logs are stored in `~/clawd/memory/skill-evolution/`:
- `analysis_history.json` - Historical analysis results
- `changes.log` - All applied modifications
- `metrics.json` - Tracked performance metrics

## Extending skill-evolver

### Adding New Analysis Rules
Edit `references/config.json` to add custom rules:
```json
{
  "custom_rules": [
    {
      "name": "check_api_timeout",
      "pattern": "requests\\.(get|post)\\(",
      "missing": "timeout=",
      "severity": "medium",
      "fix_template": "Add timeout parameter"
    }
  ]
}
```

### Adding New Improvement Templates
Create templates in `references/templates/`:
```python
# references/templates/retry_decorator.py
RETRY_TEMPLATE = '''
from functools import wraps
import time

def retry(max_attempts=3, delay=1, backoff=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts == max_attempts:
                        raise
                    time.sleep(delay * (backoff ** attempts))
            return wrapper
        return decorator
'''
```

## Troubleshooting

### Analysis Fails
```bash
# Check paths
python scripts/analyze.py --validate-config

# Run with debug
python scripts/analyze.py --debug
```

### Changes Not Applied
```bash
# Check backup space
df -h ~/clawd/backups/

# Verify permissions
ls -la ~/clawd/skills/

# Force apply (use with caution)
python scripts/evolve.py --mode=apply --force
```

### Rollback Changes
```bash
# List backups
ls -la ~/clawd/backups/[skill-name]/

# Restore specific backup
python scripts/evolve.py --rollback=backups/skill-name/file.py.20250117_143022
```

## Version History

- **v1.0.0** (2025-01-17): Initial release
  - Core analysis engine
  - Safe modification system
  - Backup and rollback support
  - Metric tracking foundation
