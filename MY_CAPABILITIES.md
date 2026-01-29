# Clawd Capabilities & System Status

## 📊 SYSTEM STATUS (2026-01-29)

### ✅ WORKING
- **10/10 skills** have SKILL.md
- **9/10 skills** have executable scripts
- **unified_orchestrator.py** installed and running
- **64 cron jobs** installed
- **Git repo** with 12 commits

### 🎯 WHAT'S WORKING
- Intent-based routing (prices, research, post-generator, etc.)
- Model tier selection (fast/standard/deep)
- Cron job scheduling
- CLI interfaces for most skills
- Documentation for all skills

---

## 🛠️ TASKS I CAN DO MYSELF

### File Operations
| Task | Command | Example |
|------|---------|---------|
| Read file | `read path` | `read memory/2026-01-29.md` |
| Write file | `write content path` | `write "# Title" README.md` |
| Edit file | `edit oldText newText` | `edit "foo" "bar"` |
| List files | `exec ls -la` | `ls -la` |
| Search files | `memory_search query` | `memory_search "prices"` |

### Git Operations
| Task | Command | Example |
|------|---------|---------|
| Commit | `exec git add -A && git commit -m "msg"` | - |
| Log | `exec git log --oneline` | - |
| Status | `exec git status` | - |

### System Operations
| Task | Command | Example |
|------|---------|---------|
| Run script | `exec python3 script.py` | - |
| Install cron | `exec crontab crontab.conf` | - |
| Check services | `exec systemctl status` | - |
| Disk usage | `exec df -h` | - |

### Web Operations
| Task | Command | Example |
|------|---------|---------|
| Web search | `web_search query` | `web_search "bitcoin news"` |
| Fetch page | `web_fetch url` | `web_fetch https://example.com` |

### Image Analysis
| Task | Command | Example |
|------|---------|---------|
| Analyze image | `image prompt path` | `image "what's in this?" photo.jpg` |

### Messaging
| Task | Command | Example |
|------|---------|---------|
| Send message | `message action=send message="text"` | Telegram |
| Send media | `message media=path message="caption"` | With file |

---

## 🤖 TASKS I CAN CREATE (Sub-Agents)

### Via `sessions_spawn`

| Agent Type | Purpose | When to Use |
|------------|---------|-------------|
| **coding-agent** | Write/refactor code | Complex programming tasks |
| **debugging-agent** | Fix bugs | Something broken, need investigation |
| **research-agent** | Deep web research | Topics requiring extensive search |
| **writing-agent** | Content creation | Blog posts, docs, copy |
| **analysis-agent** | Data analysis | Stats, reports, trends |
| **default** | General purpose | Anything else |

### Example Usage
```
sessions_spawn task="Fix the prices.py script, it has a bug" label="fix-prices"
```

---

## 🎯 WHAT I CAN AUTOMATE

### Scheduled Tasks (Cron)
| Task | Frequency | Status |
|------|-----------|--------|
| Price checks | */15 min | ✅ |
| Health checks | */5 min | ✅ |
| Queue cleanup | */6h | ✅ |
| Auto posts | 4x/day | ✅ |
| Research digest | 2x/day | ✅ |
| Style retrain | Weekly | ✅ |
| Backup | Daily | ✅ |
| Log rotation | Daily | ✅ |

### Event-Based
| Trigger | Action |
|---------|--------|
| User message | Route to skill |
| Price alert | Notify user |
| System error | Log + alert |

---

## 🚫 WHAT I CANNOT DO

### External Actions (Need Permission)
| Action | Why | Workaround |
|--------|-----|------------|
| Send emails | External API | Ask first |
| Tweet/post to social | Public action | Ask first |
| Make payments | Financial | Never |
| SSH to remote | Security | Ask first |
| Delete files permanently | Safety | Use `trash` only |

### System Limitations
| Limitation | Details |
|------------|---------|
| No root access | Can't install system packages |
| No sudo | Security restriction |
| No external API keys | Must be configured |
| Memory reset | Each session starts fresh |

---

## 📋 MY MEMORY SYSTEM

### Short-Term (Per Session)
- Files I read this session
- Current conversation

### Long-Term (Persistent)
| File | Contents |
|------|----------|
| `MEMORY.md` | Curated long-term memories |
| `memory/YYYY-MM-DD.md` | Daily logs |
| `SOUL.md` | My personality & boundaries |
| `USER.md` | Your preferences |
| `TOOLS.md` | Infrastructure notes |

### Remember
- **Tell me to remember** → I update daily notes
- **Important decisions** → I update MEMORY.md
- **Tasks for later** → I create cron jobs

---

## 🚀 QUICK START COMMANDS

```bash
# System status
python3 unified_orchestrator.py -s          # List skills
python3 unified_orchestrator.py -l          # List cron jobs
python3 unified_orchestrator.py -t "msg"    # Test routing

# Run system
./deploy.sh verify                          # Verify installation
crontab -l                                  # Check cron

# Development
git status                                  # Check changes
git log --oneline -5                        # Recent commits
```

---

## 🎯 DAILY WORKFLOW

```
Morning:
  1. Check cron logs (prices, health)
  2. Read daily notes
  3. Heartbeat check

During day:
  1. Route user messages
  2. Execute skills
  3. Remember important stuff

Evening:
  1. Research digest
  2. Auto post
  3. Backup
```

---

## 📞 INTEGRATION POINTS

| System | Connection |
|--------|------------|
| Telegram | Via Clawdbot gateway |
| Discord | Via Clawdbot gateway |
| Web APIs | Via web_search/web_fetch |
| Local files | Direct filesystem access |
| External tools | Via exec (with permission) |

---

*Last updated: 2026-01-29*
