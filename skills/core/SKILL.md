# core

Unified core management skill. Merges claude-proxy, orchestrator, config, and mcporter.

## Overview

**Merged Skills:**
- `claude-proxy` → Claude Code integration, autonomous AI
- `orchestrator` → Message routing and skill execution
- `config` → Configuration loading and management
- `mcporter` → MCP server management

## Architecture

```
core/
├── SKILL.md           # Documentation
├── config.yaml        # Configuration
└── main.py            # Unified entry point (proxy, route, config, mcp)
```

## Usage

### Claude Proxy (Autonomous AI)

```bash
# Execute a task
python3 main.py proxy --task "Analyze and fix errors in prices skill"

# Interactive mode
python3 main.py proxy --interactive

# Improve a skill
python3 main.py proxy --improve-skill research --apply

# Analyze all skills
python3 main.py proxy --analyze-all

# Autonomous mode
python3 main.py proxy --autonomous --hours 8 --focus error-fixing
```

### Orchestrator (Routing)

```bash
# Route a message
python3 main.py route "price of bitcoin"

# Test routing
python3 main.py route --test "research ethereum"

# List skills
python3 main.py route --skills

# Generate crontab
python3 main.py route --cron

# Run cron job
python3 main.py route --job price-check
```

### MCP Server Management

```bash
# List servers
python3 main.py mcp list

# Call a tool
python3 main.py mcp call server.tool --args '{"param": "value"}'

# Daemon control
python3 main.py mcp daemon start
python3 main.py mcp daemon status
python3 main.py mcp daemon stop

# Generate CLI
python3 main.py mcp generate-cli --server my-server
```

### Configuration

```bash
# List config
python3 main.py config list

# Get value
python3 main.py config get llm.primary

# Add/update
python3 main.py config add llm.fallback openai
```

### All-in-One

```bash
# Full system check
python3 main.py check

# Health report
python3 main.py health --verbose

# Status
python3 main.py status
```

## API

```python
from core import ClaudeProxy, Orchestrator, MCPManager, ConfigLoader

# Claude Proxy
proxy = ClaudeProxy()
result = proxy.execute_task("Analyze skill prices")

# Orchestrator
orchestrator = Orchestrator()
result = orchestrator.route("price of bitcoin")
result = orchestrator.execute("research ethereum")

# MCP Manager
mcp = MCPManager()
servers = mcp.list_servers()
output = mcp.call_tool("server.tool", {"param": "value"})

# Config
config = ConfigLoader()
value = config.get("llm.primary")
```

## Configuration

`config.yaml`:
```yaml
claude_proxy:
  llm:
    primary: "minimax"
    fallback: ["openai", "ollama"]
  autonomous:
    max_tasks_per_hour: 20
    focus_areas:
      - error-fixing
      - skill-improvement
  reasoning:
    self_reflect: true
    verbose: true

orchestrator:
  confidence_threshold: 0.6
  fallback_skill: default
  skills_path: /home/wner/clawd/skills

mcp:
  config_path: ~/.config/clawdbot/mcporter.yaml
  daemon:
    auto_start: false
    timeout: 30

config:
  config_dir: ~/.config/clawdbot
  loaders:
    - json
    - yaml
    - env
```

## Migration

This skill was consolidated from:
- skills/claude-proxy (v1.0.0)
- skills/orchestrator (v1.0.0)
- skills/config (v1.0.0)
- skills/mcporter (v1.0.0)

Old skills kept as aliases for backward compatibility.

## Skill Types (for routing)

| Skill | Keywords |
|-------|----------|
| prices | price, курс, btc, eth, token, market |
| research | research, найди, search, информация |
| post-generator | post, tweet, написать, gm |
| style-learner | style, стилю, learn, persona |
| camsnap | camera, камера, snap, screenshot |
| songsee | song, музыка, shazam, lyrics |
| mcporter | mcp, server, tool, integration |
| queue-manager | queue, очередь, schedule, job |
| twitter-api | twitter, tweet, retweet, follow |
| crypto-trading | whale, arbitrage, on-chain, tvl |
| ct-intelligence | competitor, trend, viral, monitor |
| claude-proxy | default routing for general queries |
