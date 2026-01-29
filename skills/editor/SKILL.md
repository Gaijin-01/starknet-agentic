# editor

Meta-controller for autonomous text processing. Combines topic classification, intent recognition, contextual memory, style parameter adaptation, safety anchoring, and output formatting.

## Overview

EDITOR is not a fixed rewrite engine. It dynamically selects operations based on:
- Domain signals
- User intent
- Context history
- Platform constraints

Inspired by xai-org/x-algorithm architecture.

## Components

### Pipeline Stages

| Stage | Function | Output |
|-------|----------|--------|
| 1. Input Intake | Accept raw text + metadata, normalize formatting | Clean input |
| 2. Topic + Intent Classifier | Multi-label topic detection, intent hierarchy | tags, intent |
| 3. MetaController | Maps topic+intent → style parameters | (fragmentation, irony, aggression, meme_density, myth_layer) |
| 4. Styler Engine | Applies transformations with selected params | Styled text |
| 5. Safety & Anchors | Hyperbole markers, no absolute truth claims | Safe text |
| 6. Output Formatter | Platform-adaptive (short, thread, markdown, code) | Platform-ready |

## Style Parameters

| Parameter | Range | Description |
|-----------|-------|-------------|
| fragmentation | 0-100 | Breaks in text flow |
| irony | 0-100 | Meta-awareness level |
| aggression | 0-100 | Attack intensity |
| meme_density | 0-100 | Meme references |
| myth_layer | 0-100 | Narrative/drama density |

## Presets

| Preset | (frag, iron, agg, meme, myth) | Use Case |
|--------|------------------------------|----------|
| normal | (30, 30, 20, 10, 5) | Standard conversation |
| ct | (55, 40, 45, 30, 25) | Crypto Twitter |
| shizo | (70, 60, 50, 45, 40) | Full schizo mode |
| v-myaso | (85, 70, 70, 70, 60) | Faces melted |
| sefirot | (45, 50, 15, 25, 40) | Minimal, cryptic, confident, supportive. Strategic emoji. Bimodal length. Starknet/L2 ecosystem, philosophy. Low aggression for engagement. |

**User overrides always take precedence.**

## Usage

```bash
# Process with default preset
python3 scripts/main.py --text "gm 🐺 starknet winning today"

# Process with specific preset
python3 scripts/main.py --text "gm 🐺 starknet winning today" --preset ct

# Process with custom parameters
python3 scripts/main.py --text "gm 🐺 starknet winning today" --fragmentation 60 --irony 50 --aggression 30

# Explain parameter selection
python3 scripts/main.py --text "gm 🐺 starknet winning today" --explain

# Thread output
python3 scripts/main.py --text "deep analysis here" --platform thread

# Safety check only
python3 scripts/main.py --safety-check "we will conquer all chains"
```

## Configuration

Parameters defined in `references/config.json`:
- Topic classifiers
- Intent patterns
- Presets
- Safety rules

## Memory Integration

- Session context preserved
- Long-term user preferences loaded from MEMORY.md
- Semantic topic signatures maintained

## Extensions

- **Domain specificity modules**: crypto, geopolitics, religion
- **Explainability tokens**: Why certain params were chosen
- **Feedback loop**: Self-improving parameter tuning

## Dependencies

- skills/multi-layer-style (style parameters)
- skills/style-learner (user profile)
- skills/safety-anchors (constraints)

## Files

- `scripts/main.py` - Main entry point
- `scripts/meta_controller.py` - Topic → params mapping
- `scripts/styler.py` - Transformation engine
- `scripts/safety.py` - Safety anchoring
- `scripts/formatter.py` - Platform adaptation
- `references/config.json` - Configuration
- `assets/` - Training data, patterns
