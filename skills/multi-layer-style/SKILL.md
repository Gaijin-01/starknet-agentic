# multi-layer-style

Multi-layered style processor for generating content in Sefirot's authentic voice.

## Overview

This skill implements a 5-layer architecture where "schizo" is a processing filter, not a fixed personality. It generates content based on:
- Topic classification
- Intent detection
- Schizo parameters (adjustable)
- Safety anchors
- Platform formatting

## Architecture

```
input_text
    ↓
topic_tags[]     ← LEVEL 1: Domain classifier
    ↓
intent           ← LEVEL 2: Intent detector
    ↓
schizo_params    ← LEVEL 3: Filter (adjustable!)
    ↓
safety_pass      ← LEVEL 4: Anti-cringe
    ↓
platform_format  ← LEVEL 5: Output formatter
    ↓
output
```

## Levels

### Level 0: Raw Input
Accept raw text as-is. No analysis.

### Level 1: Topic Classifier
Domains:
1. Crypto / Starknet / ZK
2. Geopolitics / war / states
3. Religion / history / identity
4. CT-drama / Twitter beef
5. Philosophy / meta / systems
6. Personal / fatigue / emotions
7. Meme / shitpost

### Level 2: Intent Detector
5 base intents:
1. **ENGAGE** — hook, viral
2. **ATTACK** — mock, put down
3. **SIGNAL** — show knowledge
4. **MYTH-BUILDING** — create narrative
5. **PROCESS** — think out loud

### Level 3: Schizo Filter
Parameters (0-100):
- Fragmentation: Breaks in text flow
- Irony: Meta-level awareness
- Aggression: Attack intensity
- Myth-layer: Narrative density
- Meme-density: Meme references

### Level 4: Safety Anchors
Anti-cringe module:
- Hyperbole markers
- Irony in aggressive takes
- No "I know truth" claims
- "Too much to be literal" signals

### Level 5: Output Formatter
Platform-specific:
- Twitter: Short, rhythmic, line breaks
- Thread: Escalation curve
- Longpost: Hook first, meaning second
- Reply: Dominance or cold shutdown

## Usage

```bash
# Generate with default schizo (50%)
python3 scripts/main.py --topic crypto --intent engage --text "starknet is growing"

# Generate with "в мясо" level (90%)
python3 scripts/main.py --topic crypto --intent engage --text "starknet is growing" --schizo 90

# Generate with specific parameters
python3 scripts/main.py --topic crypto --intent attack --text "solana sucks" --fragmentation 70 --irony 80 --aggression 90

# Check anti-cringe safety
python3 scripts/main.py --safety-check "we will conquer all chains"
```

## Quick Reference

| Command | Description |
|---------|-------------|
| `--topic` | Domain (crypto, geopolitics, religion, ct-drama, philosophy, personal, meme) |
| `--intent` | Intent (engage, attack, signal, myth-building, process) |
| `--schizo` | Schizo level 0-100 (default: 50) |
| `--fragmentation` | 0-100 |
| `--irony` | 0-100 |
| `--aggression` | 0-100 |
| `--myth` | 0-100 |
| `--meme` | 0-100 |
| `--platform` | twitter, thread, longpost, reply |
| `--safety-check` | Verify text passes anti-cringe |

## Presets

| Preset | Schizo | Fragmentation | Irony | Aggression | Myth | Meme |
|--------|--------|---------------|-------|------------|------|------|
| normal | 30% | 20% | 70% | 20% | 30% | 30% |
| ct | 50% | 40% | 50% | 30% | 40% | 50% |
| shizo | 70% | 70% | 60% | 50% | 60% | 60% |
| v-myaso | 90% | 90% | 30% | 80% | 80% | 40% |
| attack | 50% | 50% | 70% | 90% | 20% | 70% |
| meme | 50% | 60% | 40% | 40% | 30% | 90% |

## Formula

```
STYLE = FUNCTION(topic, intent) × schizo_filter
```

Schizo = multiplier, not foundation.

## Files
- `scripts/main.py` - Core processor
- `scripts/schizo_engine.py` - Schizo filter implementation
- `references/config.json` - Presets and parameters
