# Adaptive Routing for Clawdbot

Automatic query classifier that scores user queries based on complexity (1-100) and routes them to appropriate model tiers.

## Overview

This skill enables intelligent routing of user queries to the most appropriate model based on query complexity:

| Score Range | Tier | Model | Use Case |
|-------------|------|-------|----------|
| 1-29 | Fast | MiniMax-M2.1-Fast | Simple questions, greetings, short queries |
| 30-70 | Standard | MiniMax-M2.1 | Standard tasks, coding, analysis, summaries |
| 71-100 | Deep | MiniMax-M2.1-Deep | Complex reasoning, multi-step research, architectural decisions |

## Files

- `classifier.py` - Main classifier module
- `README.md` - This documentation

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

## API

### `classify(query: str) -> ClassificationResult`

Classifies a query and returns:
- `score` (int): Complexity score 1-100
- `tier` (str): "fast", "standard", or "deep"
- `reasoning` (str): Explanation of the score
- `suggested_model` (str): Model to use
- `system_prompt` (str): System prompt for the tier

### `route_query(query: str) -> dict`

Returns a dictionary with complete routing information for the query.

## Scoring Criteria

### High Score Indicators (Complex)
- Architectural/design discussions (+25)
- Multi-step requests (+15)
- Research/investigation requests (+15)
- Performance optimization (+25)
- System design (+25)
- Code analysis and review (+12)

### Medium Score Indicators (Standard)
- Code generation requests (+10)
- Debug/fix requests (+8)
- Analysis requests (+12)
- API/database work (+10-12)
- Documentation (+10)

### Low Score Indicators (Simple)
- Greetings (-5)
- Simple questions (-3)
- Gratitude (-5)
- Short queries (<5 words, -5)

## System Prompts

| Tier | Prompt |
|------|--------|
| Fast | "Be concise. Answer in 1-2 sentences." |
| Standard | "Be thorough but efficient. Provide complete answers." |
| Deep | "Think step by step. Provide detailed analysis with reasoning." |

## Configuration

The routing configuration is stored in `~/.clawdbot/clawdbot.json` under `models.providers.minimax.adaptiveRouting`.

### Model Configurations

**MiniMax-M2.1-Fast** (scores <30)
- Context: 50k tokens
- Max output: 2k tokens
- Cost: input 10, output 40
- Compaction: aggressive

**MiniMax-M2.1** (scores 30-70)
- Context: 200k tokens
- Max output: 8k tokens
- Cost: input 15, output 60

**MiniMax-M2.1-Deep** (scores >70)
- Context: 200k tokens
- Max output: 16k tokens
- Reasoning: enabled
- Cost: input 25, output 100

## Testing

Run the classifier tests:

```bash
cd /home/wner/clawd/skills/adaptive-routing
python classifier.py
```

Sample test results:
- "Hi, how are you?" → Score: 5 (Fast)
- "Write a Python function to calculate factorial" → Score: 42 (Standard)
- "Design a scalable microservices architecture..." → Score: 85 (Deep)
