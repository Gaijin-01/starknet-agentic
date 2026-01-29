# 🤖 Clawdbot Technical Audit Report
**Generated:** 2026-01-28 23:45 GMT+2
**System:** Linux WSL (CND3452425)

---

## 1. System Prompt (Full)

The system prompt contains core instructions including:
- **Identity:** Clawd (C), AI assistant, emoji 🤖
- **Soul:** Be genuinely helpful, have opinions, be resourceful, remember you're a guest
- **Memory System:** Daily logs in `memory/YYYY-MM-DD.md`, long-term in `MEMORY.md`
- **Skills:** 20+ skills available (1password, bird, blogwatcher, etc.)
- **Runtime:** MiniMax-M2.1 model, 200k context window, Telegram channel

---

## 2. Skills Directory Structure

```
/home/wner/clawd/skills/
├── adaptive-routing/         # Query classification (1-29 fast, 30-70 std, 71-100 deep)
│   ├── classifier.py
│   └── README.md
├── bird/                     # X/Twitter CLI (cookies-based auth)
├── blogwatcher/              # RSS/Atom feed monitoring
├── camsnap/                  # Camera snapshots
├── claude-proxy/             # Claude API proxy with self-improvement
│   ├── prompts/system.md
│   └── scripts/*.py (main.py, llm_client.py, code_gen.py, etc.)
├── config/                   # Configuration loader
│   ├── config.yaml
│   ├── config.json
│   └── config_loader.py
├── gifgrep/                  # GIF search/download
├── himalaya/                 # Email CLI (IMAP/SMTP)
├── mcporter/                 # MCP server management
├── notion/                   # Notion API integration
├── oracle/                   # One-shot LLM queries with file context
├── post-generator/           # Post generation for X/Twitter
│   └── scripts/post_generator.py
├── prices/                   # Price tracking
├── queue-manager/            # Post queue management
│   └── scripts/queue_manager.py
├── research/                 # Web search (Brave/Serper/DuckDuckGo)
│   └── scripts/research.py
├── skill-evolver/            # Skill self-improvement
│   └── scripts/evolve.py, analyze.py, utils.py
├── songsee/                  # Song metadata lookup
├── style-learner/            # User style learning
│   ├── data/observations/*.jsonl
│   ├── profiles/style_profile.json
│   └── scripts/*.py (main.py, analyzer.py, generator.py, executor.py)
├── summarize/                # URL/YouTube/file summarization
├── tmux/                     # Terminal session control
├── universal-skills/         # Universal skill framework
├── video-frames/             # Video frame extraction
├── weather/                  # Weather (wttr.in)
├── x-algorithm-optimizer/    # X algorithm optimization
│   ├── algorithm_scorer.py
│   └── STRATEGY.md
└── README.md
```

---

## 3. Config Structure (`~/.clawdbot/clawdbot.json`)

```json
{
  "meta": {
    "lastTouchedVersion": "2026.1.24-3",
    "lastTouchedAt": "2026-01-28T20:35:00.411Z"
  },
  "wizard": {
    "lastRunAt": "2026-01-28T20:35:00.408Z",
    "lastRunCommand": "doctor"
  },
  "auth": {
    "profiles": {
      "minimax:default": {
        "provider": "minimax",
        "mode": "api_key"
      }
    }
  },
  "models": {
    "mode": "merge",
    "providers": {
      "minimax": {
        "baseUrl": "https://api.minimax.io/anthropic",
        "api": "anthropic-messages",
        "models": [
          {
            "id": "MiniMax-M2.1",
            "name": "MiniMax M2.1",
            "reasoning": false,
            "contextWindow": 200000,
            "maxTokens": 8192,
            "cost": {"input": 15, "output": 60}
          },
          {
            "id": "MiniMax-M2.1-Fast",
            "contextWindow": 50000,
            "maxTokens": 2048
          },
          {
            "id": "MiniMax-M2.1-Deep",
            "reasoning": true,
            "contextWindow": 200000,
            "maxTokens": 16384
          }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {"primary": "minimax/MiniMax-M2.1"},
      "workspace": "/home/wner/clawd",
      "maxConcurrent": 4,
      "subagents": {"maxConcurrent": 8}
    }
  },
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "8237705028:AAGZjD4BknKi6lpePY9ab06rwkhslMiQtXM"
    }
  },
  "gateway": {
    "port": 18789,
    "bind": "loopback",
    "auth": {"mode": "token"}
  },
  "skills": {
    "install": {"nodeManager": "pnpm"},
    "entries": {
      "adaptive-routing": {"enabled": true},
      "bird": {"enabled": true},
      "claude-proxy": {"enabled": true},
      // ... 12 skills total
    }
  }
}
```

---

## 4. Environment Variables (Keys Only)

**API Keys:**
- `AUTH_TOKEN`
- `BRAVE_API_KEY`
- `COINGECKO_API_KEY`
- `CT0` (X/Twitter cookies)
- `GOOGLE_API_KEY`
- `MINIMAX_API_KEY`

**System:**
- `CLAWDBOT_GATEWAY_PORT`
- `CLAWDBOT_GATEWAY_TOKEN`
- `CLAWDBOT_SERVICE_KIND`
- `CLAWDBOT_SERVICE_VERSION`
- `CLAWDBOT_SYSTEMD_UNIT`

**Node/Path:**
- `NVM_DIR`
- `NVM_BIN`
- `NODE_OPTIONS`
- `PNPM_HOME`
- `PATH`

**User:**
- `HOME`
- `USER`
- `SHELL`
- `LANG`

---

## 5. File Tree (Complete)

```
/home/wner/clawd/
├── .clawdhub/
│   └── lock.json
├── .env.local
├── .git/
├── .learnings/
│   ├── ERRORS.md
│   └── LEARNINGS.md
├── AGENTS.md              (6376 bytes)
├── BOOTSTRAP.md           (1465 bytes)
├── HEARTBEAT.md           (86 bytes)
├── IDENTITY.md            (469 bytes)
├── MEMORY.md              (1939 bytes)
├── SOUL.md                (1673 bytes)
├── TOOLS.md               (856 bytes)
├── USER.md                (589 bytes)
├── canvas/
│   └── index.html
├── config/
│   └── mcporter.json
├── memory/
│   ├── 2026-01-24.md
│   ├── 2026-01-24-1425.md
│   ├── 2026-01-27.md
│   ├── 2026-01-27-2137.md
│   └── 2026-01-28-2057.md
├── post_queue/
│   └── ready/
│       ├── post_20260123_175501.txt
│       └── post_20260123_180000.txt
├── skills/
│   ├── adaptive-routing/
│   ├── bird/
│   ├── blogwatcher/
│   ├── camsnap/
│   ├── claude-proxy/
│   ├── config/
│   ├── gifgrep/
│   ├── himalaya/
│   ├── mcporter/
│   ├── notion/
│   ├── oracle/
│   ├── post-generator/
│   ├── prices/
│   ├── queue-manager/
│   ├── research/
│   ├── skill-evolver/
│   ├── songsee/
│   ├── style-learner/
│   ├── summarize/
│   ├── tmux/
│   ├── universal-skills/
│   ├── video-frames/
│   ├── weather/
│   └── x-algorithm-optimizer/
├── style-learning/
│   ├── analyze_tweets.py
│   ├── config.json
│   ├── drafts.jsonl
│   ├── generate_and_post.py
│   ├── observations.jsonl
│   ├── reply_quote.py
│   ├── reply_quote_algo.py
│   └── x_executor.py
├── workflow.py
├── clawdbot_system_report.json.gz
├── clawdbot_system_report.json
├── clawdbot_system_report.txt
├── clawdbot-extension.tar.gz
└── skills/README.md
```

---

## 6. Architecture Overview

### Core Components

```
┌─────────────────────────────────────────────────────┐
│                    Clawdbot Gateway                 │
│                    (Port 18789)                     │
├─────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │   Agent     │  │   Session   │  │   Memory    │ │
│  │   Manager   │  │   Manager   │  │   Store     │ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  Channels   │  │   Skills    │  │   Tools     │ │
│  │ (Telegram)  │  │  (20+)      │  │   (50+)     │ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  Gateway    │  │  Auth       │  │  Config     │ │
│  │  Daemon     │  │  Manager    │  │  Loader     │ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────┘
```

### Data Flow

1. **Message In** → Telegram Channel → Session Manager
2. **Classification** → Adaptive Routing (Fast/Standard/Deep)
3. **Processing** → Agent + Skills + Tools
4. **Memory** → Daily Logs → MEMORY.md (curated)
5. **Response** → Channel → User

---

## 7. Capabilities & Tools Summary

### Installed Skills (20+)
| Category | Skills |
|----------|--------|
| **Communication** | himalaya (email), gog (Google Workspace), slack |
| **Social** | bird (X/Twitter), blogwatcher (RSS) |
| **Development** | github, tmux, mcporter, oracle |
| **Content** | summarize, gifgrep, video-frames, post-generator |
| **Data** | notion, prices, research, style-learner |
| **System** | weather, 1password, config, queue-manager |
| **AI** | gemini, claude-proxy, skill-evolver |

### Core Tools (50+)
- `read`, `write`, `edit` — File operations
- `exec`, `process` — Shell execution
- `browser` — Web automation
- `message` — Multi-channel messaging
- `gateway` — Gateway management
- `memory_search`, `memory_get` — Memory retrieval
- `sessions_*` — Sub-agent management
- `tts` — Text-to-speech
- `image` — Image analysis
- `nodes` — Node control
- `canvas` — UI rendering

---

## 8. Memory Storage Format

### Daily Logs (`memory/YYYY-MM-DD.md`)
```markdown
# Session: 2026-01-28 20:57:39 UTC

- **Session Key**: agent:main:main
- **Session ID**: a88317e6-...
- **Source**: telegram

## Conversation Summary

user: [Telegram message]
assistant: Response
```

### Long-term Memory (`MEMORY.md`)
```markdown
# Memory Summary

## 🔧 Core Stack
| Component | Status | Details |
|-----------|--------|---------|
| Clawdbot | ✅ Running | Gateway 18789 |

## 📝 Quick Commands
```bash
# Gateway
clawdbot gateway start
```
```

---

## 9. API Endpoints

### Internal Gateway
- `http://localhost:18789/` — Web UI
- `http://localhost:18789/api/*` — REST API

### External (Tailscale ngrok)
- `https://dessie-unexonerated-supercolossally.ngrok-free.dev/webapp`

### Model APIs
- `https://api.minimax.io/anthropic` — MiniMax models
- Brave Search API — Web search

---

## 10. Known Issues (as of 2026-01-27)

| Issue | Level | Status |
|-------|-------|--------|
| Node v24.13.0 via NVM | Medium | Should be system Node 22+ |
| Gateway config mismatch | Medium | Entrypoint mismatch |
| Tailscale not found | Low | serve failed: spawn tailscale ENOENT |
| Sub-agents stalled (5) | Low | "abort failed: no_active_run" |
| /home/wner/clawdbot folder (2GB) | Low | May be deletable |

---

*Report generated by Clawdbot Technical Audit Module*
