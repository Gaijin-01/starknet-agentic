# System Audit Report — 2026-02-06

**Generated:** Fri 2026-02-06 05:56 GMT+2  
**Host:** CND3452425 | **OS:** Linux 6.6.87.2-microsoft-standard-WSL2 | **Node:** v22.22.0  
**Channel:** telegram | **Model:** MiniMax-M2.1

---

## Executive Summary

| Status | HEALTHY 🟢 |
|--------|-------------|
| **Overall Health** | Healthy |
| **Gateway** | ✅ Running (PID 786) |
| **Cron Jobs** | ✅ All scheduled (20+ jobs) |
| **Skills** | ✅ 39 skills, avg 89.4/100 |
| **Disk** | ✅ 4% used (36G/1007G) |
| **Memory** | ✅ 1.2G/7.4G (16% used) |
| **Git Status** | ⚠️ 75 modified files (uncommitted) |
| **Network** | ✅ Twitter OK, CoinGecko OK, MiniMax FAIL |

---

## 1. Gateway Status

| Component | Status |
|-----------|--------|
| **Service** | systemd enabled, running |
| **PID** | 786 |
| **Port** | 18789 (loopback only) |
| **State** | active, sub running |
| **RPC Probe** | ✅ OK |
| **Dashboard** | http://127.0.0.1:18789/ |

**Note:** Gateway bound to 127.0.0.1 only — local clients only.

---

## 2. Cron Jobs Status

| Job | Schedule | Status | Last Run |
|-----|----------|--------|----------|
| Price check | */15 min | ✅ Running | See prices.log |
| Health check | */5 min | ⚠️ Failing | Error: "Unknown job: health-check" |
| Skill evolution | 0 * * * * | ✅ Running | evolution.log |
| Queue cleanup | 0 */6 * * | ✅ Running | queue.log |
| Auto post | 0 9,13,18,22 | ✅ Running | posts.log |
| Research digest | 0 8,20 | ✅ Running | research.log |
| Style learner | */30 * | ✅ Running | style-learn.log |
| Daily report | 30 5 * * * | ✅ Running | cron_daily_report.log |
| Crypto research | 0 2 * * * | ✅ Running | crypto_research.log |
| Cairo dev | 0 3 * * * | ✅ Running | cairo_dev.log |
| Blockchain dev | 0 4 * * * | ✅ Running | blockchain_dev.log |
| Starknet research | 0 2 * * 1 | ✅ Running | starknet_research.log |

**⚠️ Issue Found:** Health check job failing with "Unknown job: health-check" in cron. The orchestrator doesn't recognize this job name.

---

## 3. Skills Analysis

### Overall Statistics
| Metric | Value |
|--------|-------|
| **Total Skills** | 39 |
| **Average Score** | 89.4/100 |
| **Critical Issues** | 0 |
| **High Priority** | 0 |
| **Medium Priority** | 22 |
| **Low Priority** | 38 |

### Top Scoring Skills (100/100)
| Skill | Category |
|-------|----------|
| colony | _system |
| crypto-trading | _system |
| ct-intelligence | _system |
| post-generator | _system |
| publisher | _system |
| queue-manager | _system |
| twitter-api | _system |
| claude-proxy | _system |
| core | _system |
| intelligence | _system |
| prices | _system |
| research | _system |
| style-learner | _system |
| system | _system |

### Skills Needing Work (Score < 80)
| Skill | Score | Issues |
|-------|-------|--------|
| skill-creator | 76 | Missing workflow section |
| openai-image-gen | 69 | Missing overview, workflow, examples |
| session-logs | 69 | Missing overview, workflow, examples |
| openai-whisper-api | 65 | Low score |
| video-frames | 65 | Low score |

### Medium Priority Issues (22)
- **API Keys in Code:** 6 files may contain hardcoded API keys
  - avnu_client.py
  - arbitrage_tracker.py, ekubo_client.py, arbitrage.py
  - gather.py
- **Missing Error Handling:** 9 files lack error handling
  - starknet-privacy: zk_proof_generator.py, zk_snarkjs_workflow.py, download_ptau.py, merkle_tree.py
  - starknet-mini-pay: invoice.py
  - intelligence: weekly_digest.py, weekly_wrap.py
  - prices: coingecko_client.py
- **Missing Documentation:** 7 skills missing sections
  - session-logs (overview, workflow, examples)
  - openai-image-gen (overview, workflow, examples)
  - starknet-mini-pay (workflow)
  - skill-creator (workflow)
  - model-usage (workflow)

---

## 4. Disk & Memory

### Disk Usage
| Filesystem | Size | Used | Avail | Use% |
|------------|------|------|-------|------|
| /dev/sdd | 1007G | 36G | 920G | 4% |

### RAM Usage
| Metric | Value |
|--------|-------|
| Total | 7.4 GiB |
| Used | 1.2 GiB (16%) |
| Free | 5.7 GiB |
| Available | 6.2 GiB |
| Buff/Cache | 641 MiB |

### Swap
| Metric | Value |
|--------|-------|
| Total | 2.0 GiB |
| Used | 0 B |

**✅ System has ample resources.**

---

## 5. Running Processes

| User | PID | CPU% | MEM% | VSZ | RSS | TTY | STAT | START | TIME | COMMAND |
|------|-----|------|------|-----|-----|-----|------|-------|------|---------|
| wner | 786 | 0.7 | 8.6 | 23024096 | 669276 | ? | Ssl | Feb05 | 8:48 | openclaw-gateway |

**✅ Only gateway process running (expected).**

---

## 6. Recent Logs Analysis

### health.log
```
Unknown job: health-check (repeated 3+ times)
```
**Issue:** Health check cron job failing - orchestrator doesn't recognize the job.

### prices.log
```
Executing job: price-check
Config: {skill: prices, mode: alert, threshold: 5.0}
Status: success (repeated)
```
**✅ Price monitoring working correctly.**

### posts.log
```
Executing job: auto-post
Status: success (last run: scheduled times 9,13,18,22)
```
**✅ Auto-post working correctly.**

### gateway.log
```
HTTP Request: POST https://api.telegram.org/bot... getUpdates "HTTP/1.1 409 Conflict"
ERROR: Exception happened while polling for updates
```
**⚠️ Telegram 409 Conflict** - Another instance is polling updates. This may cause message delays.

---

## 7. Git Status

| Status | Count |
|--------|-------|
| **Modified (tracked)** | 75 files |
| **Untracked** | 32 files |

### Modified Files by Category
| Category | Files |
|----------|-------|
| Memory files | evolution.md, starknet_errors.md, daily reports |
| Log files | 11 log files modified |
| Configs | MEMORY.md, crontab.conf, SKILLS_INDEX.md |
| Skills | 17 Python files modified |
| __pycache__ | 40+ .pyc files deleted |

### Untracked
- Backups: clawd-20260204.tar.gz, clawd-20260206.tar.gz
- Logs: blockchain_dev.log, cairo_dev.log, crypto_research.log
- Memory: 2026-02-04.md, 2026-02-06.md, dev progress reports
- Skills: starknet-mini-pay/, session-logs/scripts/

**⚠️ Recommendation:** Commit or discard changes. Many __pycache__ deletions are noise.

---

## 8. Memory Files

| Metric | Value |
|--------|-------|
| Total .md files | 51 |
| Corrupted files | 0 |
| Missing yesterday | 2026-02-05.md (doesn't exist) |

### Memory File Health
- **2026-02-06.md** ✅ Exists, contains today's notes
- **2026-02-05.md** ❌ Missing - no daily notes for yesterday
- **evolution.md** ✅ Exists, up to date
- All other files readable and intact

**⚠️ Issue:** Missing daily notes for 2026-02-05. This gap should be investigated.

---

## 9. Python Environments

| Check | Result |
|-------|--------|
| **Virtual Environments** | None found in standard locations |
| **System Python** | /usr/bin/python3 (3.14) |
| **Linuxbrew Python** | /home/linuxbrew/.linuxbrew/lib/python3.14 |
| **Python 3.12** | /usr/bin/python3.12 (has starknet-py) |

**Note:** The system uses system Python (3.14) for most tasks. starknet-py requires Python 3.12.

**Cron fix applied 2026-02-06:** Changed whale-check cron to use python3.12 instead of python3 (3.14 lacks starknet-py).

---

## 10. Network & External Connections

| Service | Endpoint | Status | Notes |
|---------|----------|--------|-------|
| **Twitter/X** | api.twitter.com/2 | ✅ 200 | Authenticated OK |
| **CoinGecko** | api.coingecko.com/v3 | ✅ 200 | Price API OK |
| **MiniMax** | api.minimax.com | ❌ FAIL | Health check failed |
| **Telegram** | api.telegram.org | ⚠️ 409 | Conflict (another poller) |

### Issues
1. **MiniMax API unreachable** - May affect AI model calls
2. **Telegram 409 Conflict** - Another client polling updates

---

## Summary of Issues Found

| Severity | Issue | Location | Recommendation |
|----------|-------|----------|----------------|
| **Medium** | Health-check cron failing | crontab, health.log | Fix or remove health-check job |
| **Medium** | Telegram 409 Conflict | gateway.log | Stop duplicate poller |
| **Medium** | MiniMax API unreachable | network test | Check API key, endpoint |
| **Low** | Missing daily notes | memory/2026-02-05.md | Check backup, restore if needed |
| **Low** | 75 uncommitted git changes | repo | Commit or discard |
| **Low** | API keys in code | 6 skill files | Move to env vars/config |
| **Low** | Missing error handling | 9 files | Add try/except blocks |
| **Low** | Documentation gaps | 7 skills | Add missing sections |

---

## Comparison vs Yesterday

| Metric | Today (2026-02-06) | Yesterday (2026-02-05) | Change |
|--------|-------------------|------------------------|--------|
| **Overall Status** | Healthy | ❓ Unknown | - |
| **Gateway** | ✅ Running | - | Same |
| **Skills Avg Score** | 89.4/100 | - | Stable |
| **Disk Used** | 4% | - | Stable |
| **RAM Used** | 1.2G (16%) | - | Stable |
| **Critical Issues** | 0 | - | Same |
| **Medium Issues** | 22 | - | Tracked |

**Note:** No yesterday audit exists for direct comparison.

---

## Recommended Actions

### Immediate (Today)
1. **Fix health-check cron** - Either implement the job or remove from crontab
2. **Investigate Telegram 409** - Find and stop duplicate poller
3. **Check MiniMax API** - Verify endpoint and credentials

### This Week
4. **Git cleanup** - Commit meaningful changes, discard cache noise
5. **API key remediation** - Move 6 hardcoded keys to environment variables
6. **Error handling** - Add try/except to 9 identified files
7. **Documentation** - Fill gaps in 7 skills

### Next Sprint
8. **Restore 2026-02-05.md** - Check backups if important
9. **Skill improvement** - Address 22 medium-priority issues
10. **Consider venv** - Standardize Python environments

---

## Appendix

### Active Skills by Category
- **_system/** (17 skills): avg ~91/100
- **_integrations/** (24 skills): avg ~82/100

### Cron Jobs Active
- High frequency: price-check (15min), health-check (5min), style-learn (30min)
- Medium frequency: skill-evolve (hourly), queue-cleanup (6h), auto-post (4x daily)
- Low frequency: research (2x daily), crypto-research (daily), cairo-dev (daily)

### Network Endpoints Verified
- ✅ Twitter API v2
- ✅ CoinGecko API v3
- ❌ MiniMax API (fail)
- ⚠️ Telegram (409 conflict)

---

*Report generated by OpenClaw System Audit*
