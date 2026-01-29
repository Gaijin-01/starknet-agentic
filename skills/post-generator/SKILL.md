# Post Generator Skill

## Overview
Universal post generation using config-based templates and persona.

## How It Works
1. Reads persona from `config.yaml`
2. Uses templates for content type (gm, price, news, insight)
3. Formats post within character limit
4. Saves to queue directory

## Config
```yaml
persona:
  name: "SCHIZODIO"
  voice: "degen"
  
templates:
  gm:
    - "gm {emoji} zk summer loading..."
  news:
    - "{headline}. bullish if true. 🔥"
```

## Usage
```bash
# Generate GM post
python scripts/post_generator.py --type gm

# Generate from news headline
python scripts/post_generator.py --type news --headline "Starknet TVL hits $1B"

# Generate price post
python scripts/post_generator.py --type price --asset STRK

# Custom content
python scripts/post_generator.py --custom "your text here"

# Save to queue
python scripts/post_generator.py --type gm --save
```

## Personas
- **degen**: crypto slang, minimal, edgy
- **professional**: formal, structured, no slang
- **casual**: friendly, conversational
- **sarcastic**: ironic, witty
- **formal**: corporate, polished

## Troubleshooting

```bash
# Check config
python scripts/post_generator.py --validate

# Debug mode
python scripts/post_generator.py --type gm --debug

# Check queue directory
ls -la ~/clawd/post_queue/
```

## Version

- v1.0.0 (2026-01-17): Initial release


