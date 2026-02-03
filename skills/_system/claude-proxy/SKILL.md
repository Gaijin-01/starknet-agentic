# claude-proxy (Ultra Skill)

## Overview

Автономный агент-заместитель, работающий когда Claude недоступен. Эмулирует стиль мышления, принятия решений и генерации кода Claude.

**Когда использовать:**
- Claude API недоступен (лимиты, даунтайм)
- Нужна 24/7 автономная работа
- Локальная обработка без внешних API
- Backup reasoning engine

## Capabilities

| Capability | Description |
|------------|-------------|
| **Reasoning** | Chain-of-thought, structured thinking |
| **Code Generation** | Python, Bash, configs, skills |
| **Self-Improvement** | Анализ и улучшение скилов |
| **Decision Making** | Multi-criteria analysis |
| **Error Recovery** | Автоматическое исправление |
| **Memory** | Persistent learning |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLAUDE-PROXY                              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Input     │→ │  Reasoning  │→ │   Output    │         │
│  │  Parser     │  │   Engine    │  │  Generator  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│         │                │                │                 │
│         ▼                ▼                ▼                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Context    │  │    LLM      │  │   Code      │         │
│  │  Manager    │  │   Client    │  │   Gen       │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│         │                │                │                 │
│         └────────────────┼────────────────┘                 │
│                          ▼                                  │
│                   ┌─────────────┐                           │
│                   │   Memory    │                           │
│                   │   Store     │                           │
│                   └─────────────┘                           │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Autonomous task execution
python scripts/main.py --task "Analyze and fix errors in whale-tracker skill"

# Interactive mode
python scripts/main.py --interactive

# Code generation
python scripts/main.py --generate-code "Create a Telegram alert function"

# Skill improvement
python scripts/main.py --improve-skill x-persona-adapter

# Full autonomous mode
python scripts/main.py --autonomous --hours 8
```

## Components

### 1. Reasoning Engine (`reasoning.py`)
- Structured thinking: Goal → Context → Plan → Execute → Validate
- Chain-of-thought prompting
- Multi-step problem decomposition
- Self-reflection and correction

### 2. LLM Client (`llm_client.py`)
- Multi-provider support: MiniMax, OpenAI, Ollama, Anthropic
- Automatic fallback chain
- Rate limiting and retry logic
- Token optimization

### 3. Code Generator (`code_gen.py`)
- Python, Bash, JSON generation
- Template-based generation
- Syntax validation
- Auto-testing

### 4. Self-Improver (`self_improve.py`)
- Skill analysis and scoring
- Automated fixes
- Documentation generation
- Test creation

## Configuration

`references/config.json`:
```json
{
  "llm": {
    "primary": "minimax",
    "fallback": ["openai", "ollama"],
    "model": "MiniMax-M2.1",
    "max_tokens": 4096,
    "temperature": 0.7
  },
  "reasoning": {
    "max_iterations": 5,
    "self_reflect": true,
    "verbose": true
  },
  "code_gen": {
    "validate_syntax": true,
    "auto_test": false,
    "style": "claude"
  },
  "memory": {
    "enabled": true,
    "max_entries": 1000
  }
}
```

## Prompts Structure

The skill uses carefully crafted prompts that emulate Claude's thinking style:

```
prompts/
├── system.md          # Core system prompt
├── reasoning.md       # Chain-of-thought template
├── code_gen.md        # Code generation style
├── analysis.md        # Skill analysis template
└── decision.md        # Decision making framework
```

## Usage Examples

### Task Execution
```bash
# Simple task
python scripts/main.py --task "Check browser status and restart if needed"

# Complex task with context
python scripts/main.py --task "Analyze last 24h errors and create fix plan" \
  --context-file ~/clawd/memory/agent_state.json
```

### Skill Evolution
```bash
# Analyze and improve specific skill
python scripts/main.py --improve-skill web-search --apply

# Analyze all skills
python scripts/main.py --analyze-all --report
```

### Code Generation
```bash
# Generate new skill
python scripts/main.py --generate-skill "twitter-analytics" \
  --description "Analyze Twitter engagement metrics"

# Generate function
python scripts/main.py --generate-code "async function to fetch crypto prices" \
  --output ~/clawdbot/skills/public/price-fetcher/scripts/fetch.py
```

### Autonomous Mode
```bash
# Run for 8 hours, checking tasks every 30 minutes
python scripts/main.py --autonomous --hours 8 --interval 30

# With specific focus
python scripts/main.py --autonomous --focus "error-fixing,skill-improvement"
```

## Integration with skill-evolver

claude-proxy extends skill-evolver with:
- LLM-powered analysis (not just regex patterns)
- Intelligent fix generation
- Natural language improvement suggestions
- Code refactoring capabilities

```bash
# Use claude-proxy as backend for skill-evolver
python ~/clawdbot/skills/public/skill-evolver/scripts/evolve.py \
  --backend claude-proxy \
  --mode apply
```

## Memory System

Stores learnings and patterns:

```json
{
  "successful_patterns": [
    {"task": "fix_error", "approach": "...", "success_rate": 0.95}
  ],
  "failed_approaches": [...],
  "code_templates": {...},
  "decision_history": [...]
}
```

## Safety

- **Backup before changes**: Always creates backups
- **Dry-run mode**: Preview changes without applying
- **Confirmation prompts**: For destructive operations
- **Rate limiting**: Prevents API abuse
- **Logging**: All actions logged

## Troubleshooting

```bash
# Check status
python scripts/main.py --status

# Debug mode
python scripts/main.py --task "test" --verbose

# Check logs
tail -f ~/.claude/logs/claude-proxy.log
```

## Version

- v1.0.0 (2026-01-18): Initial release

