#!/bin/bash
# Arbitrage Signal Cron Setup
# Run scan every 15 minutes

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH="${PYTHON_PATH:-python3}"
CRON_LINE="*/15 * * * * cd $SCRIPT_DIR && $PYTHON_PATH arbitrage_signal.py >> /tmp/arbitrage.log 2>&1"

echo "Setting up arbitrage signal cron job..."
echo "$CRON_LINE"

# Check if cron already exists
if crontab -l 2>/dev/null | grep -q "arbitrage_signal.py"; then
    echo "⚠️ Cron job already exists"
else
    # Add to crontab
    (crontab -l 2>/dev/null || true; echo "$CRON_LINE") | crontab -
    echo "✅ Cron job added"
fi

# Show current crontab
echo ""
echo "Current crontab:"
crontab -l
