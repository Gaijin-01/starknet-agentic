# Config Skill

Centralized configuration management for Clawdbot.

## Overview

Loads and provides access to config.yaml and config.json with environment override support.

## Usage

```python
from config_loader import Config

cfg = Config()
value = cfg.get('section.key', 'default')
```

## Config Sources

1. `config.yaml` - Main config
2. `config.json` - JSON overrides
3. Environment variables override file values

## Commands

```bash
# Validate config
python config_loader.py --validate

# Show all config
python config_loader.py --show
```

## Structure

```
config/
├── config.yaml        # Main config
├── config.json        # JSON overrides  
├── config_loader.py   # Loader module
└── loaders/           # Format-specific loaders
```
