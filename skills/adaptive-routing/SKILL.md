# adaptive-routing

## Overview

Intent-based skill router for claude-proxy bot. Analyzes incoming messages and routes them to the appropriate skill based on keyword patterns, context, and confidence scoring.

## Workflow

```
1. Message received from Gateway
2. AdaptiveRouter.route(message, context)
3. Pattern matching against all skill keywords
4. Score calculation (0.0 - 1.0 confidence)
5. Parameter extraction for target skill
6. Return RoutingResult with skill, confidence, params, fallback
```

## Configuration

### Skill Patterns

Each skill has associated regex patterns:

| Skill | Trigger Keywords |
|-------|-----------------|
| prices | price, курс, btc, eth, $TOKEN, market |
| research | research, search, news, what is |
| post-generator | post, tweet, write, generate |
| style-learner | style, tone, persona, mimic |
| camsnap | camera, photo, capture, screenshot |
| songsee | song, music, shazam, lyrics |
| mcporter | mcp, server, connect, tool |
| queue-manager | queue, task, schedule, pending |

### Confidence Thresholds

- `>= 0.7` — High confidence, execute immediately
- `0.3 - 0.7` — Medium confidence, execute with fallback ready
- `< 0.3` — Low confidence, route to claude-proxy (general chat)

## Usage

### CLI

```bash
# Test routing
python orchestrator.py --test-route "what's the price of $BTC"

# Process message
python orchestrator.py --message "write a tweet about starknet"

# Generate crontab
python orchestrator.py --generate-cron
```

### Python API

```python
from orchestrator import AdaptiveRouter, SkillExecutor

router = AdaptiveRouter()
result = router.route("check ETH price")

print(result.skill)       # SkillType.PRICES
print(result.confidence)  # 0.6
print(result.params)      # {"tokens": ["eth"], "raw_message": "..."}
```

## Examples

### Price Query
```
Input:  "сколько стоит $STRK?"
Output: skill=prices, confidence=0.9, params={tokens: ["STRK"]}
```

### Research Query
```
Input:  "что нового в defi?"
Output: skill=research, confidence=0.6, params={query: "что нового в defi?"}
```

### Ambiguous Query
```
Input:  "привет"
Output: skill=claude-proxy, confidence=0.5, params={message: "привет"}
```

## Integration Points

- **Gateway**: Receives routed messages, returns responses
- **Queue Manager**: Async task execution
- **Memory**: Context for better routing decisions
- **All Skills**: Target execution modules

## Error Handling

1. Skill not found → Log error, try fallback
2. Low confidence → Route to claude-proxy
3. Execution failure → Queue for retry, notify admin
