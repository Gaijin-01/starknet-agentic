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

## Moltbot Configuration

### Sub-Agent Allowlist (CRITICAL)

**Correct Structure:**
```json
{
  "agents": {
    "defaults": {
      "model": { "primary": "minimax/MiniMax-M2.1" },
      "maxConcurrent": 4,
      "subagents": { "maxConcurrent": 8 }
    },
    "list": [
      {
        "id": "main",
        "subagents": {
          "allowAgents": ["*"]  // ✅ CORRECT: list[].subagents.allowAgents
        }
      }
    ]
  }
}
```

**Common Mistakes:**
- ❌ `agents.defaults.subagents.allowlist` — WRONG path
- ❌ `agents.list[].subagents.allowAgents` with wrong key name
- Missing `agents.list` array entirely

**To allow specific agents only:**
```json
"allowAgents": ["evolver", "researcher", "poster"]
```

### ⚠️ Doctor --fix Warning

Running `moltbot doctor --fix` can **reset custom configs** to defaults.

**Before running `--fix`:**
1. Backup config: `cp ~/.moltbot/moltbot.json ~/.moltbot/moltbot.json.backup`
2. Review changes diff before applying

**Recovery if config is reset:**
```bash
# Restore from backup
cp ~/.moltbot/moltbot.json.backup ~/.moltbot/moltbot.json

# Or use the backup script (see below)
./scripts/backup_moltbot_config.sh
```

## Skill Configuration

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

## Troubleshooting

### Claude Proxy Issues

**Task execution fails**
```bash
# Check logs
python3 main.py health --verbose

# Restart proxy
python3 main.py proxy --task "status check"
```

**Autonomous mode doesn't start**
- Verify LLM configuration: `python3 main.py config get claude_proxy.llm.primary`
- Check model availability: `python3 main.py status`
- Review reasoning logs in `memory/`

**Model returns empty responses**
- Increase confidence threshold: `python3 main.py config add orchestrator.confidence_threshold 0.7`
- Check fallback models configured

### Orchestrator Issues

**Messages routed to wrong skill**
- Update skill keywords: `python3 main.py route --skills`
- Check confidence score: Increase threshold
- Review routing logs in `memory/`

**Skills not found**
- Verify skills path: `python3 main.py config get orchestrator.skills_path`
- Run analysis: `python3 main.py proxy --analyze-all`
- Check skill directories exist at configured path

### MCP Server Issues

**Server not responding**
```bash
# Check status
python3 main.py mcp daemon status

# Restart
python3 main.py mcp daemon stop
python3 main.py mcp daemon start

# Check logs
cat ~/.config/clawdbot/mcporter.log
```

**Tool call fails**
- Verify server is running: `python3 main.py mcp list`
- Check tool name format: `server.tool_name`
- Verify JSON args format

### Configuration Issues

**Config not loading**
```bash
# Debug config loading
python3 main.py config list

# Check config directory exists
ls ~/.config/clawdbot/

# Verify file permissions
chmod 600 ~/.config/clawdbot/*.yaml
```

**Doctor --fix reset config**
- Restore from backup: `cp ~/.moltbot/moltbot.json.backup ~/.moltbot/moltbot.json`
- Manual recovery from memory/evolution.md logs

### Common Error Messages

| Error | Solution |
|-------|----------|
| `Model not found` | Check LLM config, verify API keys |
| `Skill not loaded` | Run `python3 main.py proxy --analyze-all` |
| `MCP server timeout` | Increase timeout in config, restart daemon |
| `Confidence too low` | Lower threshold or improve query |
| `Permission denied` | Check file/directory permissions |

### Debug Commands

```bash
# Full health check
python3 main.py check

# Verbose status
python3 main.py health --verbose

# Route test
python3 main.py route --test "your query"

# Config debug
python3 main.py config list

# MCP diagnostics
python3 main.py mcp list
python3 main.py mcp daemon status

# Log analysis
tail -f ~/.config/clawdbot/mcporter.log
cat memory/*.log | grep ERROR
```

### Getting Help

1. Check logs: `python3 main.py health --verbose`
2. Run diagnostics: `python3 main.py check`
3. Review skill-evolver: `cat memory/evolution.md`
4. Check Moltbot docs: `/home/wner/moltbot/docs/`
