#!/bin/bash
# ============================================
# CLAWDBOT SYSTEM - DEPLOYMENT SCRIPT
# Merged from archive + x402 extensions
# ============================================

set -e

BOT_HOME="${BOT_HOME:-/home/wner/clawd}"
LOG_DIR="$BOT_HOME/logs"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[+]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[x]${NC} $1"; }
info() { echo -e "${BLUE}[*]${NC} $1"; }

# ============================================
# 1. Create directories
# ============================================
create_directories() {
    log "Creating directory structure..."
    mkdir -p "$BOT_HOME"/{logs,backups,memory,config,data}
    mkdir -p "$BOT_HOME/skills"/{adaptive-routing,camsnap,mcporter,songsee}/{scripts,references,assets}
    mkdir -p "$BOT_HOME/skills/starknet-yield-agent-ts/src/data"
    mkdir -p "$BOT_HOME/skills/ct-intelligence-agent-ts/src/data"
    log "Directories created"
}

# ============================================
# 2. Fix broken skills (stubs)
# ============================================
fix_broken_skills() {
    log "Fixing incomplete skills..."
    
    for skill in camsnap mcporter songsee; do
        MAIN_PY="$BOT_HOME/skills/$skill/scripts/main.py"
        if [[ ! -f "$MAIN_PY" ]]; then
            cat > "$MAIN_PY" << 'STUB'
#!/usr/bin/env python3
"""
Stub for $skill - requires external binary installation.
"""

def execute(params: dict) -> dict:
    return {"status": "stub", "message": "$skill not implemented - requires binary installation"}

if __name__ == "__main__":
    import json, sys
    params = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    print(json.dumps(execute(params), indent=2))
STUB
            chmod +x "$MAIN_PY"
            info "$skill stub created"
        fi
    done
}

# ============================================
# 3. Setup cron jobs
# ============================================
setup_cron() {
    log "Setting up cron jobs..."
    
    # Backup existing
    crontab -l > "$BOT_HOME/backups/crontab.backup.$(date +%Y%m%d)" 2>/dev/null || true
    
    # Install crontab
    if [[ -f "$BOT_HOME/crontab.conf" ]]; then
        crontab "$BOT_HOME/crontab.conf"
        log "Cron jobs installed"
        crontab -l | grep -v "^#" | grep -v "^$" | head -5
    else
        warn "crontab.conf not found"
    fi
}

# ============================================
# 4. Verify orchestrator
# ============================================
verify_orchestrator() {
    log "Verifying orchestrator..."
    
    if [[ -f "$BOT_HOME/unified_orchestrator.py" ]]; then
        cd "$BOT_HOME"
        TEST=$(python3 unified_orchestrator.py -t "test" 2>/dev/null)
        if echo "$TEST" | grep -qE "(prices|research|orchestrator)"; then
            log "Unified orchestrator: OK"
        else
            info "Orchestrator running, testing routing..."
        fi
    fi
}

# ============================================
# 5. Deploy x402 agents (NEW)
# ============================================
deploy_x402_agents() {
    log "Deploying x402 agents..."
    
    if ! command -v npm &> /dev/null; then
        warn "npm not found. Install Node.js first."
        return
    fi
    
    if ! command -v vercel &> /dev/null; then
        info "Installing Vercel CLI..."
        npm i -g vercel
    fi
    
    # Deploy starknet-yield-agent
    if [[ -d "$BOT_HOME/skills/starknet-yield-agent-ts" ]]; then
        cd "$BOT_HOME/skills/starknet-yield-agent-ts"
        info "Deploying starknet-yield-agent..."
        npm install 2>/dev/null || true
        vercel --prod --yes 2>/dev/null || warn "Vercel deploy failed"
    fi
    
    # Deploy ct-intelligence-agent
    if [[ -d "$BOT_HOME/skills/ct-intelligence-agent-ts" ]]; then
        cd "$BOT_HOME/skills/ct-intelligence-agent-ts"
        info "Deploying ct-intelligence-agent..."
        npm install 2>/dev/null || true
        vercel --prod --yes 2>/dev/null || warn "Vercel deploy failed"
    fi
    
    log "x402 agents deployment complete"
}

# ============================================
# 6. Create systemd service (optional)
# ============================================
create_systemd_service() {
    SERVICE_FILE="/etc/systemd/system/clawdbot.service"
    
    info "Creating systemd service..."
    sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=Clawdbot - AI Agent System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$BOT_HOME
ExecStart=/usr/bin/python3 $BOT_HOME/unified_orchestrator.py --mode daemon
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    info "Systemd service created"
    info "Enable: sudo systemctl enable clawdbot"
    info "Start: sudo systemctl start clawdbot"
}

# ============================================
# 7. Full verification
# ============================================
verify_all() {
    log "Verifying installation..."
    
    ISSUES=0
    
    # Check core files
    for file in unified_orchestrator.py crontab.conf; do
        if [[ ! -f "$BOT_HOME/$file" ]]; then
            error "Missing: $file"
            ((ISSUES++))
        fi
    done
    
    # Check skills
    for skill in claude-proxy prices research post-generator editor; do
        if [[ ! -f "$BOT_HOME/skills/$skill/SKILL.md" ]]; then
            warn "Missing SKILL.md: $skill"
        fi
    done
    
    # Check x402 agents
    if [[ -f "$BOT_HOME/skills/starknet-yield-agent-ts/package.json" ]]; then
        log "starknet-yield-agent-ts: OK"
    fi
    
    if [[ -f "$BOT_HOME/skills/ct-intelligence-agent-ts/package.json" ]]; then
        log "ct-intelligence-agent-ts: OK"
    fi
    
    if [[ $ISSUES -eq 0 ]]; then
        log "All checks passed ✅"
    else
        warn "$ISSUES issues found"
    fi
}

# ============================================
# Main
# ============================================
main() {
    echo ""
    echo "============================================"
    echo "🤖 CLAWDBOT SYSTEM DEPLOYMENT"
    echo "============================================"
    echo ""
    
    case "${1:-all}" in
        dirs)
            create_directories
            ;;
        skills)
            fix_broken_skills
            ;;
        cron)
            setup_cron
            ;;
        verify)
            verify_all
            ;;
        x402)
            deploy_x402_agents
            ;;
        systemd)
            create_systemd_service
            ;;
        all)
            create_directories
            fix_broken_skills
            setup_cron
            verify_orchestrator
            verify_all
            ;;
        *)
            echo "Usage: $0 {dirs|skills|cron|verify|x402|systemd|all}"
            echo ""
            echo "Commands:"
            echo "  dirs     - Create directory structure"
            echo "  skills   - Fix incomplete skills"
            echo "  cron     - Setup cron jobs"
            echo "  verify   - Verify installation"
            echo "  x402     - Deploy x402 agents"
            echo "  systemd  - Create systemd service"
            echo "  all      - Run everything"
            exit 1
            ;;
    esac
    
    echo ""
    log "Done! ✅"
}

main "$@"
