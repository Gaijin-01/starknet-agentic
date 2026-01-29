# Adaptive Routing

Automatic query classifier that scores user queries based on complexity (1-100) and routes them to appropriate model tiers for optimal performance and cost efficiency.

## Overview

This skill enables intelligent routing of user queries to the most appropriate AI model based on query complexity. It analyzes each incoming message and assigns a complexity score, then routes to MiniMax-M2.1-Fast, MiniMax-M2.1, or MiniMax-M2.1-Deep accordingly.

## Workflow

```
Message: "Design a scalable microservices architecture"
         │
         ▼
    Pattern Matching
         │
    ▼
    Complexity Scoring (1-100)
         │
    ┌────┴────┐
    │         │
    ▼         ▼
  Score    Score
   1-29    30-70
    │         │
    ▼         ▼
 MiniMax   MiniMax
 Fast     M2.1
          │
          ▼
       Score
       71-100
          │
          ▼
       MiniMax
       M2.1-Deep
```

## Scoring Criteria

### High Score Indicators (+15-25)
- Architectural/design discussions
- Multi-step requests
- Research/investigation requests
- Performance optimization
- System design
- Code analysis and review

### Medium Score Indicators (+8-12)
- Code generation requests
- Debug/fix requests
- Analysis requests
- API/database work
- Documentation

### Low Score Indicators (-3 to -5)
- Greetings
- Simple questions
- Gratitude
- Short queries (<5 words)

## Configuration

The routing configuration is stored in `~/.clawdbot/clawdbot.json` under `models.providers.minimax`.

```yaml
models:
  providers:
    minimax:
      adaptiveRouting:
        enabled: true
        tiers:
          fast:
            model: "minimax/MiniMax-M2.1-Fast"
            scoreMax: 29
            maxTokens: 2000
          standard:
            model: "minimax/MiniMax-M2.1"
            scoreMin: 30
            scoreMax: 70
            maxTokens: 8000
          deep:
            model: "minimax/MiniMax-M2.1-Deep"
            scoreMin: 71
            maxTokens: 16000
            reasoning: true
```

## Usage

```python
from classifier import classify, route_query

# Simple classification
result = classify("What is Python?")
print(f"Score: {result.score}, Tier: {result.tier}")

# Get full routing info
routing = route_query("Design a scalable microservices architecture")
print(routing)
```

### API

| Function | Description |
|----------|-------------|
| `classify(query: str)` | Returns ClassificationResult with score, tier, reasoning |
| `route_query(query: str)` | Returns dict with complete routing information |

## Examples

| Query | Score | Tier |
|-------|-------|------|
| "Hi, how are you?" | 5 | Fast |
| "Write a Python function to calculate factorial" | 42 | Standard |
| "Design a scalable microservices architecture" | 85 | Deep |

## Files

- `classifier.py` - Main classifier module
- `SKILL.md` - This documentation
