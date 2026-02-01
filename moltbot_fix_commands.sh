#!/bin/bash
# ============================================
# MOLTBOT FIX COMMANDS - Generated 2026-01-30
# ============================================
# Based on actual system state:
# - Config: ~/.moltbot/moltbot.json
# - Crontab: 16 active jobs
# - Node: v25.4.0 (system), v24.13.0 (NVM default)
# - Gateway: Running on port 18789
# ============================================

set -e

echo "=============================================="
echo "MOLTBOT FIX SCRIPT - $(date)"
echo "=============================================="

# ============================================
# 1. SUB-AGENT ALLOWLIST (CRITICAL)
# ============================================
echo ""
echo ">>> 1. SUB-AGENT ALLOWLIST FIX"

# The agents.allowlist doesn't exist - we need to add it
CONFIG_FILE="$HOME/.moltbot/moltbot.json"
BACKUP_FILE="$HOME/.moltbot/moltbot.json.fix_backup_$(date +%Y%m%d_%H%M%S)"

cp "$CONFIG_FILE" "$BACKUP_FILE"
echo "Backup created: $BACKUP_FILE"

# Add agents.allowlist section if not exists
if ! jq -e '.agents.allowlist' "$CONFIG_FILE" > /dev/null 2>&1; then
    echo "Adding agents.allowlist to config..."
    jq '.agents.allowlist = {
      "enabled": true,
      "agents": ["evolver", "researcher", "poster", "debugger", "writer", "analyst", "default"]
    }' "$CONFIG_FILE" > /tmp/moltbot_fix.json && mv /tmp/moltbot_fix.json "$CONFIG_FILE"
    echo "✅ Allowlist added"
else
    echo "✅ Allowlist already exists"
fi

echo "Current allowlist:"
jq '.agents.allowlist // "Not set"' "$CONFIG_FILE"

# ============================================
# 2. KILL STALE EVOLVER SESSION
# ============================================
echo ""
echo ">>> 2. CLEANUP STALE SESSIONS"

# Check for evolver processes
EVOLVER_PID=$(pgrep -f "evolver" 2>/dev/null || echo "")
if [ -n "$EVOLVER_PID" ]; then
    echo "Found evolver processes: $EVOLVER_PID"
    read -p "Kill? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kill $EVOLVER_PID 2>/dev/null || true
        echo "✅ Killed evolver PID $EVOLVER_PID"
    fi
else
    echo "No stale evolver processes found"
fi

# ============================================
# 3. GATEWAY CONFIG RECONCILIATION
# ============================================
echo ""
echo ">>> 3. GATEWAY CONFIG CHECK"

echo "Gateway running config:"
curl -s "http://localhost:18789/config" 2>/dev/null | jq -S '.' > /tmp/gw_running.json || echo "Cannot fetch running config"

echo "File config:"
cat "$CONFIG_FILE" | jq -S '.' > /tmp/gw_file.json

echo "Diff:"
if diff -q /tmp/gw_running.json /tmp/gw_file.json > /dev/null 2>&1; then
    echo "✅ Configs match"
else
    echo "⚠️ Configs differ - manual review needed"
    echo "Running config:"
    cat /tmp/gw_running.json | head -50
fi

# ============================================
# 4. NODE.JS VERSION FIX
# ============================================
echo ""
echo ">>> 4. NODE.JS VERSION"

echo "Current Node versions:"
echo "  System: $(node -v 2>/dev/null || echo 'N/A')"
echo "  NVM default: $(source ~/.nvm/nvm.sh && nvm version default 2>/dev/null || echo 'N/A')"
echo "  NVM current: $(source ~/.nvm/nvm.sh && nvm version node 2>/dev/null || echo 'N/A')"

echo ""
echo "Options:"
echo "  A) Set NVM default to v22 (LTS)"
echo "  B) Keep v24.13.0 (current)"
echo "  C) Skip"
read -p "Choose (A/B/C): " -n 1 -r
echo
case $REPLY in
    A|a)
        echo "Setting NVM default to v22..."
        source ~/.nvm/nvm.sh && nvm install 22 && nvm alias default 22
        echo "✅ NVM default set to v22"
        echo "⚠️ Restart gateway to apply: moltbot gateway restart"
        ;;
    B|b)
        echo "Skipping Node.js change"
        ;;
    *)
        echo "Skipping"
        ;;
esac

# ============================================
# 5. QUEUE DIAGNOSTICS
# ============================================
echo ""
echo ">>> 5. QUEUE STATE"

QUEUE_FILE="$HOME/.moltbot/cron/jobs.json"
if [ -f "$QUEUE_FILE" ]; then
    echo "Queue file exists: $QUEUE_FILE"
    echo "Queue mode: $(jq -r '.mode // "unknown"' $QUEUE_FILE 2>/dev/null || echo 'Cannot read')"
    echo "Queue depth: $(jq '.jobs | length' $QUEUE_FILE 2>/dev/null || echo 'N/A')"
else
    echo "Queue file not found at $QUEUE_FILE"
fi

# ============================================
# 6. API QUOTA HEALTH CHECK
# ============================================
echo ""
echo ">>> 6. API HEALTH"

echo "MiniMax API:"
curl -s -X POST "https://api.minimax.io/anthropic/v1/messages" \
    -H "Authorization: Bearer $MINIMAX_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"model":"minimax/MiniMax-M2.1","messages":[{"role":"user","content":"ping"}],"max_tokens":5}' \
    | jq '.error // "OK"' 2>/dev/null || echo "Cannot reach MiniMax"

echo ""
echo "Brave Search:"
# Test search with minimal query
WEB_SEARCH_RESULT=$(web_search "test" --count 1 2>&1) || echo "Search failed"

# ============================================
# 7. CRON HEALTH AUDIT
# ============================================
echo ""
echo ">>> 7. CRON HEALTH"

CRON_COUNT=$(crontab -l 2>/dev/null | grep -c "^[^#]" || echo "0")
echo "Active cron jobs: $CRON_COUNT"

echo ""
echo "Recent errors in logs:"
LOG_FILE="$HOME/clawd/logs/cron.log"
if [ -f "$LOG_FILE" ]; then
    tail -20 "$LOG_FILE" | grep -E "(ERROR|FAIL|exception)" || echo "No recent errors"
else
    echo "Log file not found: $LOG_FILE"
fi

# ============================================
# 8. MEMORY SYSTEM CLEANUP
# ============================================
echo ""
echo ">>> 8. MEMORY CLEANUP"

echo "Memory file sizes:"
du -sh "$HOME/clawd/memory/" 2>/dev/null || echo "memory/ not found"
du -sh "$HOME/clawd/MEMORY.md" 2>/dev/null || echo "MEMORY.md not found"

echo ""
echo "Daily memories (keep last 30):"
MEMORY_DIR="$HOME/clawd/memory"
if [ -d "$MEMORY_DIR" ]; then
    OLD_FILES=$(find "$MEMORY_DIR" -name "*.md" -mtime +30 2>/dev/null | wc -l)
    echo "  Old files (>30 days): $OLD_FILES"
    if [ "$OLD_FILES" -gt 0 ]; then
        read -p "Archive old memories? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            find "$MEMORY_DIR" -name "*.md" -mtime +30 -exec gzip {} \; 2>/dev/null || true
            echo "✅ Archived $(find "$MEMORY_DIR" -name "*.md.gz" | wc -l) files"
        fi
    fi
fi

# ============================================
# SUMMARY
# ============================================
echo ""
echo "=============================================="
echo "FIX SUMMARY"
echo "=============================================="
echo "✅ Config backup: $BACKUP_FILE"
echo "✅ Allowlist added: agents.allowlist"
echo "⚠️  Node.js: Manual review needed"
echo "⚠️  Gateway config: Manual review if diffs found"
echo "✅ Cron jobs: $CRON_COUNT active"
echo "=============================================="
echo "NEXT STEPS:"
echo "1. Review $BACKUP_FILE before applying"
echo "2. Run: moltbot gateway restart"
echo "3. Test sub-agent spawning: agents_list"
echo "=============================================="
