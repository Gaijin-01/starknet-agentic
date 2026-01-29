# Memory Summary (2026-01-29 UPDATE)

## 🔧 Core Stack

| Component | Status | Details |
|-----------|--------|---------|
| Clawdbot | ✅ Running | Gateway 18789, uptime ~3 days |
| MiniMax-M2.1 | ✅ Default | 200k context |
| Telegram | ✅ Connected | @Groove_Armada |
| **Unified Orchestrator** | ✅ NEW | Combined routing + tier + execution |

## 📊 System Status (2026-01-29)

### Skills (10 total)
| Skill | SKILL.md | Scripts | Status |
|-------|----------|---------|--------|
| claude-proxy | ✅ | ✅ main.py, llm_client.py, code_gen.py, reasoning.py, self_improve.py | 100/100 |
| prices | ✅ | ✅ prices.py | 100/100 |
| research | ✅ | ✅ research.py | 100/100 |
| post-generator | ✅ | ✅ post_generator.py, persona_post.py | 100/100 |
| queue-manager | ✅ | ✅ queue_manager.py | 100/100 |
| style-learner | ✅ | ✅ main.py, analyzer.py, executor.py, generator.py | 91/100 |
| adaptive-routing | ✅ | ✅ SKILL.md (FIXED) | 85+ |
| camsnap | ✅ | ✅ main.py (NEW) | Ready |
| mcporter | ✅ | ✅ main.py (NEW) | Ready |
| songsee | ✅ | ✅ main.py (NEW) | Ready |

**Average Score**: 65.1 → 85+ (after medium priority fixes)

### Infrastructure
- ✅ unified_orchestrator.py (16KB, full routing + execution)
- ✅ 64 cron jobs installed
- ✅ deploy.sh (full deployment script)
- ✅ crontab.conf (scheduled jobs)
- ✅ Git repo with 12 commits

## 🎯 Three-Tier Model System

| Tier | Score | Model | Use Case |
|------|-------|-------|----------|
| **Fast** | 1-29 | MiniMax-M2.1-Fast | Simple questions, greetings |
| **Standard** | 30-70 | MiniMax-M2.1 | Standard tasks, coding |
| **Deep** | 71-100 | MiniMax-M2.1-Deep | Complex reasoning, research |

## 🛠️ What I Can Do Myself

### Without Asking
| Category | Examples |
|----------|----------|
| **File ops** | read, write, edit, list, search |
| **Git** | status, log, add, commit |
| **System** | python scripts, cron, df, ls |
| **Web** | web_search, web_fetch |
| **Images** | image analysis |
| **Memory** | memory_search, memory_get, update |

### Must Ask First
| Action | Reason |
|--------|--------|
| Send emails | External action |
| Tweet/post | Public action |
| SSH to servers | Security |
| Delete files | Use trash only |

## 🤖 Sub-Agents I Can Create

| Agent | Purpose |
|-------|---------|
| `coding-agent` | Write/refactor code |
| `debugging-agent` | Fix bugs, investigate |
| `research-agent` | Deep web research |
| `writing-agent` | Content creation |
| `analysis-agent` | Data analysis |
| `default` | General purpose |

Usage: `sessions_spawn task="..." label="..."`

## 📅 Cron Schedule (All Active)

| Job | Schedule | Status |
|-----|----------|--------|
| Price check | */15 min | ✅ |
| Health check | */5 min | ✅ |
| Queue cleanup | 0 */6h | ✅ |
| Auto post | 0 9,13,18,22 | ✅ |
| Research digest | 0 8,20 | ✅ |
| Style retrain | Sun 3AM | ✅ |
| Backup | 0 4 * | ✅ |
| Log rotation | 0 0 * | ✅ |

## 🐦 Bird/X Stack (Unchanged)

**Persona**: SefirotWatch
- Tone: minimal, cryptic, confident
- Emoji: 🐺🔥
- Words: 10 avg

**Skills**: research, prices, x-algorithm-optimizer, style-learner, post-generator, queue-manager

**X Algorithm Weights**:
- Quote: 3.5x | Reply: 3.0x | Repost: 2.0x | Like: 1.0x

**Optimal Daily Mix**: 10 replies + 3 quotes + 1 thread + 2 posts

**Peak Hours**: 6-9, 12-14, 18-21 UTC

## 🌐 Remote Interface

- URL: https://dessie-unexonerated-supercolossally.ngrok-free.dev/webapp
- Russian localization: ✅
- Dashboard: ✅

## ⚠️ Known Issues (UPDATED)

| Issue | Level | Status |
|-------|-------|--------|
| Node v24.13.0 via NVM | Medium | Still present |
| Gateway config mismatch | Medium | Still present |
| Tailscale not found | Low | Still present |
| Sub-agents stalled | Low | Still present |
| Docstrings missing | Medium | PENDING |
| Error handling in persona_post.py | Medium | PENDING |

## 📁 Key Files

| File | Purpose |
|------|---------|
| `unified_orchestrator.py` | Main routing + execution engine |
| `crontab.conf` | Cron job definitions |
| `deploy.sh` | Deployment script |
| `MY_CAPABILITIES.md` | My capabilities reference |
| `~/.clawdbot/clawdbot.json` | Main config |
| `~/clawd/skills/` | Skills directory |
| `~/clawd/memory/` | Daily notes |
| `~/clawd/post_queue/` | Post queue |

## 🔗 Quick Commands

```bash
# System status
python3 unified_orchestrator.py -s          # List skills
python3 unified_orchestrator.py -l          # List cron jobs
python3 unified_orchestrator.py -t "msg"    # Test routing
python3 unified_orchestrator.py -g          # Generate crontab

# Deployment
./deploy.sh verify                          # Verify installation
crontab -l                                  # Check cron

# Git
git log --oneline -5                        # Recent commits
```

## 💡 Key Learnings

1. **Skills are modular** - each skill has SKILL.md + scripts/
2. **Orchestrator unifies routing** - skill selection + model tier in one
3. **Cron handles scheduled tasks** - everything runs automatically
4. **Memory is file-based** - daily notes + curated MEMORY.md
5. **Sub-agents for complex tasks** - sessions_spawn for heavy lifting

---

*Last updated: 2026-01-29*
*Major update: Added unified_orchestrator.py, fixed all critical skill issues*
