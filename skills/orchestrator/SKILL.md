---
name: adaptive-routing
description: Intent-based skill router for claude-proxy bot. Routes messages to appropriate skills using keyword patterns and confidence scoring.
homepage: https://github.com
metadata: {"clawdbot":{"emoji":"🛣️","requires":{"python":[]},"install":[]}}
---

# adaptive-routing

## Overview

Intent-based skill router for claude-proxy bot. Analyzes incoming messages and routes them to the appropriate skill based on keyword patterns, context, and confidence scoring.

**Key Capabilities:**
- Pattern-based intent detection with regex
- Confidence scoring (0.0 - 1.0)
- Automatic parameter extraction for target skills
- Fallback routing when confidence is low
- Built-in cron job scheduling
- Support for 12+ skills including new ones (twitter-api, crypto-trading, ct-intelligence)

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                  Adaptive Routing Workflow                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Message Received                                         │
│     - Raw text from Gateway/user                             │
│     - Optional context (history, user prefs)                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Pattern Matching                                         │
│     - Match against 12 skill patterns                        │
│     - Score each match (0.3 per pattern hit)                 │
│     - Normalize to 0-1 range                                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Confidence Scoring                                       │
│     - Best match: highest score                              │
│     - Fallback: second-best if >0.1 confidence               │
│     - Default: claude-proxy if <0.1 confidence               │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Parameter Extraction                                     │
│     - Extract skill-specific parameters                      │
│     - Tokens, queries, topics, actions                       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Skill Execution                                          │
│     - Load and execute target skill                          │
│     - Handle errors with fallback                            │
└─────────────────────────────────────────────────────────────┘
```

## Skill Patterns

| Skill | Trigger Keywords | Examples |
|-------|-----------------|----------|
| prices | price, курс, $TOKEN, btc, eth, market | "What's the price of $BTC?" |
| research | research, news, what is, explain | "Research defi trends" |
| post-generator | post, tweet, write, generate | "Write a thread about AI" |
| style-learner | style, tone, voice, learn | "Match my writing style" |
| camsnap | camera, photo, capture | "Take a photo" |
| songsee | song, music, shazam | "What song is this?" |
| mcporter | mcp, server, tool | "Connect to MCP server" |
| queue-manager | queue, task, schedule | "Check pending tasks" |
| twitter-api | twitter, tweet, follow | "Post a tweet" |
| crypto-trading | crypto, whale, arbitrage | "Track whale activity" |
| ct-intelligence | competitor, trend, viral | "Analyze competitor" |
| adaptive-routing | route, tier, fast/standard/deep | "Use fast tier" |

## Confidence Thresholds

- `>= 0.7` — High confidence → Execute immediately
- `0.3 - 0.7` — Medium confidence → Execute with fallback ready
- `< 0.3` — Low confidence → Route to claude-proxy (general chat)

## Installation

```bash
# Skill is already in skills directory
cd ~/clawd/skills/orchestrator

# Test routing
python3 scripts/main.py --test-route "What's the price of $BTC?"

# List available jobs
python3 scripts/main.py --list-jobs

# Generate crontab
python3 scripts/main.py --generate-cron
```

## Usage

### CLI Commands

```bash
# Test routing for a message
python3 scripts/main.py --test-route "сколько стоит $STRK?"
python3 scripts/main.py --test-route "research defi news"

# Process a message (routes + executes)
python3 scripts/main.py --message "post a tweet about starknet"

# Run specific cron job
python3 scripts/main.py --job price-check
python3 scripts/main.py --job auto-post

# Generate crontab for all jobs
python3 scripts/main.py --generate-cron

# List all cron jobs
python3 scripts/main.py --list-jobs
```

### Python API

```python
from scripts.main import AdaptiveRouter, SkillExecutor, SkillType

# Simple routing
router = AdaptiveRouter()
result = router.route("What's the price of $BTC?")

print(f"Skill: {result.skill.value}")
print(f"Confidence: {result.confidence}")
print(f"Params: {result.params}")

# Full execution
executor = SkillExecutor()
result = executor.execute("Research defi trends")

print(f"Status: {result['status']}")
print(f"Output: {result['output']}")
```

### Integration with Gateway

```python
from scripts.main import AdaptiveRouter

def process_message(message: str, context: dict = None) -> dict:
    router = AdaptiveRouter()
    route = router.route(message, context)
    
    if route.confidence >= 0.7:
        # High confidence - execute skill
        return execute_skill(route.skill, route.params)
    elif route.confidence >= 0.3:
        # Medium confidence - execute with confirmation
        return {
            "action": "confirm",
            "skill": route.skill.value,
            "confidence": route.confidence,
            "params": route.params
        }
    else:
        # Low confidence - general chat
        return send_to_claude_proxy(message, context)
```

## Cron Jobs

The orchestrator manages scheduled tasks:

| Job | Schedule | Skill | Description |
|-----|----------|-------|-------------|
| price-check | `*/15 * * * *` | prices | Check prices every 15 min |
| research-digest | `0 8,20 * * *` | research | Morning/evening digest |
| style-update | `0 3 * * 0` | style-learner | Weekly model retrain |
| queue-cleanup | `0 */6 * * *` | queue-manager | Clean stale items |
| auto-post | `0 9,13,18,22 * * *` | post-generator | 4x daily posts |
| crypto-watch | `*/30 * * * *` | crypto-trading | Whale monitoring |
| trend-scan | `0 */4 * * *` | ct-intelligence | Trend scanning |

### Installing Cron Jobs

```bash
# Generate and install crontab
crontab <(python3 scripts/main.py --generate-cron)

# Or manually add to crontab
# 0 9,13,18,22 * * * cd /home/wner/clawd && python skills/orchestrator/scripts/main.py --job auto-post
```

## Parameter Extraction

The router extracts skill-specific parameters:

### Prices Skill
```python
message: "What's the price of $BTC and $ETH?"
params = {
    "raw_message": message,
    "tokens": ["BTC", "ETH"]
}
```

### Research Skill
```python
message: "Research latest defi news"
params = {
    "raw_message": message,
    "query": "Research latest defi news"
}
```

### Post Generator
```python
message: "Write a tweet about AI"
params = {
    "raw_message": message,
    "topic": "Write a tweet about AI",
    "format": "tweet"
}
```

### Crypto Trading
```python
message: "Track whale activity for $SOL"
params = {
    "raw_message": message,
    "tokens": ["SOL"],
    "action": "whale"
}
```

### CT Intelligence
```python
message: "Analyze competitor trends"
params = {
    "raw_message": message,
    "query": "Analyze competitor trends",
    "mode": "competitor"
}
```

## Examples

### Price Query Routing
```
Input:  "сколько стоит $STRK?"
Output: skill=prices, confidence=0.9, params={tokens: ["STRK"]}

Input:  "btc price now"
Output: skill=prices, confidence=0.7, params={tokens: ["btc"]}
```

### Research Query Routing
```
Input:  "что нового в defi?"
Output: skill=research, confidence=0.6, params={query: "что нового в defi?"}

Input:  "Research Ethereum governance"
Output: skill=research, confidence=0.8, params={query: "Research Ethereum governance"}
```

### Content Generation
```
Input:  "write a thread about starknet"
Output: skill=post-generator, confidence=0.9, params={topic: "...", format: "thread"}

Input:  "generate a tweet"
Output: skill=post-generator, confidence=0.8, params={topic: "...", format: "tweet"}
```

### Ambiguous Query
```
Input:  "привет"
Output: skill=claude-proxy, confidence=0.5, params={message: "привет"}

Input:  "help me"
Output: skill=claude-proxy, confidence=0.3, params={message: "help me"}
```

## File Structure

```
orchestrator/
├── __init__.py
├── scripts/
│   ├── main.py           # CLI entry point & core logic
│   ├── router.py         # AdaptiveRouter class
│   └── executor.py       # SkillExecutor class (optional)
├── references/
│   └── skill_patterns.json  # Pattern definitions
└── SKILL.md
```

## Adding New Skills

### 1. Add to SkillType Enum

```python
class SkillType(Enum):
    # ... existing skills ...
    NEW_SKILL = "new-skill"
```

### 2. Add Patterns

```python
AdaptiveRouter.PATTERNS[SkillType.NEW_SKILL] = [
    r'\b(new|skill|feature)\b',
    r'\b(trigger|activate)\b',
]
```

### 3. Add to CRON_JOBS (optional)

```python
CRON_JOBS["new-skill-task"] = {
    "schedule": "0 * * * *",
    "skill": SkillType.NEW_SKILL,
    "params": {"mode": "default"},
    "description": "Run new skill hourly"
}
```

### 4. Update Parameter Extraction

```python
def _extract_params(self, skill: SkillType, message: str):
    # ... existing code ...
    elif skill == SkillType.NEW_SKILL:
        params["action"] = "default"
        # Extract your parameters here
```

## Troubleshooting

### Low Confidence Routing

```bash
# Test message routing
python3 scripts/main.py --test-route "your message here"

# Check pattern coverage
# Patterns may need tuning for your use case
```

### Skill Not Found

```bash
# Verify skill exists
ls ~/clawd/skills/

# Check skill has scripts/main.py
ls ~/clawd/skills/skill-name/scripts/
```

### Cron Jobs Not Running

```bash
# Check crontab is installed
crontab -l

# Test job manually
python3 scripts/main.py --job price-check

# Check logs
tail -f /var/log/cron.log
```

### Pattern Matching Issues

```python
# Test pattern matching directly
router = AdaptiveRouter()
result = router.route("your message")

# Add debug output
print(f"All scores: {router._get_all_scores('your message')}")
```

## Integration Points

### Gateway Integration

```python
from scripts.main import AdaptiveRouter

def gateway_handler(message, context=None):
    router = AdaptiveRouter()
    result = router.route(message, context)
    
    if result.confidence >= 0.7:
        return execute_skill(result.skill, result.params)
    else:
        return escalate_to_human(message)
```

### Queue Integration

```python
from scripts.main import SkillExecutor, CRON_JOBS

def process_queued_task(job_name, params):
    if job_name not in CRON_JOBS:
        return {"error": f"Unknown job: {job_name}"}
    
    executor = SkillExecutor()
    return executor.execute(
        f"Execute {job_name}",
        context=CRON_JOBS[job_name]["params"]
    )
```

## Version

- v1.0.0 (2025-01-17): Initial release with 8 skills
- v1.1.0 (2025-01-17): Added twitter-api, crypto-trading, ct-intelligence
- v1.2.0 (2025-01-17): Converted to proper skill package format
