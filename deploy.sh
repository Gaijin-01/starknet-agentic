#!/bin/bash
# ============================================
# Claude-Proxy Bot Deployment Script
# ============================================

set -e

BOT_HOME="${BOT_HOME:-/home/wner/clawd}"
LOG_DIR="$BOT_HOME/logs"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[+]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[x]${NC} $1"; }

# ============================================
# 1. Create missing directories
# ============================================
create_directories() {
    log "Creating directory structure..."
    
    mkdir -p "$BOT_HOME"/{logs,backups,memory,config}
    mkdir -p "$BOT_HOME/skills"/{adaptive-routing,camsnap,mcporter,songsee}/{scripts,references,assets}
    
    log "Directories created"
}

# ============================================
# 2. Fix broken skills
# ============================================
fix_broken_skills() {
    log "Fixing broken skills..."
    
    # adaptive-routing - copy SKILL.md if exists locally
    if [[ -f "./skills/adaptive-routing/SKILL.md" ]]; then
        cp "./skills/adaptive-routing/SKILL.md" "$BOT_HOME/skills/adaptive-routing/SKILL.md"
        log "adaptive-routing SKILL.md installed"
    fi
    
    # Create stub main.py for incomplete skills
    for skill in camsnap mcporter songsee; do
        MAIN_PY="$BOT_HOME/skills/$skill/scripts/main.py"
        if [[ ! -f "$MAIN_PY" ]]; then
            cat > "$MAIN_PY" << 'STUB'
#!/usr/bin/env python3
"""
Stub implementation for skill.
TODO: Implement actual functionality.
"""

def execute(params: dict) -> dict:
    """
    Execute skill with given parameters.
    
    Args:
        params: Skill-specific parameters
        
    Returns:
        Execution result dict
    """
    return {
        "status": "not_implemented",
        "message": f"Skill not yet implemented. Received params: {params}"
    }

if __name__ == "__main__":
    import json
    import sys
    
    if len(sys.argv) > 1:
        params = json.loads(sys.argv[1])
    else:
        params = {}
    
    result = execute(params)
    print(json.dumps(result, indent=2))
STUB
            chmod +x "$MAIN_PY"
            log "$skill main.py stub created"
        fi
    done
}

# ============================================
# 3. Install orchestrator
# ============================================
install_orchestrator() {
    log "Installing orchestrator..."
    
    if [[ -f "./orchestrator.py" ]]; then
        cp "./orchestrator.py" "$BOT_HOME/orchestrator.py"
        chmod +x "$BOT_HOME/orchestrator.py"
        log "Orchestrator installed"
    else
        error "orchestrator.py not found in current directory"
    fi
}

# ============================================
# 4. Setup cron jobs
# ============================================
setup_cron() {
    log "Setting up cron jobs..."
    
    if [[ -f "./crontab.conf" ]]; then
        # Backup existing crontab
        crontab -l > "$BOT_HOME/backups/crontab.backup.$(date +%Y%m%d)" 2>/dev/null || true
        
        # Install new crontab
        crontab "./crontab.conf"
        log "Cron jobs installed"
        
        # Verify
        log "Current cron jobs:"
        crontab -l | grep -v "^#" | grep -v "^$" | head -10
    else
        warn "crontab.conf not found, skipping cron setup"
    fi
}

# ============================================
# 5. Create systemd service (optional)
# ============================================
create_systemd_service() {
    log "Creating systemd service..."
    
    SERVICE_FILE="/etc/systemd/system/claude-proxy.service"
    
    sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=Claude-Proxy Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$BOT_HOME
ExecStart=/usr/bin/python3 $BOT_HOME/gateway.py
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    log "Systemd service created"
    warn "To enable: sudo systemctl enable claude-proxy"
    warn "To start: sudo systemctl start claude-proxy"
}

# ============================================
# 6. Verify installation
# ============================================
verify_installation() {
    log "Verifying installation..."
    
    ISSUES=0
    
    # Check critical files
    for file in skills/orchestrator.py; do
        if [[ ! -f "$BOT_HOME/$file" ]]; then
            error "Missing: $file"
            ((ISSUES++))
        fi
    done
    
    # Check skill directories
    for skill in adaptive-routing prices queue-manager research post-generator style-learner; do
        if [[ ! -f "$BOT_HOME/skills/$skill/SKILL.md" ]]; then
            warn "Missing SKILL.md: $skill"
        fi
    done
    
    # Test orchestrator
    if [[ -f "$BOT_HOME/skills/orchestrator.py" ]]; then
        cd "$BOT_HOME"
        TEST=$(python3 skills/orchestrator.py --test-route "price of btc" 2>/dev/null)
        if echo "$TEST" | grep -q "prices"; then
            log "Orchestrator routing: OK"
        else
            warn "Orchestrator routing: needs verification"
        fi
    fi
    
    if [[ $ISSUES -eq 0 ]]; then
        log "Installation verified successfully"
    else
        error "$ISSUES issues found"
    fi
}

# ============================================
# Main
# ============================================
main() {
    echo "============================================"
    echo "Claude-Proxy Bot Deployment"
    echo "============================================"
    echo ""
    
    case "${1:-all}" in
        dirs)
            create_directories
            ;;
        skills)
            fix_broken_skills
            ;;
        orchestrator)
            install_orchestrator
            ;;
        cron)
            setup_cron
            ;;
        systemd)
            create_systemd_service
            ;;
        verify)
            verify_installation
            ;;
        all)
            create_directories
            fix_broken_skills
            install_orchestrator
            setup_cron
            verify_installation
            ;;
        *)
            echo "Usage: $0 {dirs|skills|orchestrator|cron|systemd|verify|all}"
            exit 1
            ;;
    esac
    
    echo ""
    log "Done!"
}

main "$@"
