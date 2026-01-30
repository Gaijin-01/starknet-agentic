#!/bin/bash
# ============================================
# Moltbot Config Backup Script
# Purpose: Prevent config drift from moltbot doctor --fix
# Usage: ./backup_moltbot_config.sh [--restore]
# ============================================

set -e

CONFIG_FILE="$HOME/.moltbot/moltbot.json"
BACKUP_DIR="$HOME/.moltbot/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/moltbot_$TIMESTAMP.json"
LATEST_LINK="$BACKUP_DIR/latest.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Function to create backup
backup() {
    if [ ! -f "$CONFIG_FILE" ]; then
        log_error "Config file not found: $CONFIG_FILE"
        exit 1
    fi

    cp "$CONFIG_FILE" "$BACKUP_FILE"
    ln -sf "$(basename "$BACKUP_FILE")" "$LATEST_LINK"

    log_info "Backup created: $BACKUP_FILE"
    log_info "Latest symlink updated: $LATEST_LINK"

    # Show backup stats
    BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/moltbot_*.json 2>/dev/null | wc -l)
    log_info "Total backups: $BACKUP_COUNT"

    # List recent backups
    echo ""
    log_info "Recent backups:"
    ls -lt "$BACKUP_DIR"/moltbot_*.json 2>/dev/null | head -5 | while read line; do
        echo "  $line"
    done
}

# Function to restore from backup
restore() {
    if [ ! -L "$LATEST_LINK" ] && [ ! -f "$LATEST_LINK" ]; then
        log_error "No backup found to restore from"
        exit 1
    fi

    LATEST_BACKUP=$(readlink -f "$LATEST_LINK")

    if [ ! -f "$LATEST_BACKUP" ]; then
        log_error "Backup file missing: $LATEST_BACKUP"
        exit 1
    fi

    log_warn "This will overwrite: $CONFIG_FILE"
    log_warn "Source backup: $LATEST_BACKUP"
    echo ""

    read -p "Continue with restore? (y/n): " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp "$LATEST_BACKUP" "$CONFIG_FILE"
        log_info "Config restored from: $LATEST_BACKUP"
        log_info "Run 'moltbot gateway restart' to apply changes"
    else
        log_info "Restore cancelled"
    fi
}

# Function to list backups with diff summary
list_backups() {
    log_info "Available backups:"
    echo ""

    for backup in "$BACKUP_DIR"/moltbot_*.json; do
        if [ -f "$backup" ]; then
            SIZE=$(du -h "$backup" | cut -f1)
            DATE=$(stat -c %y "$backup" 2>/dev/null | cut -d' ' -f1,2 | cut -d'.' -f1 || stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$backup")
            echo "  $(basename "$backup"): $SIZE, $DATE"
        fi
    done

    echo ""
    log_info "Latest: $(readlink -f "$LATEST_LINK" 2>/dev/null || echo 'Not set')"
}

# Function to show diff between backup and current
diff_backup() {
    if [ ! -f "$CONFIG_FILE" ]; then
        log_error "Current config not found"
        exit 1
    fi

    if [ ! -f "$LATEST_LINK" ]; then
        log_error "No backup found"
        exit 1
    fi

    echo ""
    log_info "Diff between current config and latest backup:"
    echo ""

    if command -v diff &> /dev/null; then
        diff -u "$LATEST_LINK" "$CONFIG_FILE" || true
    elif command -v jq &> /dev/null; then
        # Show JSON diff using jq
        echo "Backup keys: $(jq -r 'keys[]' "$LATEST_LINK" | tr '\n' ' ')"
        echo "Current keys: $(jq -r 'keys[]' "$CONFIG_FILE" | tr '\n' ' ')"
    else
        log_warn "No diff tool available. Showing file sizes:"
        ls -la "$LATEST_LINK" "$CONFIG_FILE"
    fi
}

# Main script logic
case "${1:-backup}" in
    backup)
        backup
        ;;
    restore)
        restore
        ;;
    list)
        list_backups
        ;;
    diff)
        diff_backup
        ;;
    help|--help|-h)
        echo "Moltbot Config Backup Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  backup    - Create a timestamped backup (default)"
        echo "  restore   - Restore from the latest backup"
        echo "  list      - List all available backups"
        echo "  diff      - Show diff between current and backup"
        echo "  help      - Show this help message"
        echo ""
        echo "Files:"
        echo "  Config:   $CONFIG_FILE"
        echo "  Backups:  $BACKUP_DIR/"
        ;;
    *)
        log_error "Unknown command: $1"
        echo "Run '$0 help' for usage"
        exit 1
        ;;
esac
