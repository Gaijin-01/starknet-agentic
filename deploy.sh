#!/bin/bash
# Claude-Proxy Deployment Script
# Usage: ./deploy.sh [all|cron|verify|test|status]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Ensure required directories exist
setup_directories() {
    log_info "Setting up directories..."
    mkdir -p logs
    mkdir -p memory
    mkdir -p post_queue/ready
    mkdir -p post_queue/drafts
    
    for skill in prices research post-generator style-learner camsnap mcporter songsee adaptive-routing; do
        mkdir -p "skills/$skill/scripts"
    done
    
    log_info "Directories created"
}

# Install dependencies
install_deps() {
    log_info "Installing Python dependencies..."
    
    # Core dependencies
    pip3 install requests python-dotenv --quiet 2>/dev/null || true
    
    # Check for skill-specific dependencies
    if [ -f "skills/prices/requirements.txt" ]; then
        pip3 install -r skills/prices/requirements.txt --quiet 2>/dev/null || true
    fi
    
    if [ -f "skills/research/requirements.txt" ]; then
        pip3 install -r skills/research/requirements.txt --quiet 2>/dev/null || true
    fi
    
    log_info "Dependencies installed"
}

# Make scripts executable
make_executable() {
    log_info "Making scripts executable..."
    
    find skills -name "*.py" -type f -exec chmod +x {} \; 2>/dev/null || true
    
    # Ensure orchestrator is executable
    chmod +x skills/orchestrator.py 2>/dev/null || true
    
    log_info "Scripts are now executable"
}

# Install cron jobs
install_cron() {
    log_info "Installing cron jobs..."
    
    # Backup existing crontab
    crontab -l > /tmp/crontab.backup 2>/dev/null || true
    
    # Install new crontab
    crontab crontab.conf
    
    log_info "Cron jobs installed"
    log_info "Current crontab:"
    crontab -l
}

# Verify installation
verify() {
    log_info "Verifying installation..."
    
    echo ""
    echo "=== Directory Structure ==="
    ls -la
    
    echo ""
    echo "=== Logs Directory ==="
    ls -la logs/ 2>/dev/null || echo "logs/ not found"
    
    echo ""
    echo "=== Skills ==="
    for skill in skills/*/; do
        if [ -d "$skill" ]; then
            skill_name=$(basename "$skill")
            has_scripts=$(ls -d "$skill/scripts" 2>/dev/null && echo "✓ scripts/" || echo "✗ no scripts/")
            has_skill_md=$(ls -f "$skill/SKILL.md" 2>/dev/null && echo "✓ SKILL.md" || echo "✗ no SKILL.md")
            echo "  $skill_name: $has_scripts $has_skill_md"
        fi
    done
    
    echo ""
    echo "=== Cron Jobs ==="
    crontab -l 2>/dev/null || echo "No cron jobs installed"
    
    echo ""
    log_info "Verification complete"
}

# Test routing
test_routing() {
    log_info "Testing query routing..."
    
    python3 skills/orchestrator.py --test-route "сколько стоит $BTC"
    echo ""
    python3 skills/orchestrator.py --test-route "напиши пост про DeFi"
    echo ""
    python3 skills/orchestrator.py --test-route "привет как дела"
    
    log_info "Routing tests complete"
}

# Check service status
status() {
    log_info "Checking service status..."
    
    echo ""
    echo "=== Systemctl Services ==="
    for service in claude-proxy clawdbot; do
        if systemctl is-active --quiet "$service" 2>/dev/null; then
            echo -e "${GREEN}●${NC} $service: active"
        else
            echo -e "${YELLOW}○${NC} $service: not running"
        fi
    done
    
    echo ""
    echo "=== Cron Daemon ==="
    if pgrep -x "cron" > /dev/null; then
        echo -e "${GREEN}●${NC} cron: running"
    else
        echo -e "${YELLOW}○${NC} cron: not running"
    fi
    
    echo ""
    echo "=== Recent Logs ==="
    tail -5 logs/orchestrator.log 2>/dev/null || echo "No orchestrator logs"
}

# Run manual job
run_job() {
    local job=$1
    log_info "Running job: $job"
    python3 skills/orchestrator.py --job "$job"
}

# Main entry point
case "${1:-all}" in
    all)
        setup_directories
        install_deps
        make_executable
        install_cron
        verify
        ;;
    dirs)
        setup_directories
        ;;
    deps)
        install_deps
        ;;
    cron)
        install_cron
        ;;
    verify)
        verify
        ;;
    test)
        test_routing
        ;;
    status)
        status
        ;;
    job)
        if [ -z "$2" ]; then
            log_error "Job name required"
            echo "Usage: $0 job <job_name>"
            echo "Available jobs: price-check, research-digest, auto-post, health-check, queue-cleanup, backup"
            exit 1
        fi
        run_job "$2"
        ;;
    *)
        echo "Usage: $0 {all|dirs|deps|cron|verify|test|status|job}"
        exit 1
        ;;
esac

log_info "Done!"
