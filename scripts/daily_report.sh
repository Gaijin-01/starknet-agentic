#!/bin/bash
# Daily Report Script - generates summary of system status, prices, posts

BOT_HOME=/home/wner/clawd
LOG_DIR=$BOT_HOME/logs
REPORT_FILE=$LOG_DIR/daily_report_$(date +%Y-%m-%d).txt

echo "=== Daily Report - $(date) ===" > $REPORT_FILE
echo "" >> $REPORT_FILE

# System health
echo "📊 System Health:" >> $REPORT_FILE
df -h / | tail -1 >> $REPORT_FILE
free -h | head -2 >> $REPORT_FILE
echo "" >> $REPORT_FILE

# Git status
echo "🔀 Git Status:" >> $REPORT_FILE
cd $BOT_HOME && git status --short | head -20 >> $REPORT_FILE
echo "" >> $REPORT_FILE

# Recent commits
echo "📝 Recent Commits:" >> $REPORT_FILE
git log --oneline -5 >> $REPORT_FILE
echo "" >> $REPORT_FILE

# Cron jobs count
echo "⏰ Cron Jobs:" >> $REPORT_FILE
crontab -l 2>/dev/null | grep -v "^#" | grep -v "^$" | wc -l >> $REPORT_FILE
echo "" >> $REPORT_FILE

# Log summary
echo "📜 Today's Logs:" >> $REPORT_FILE
ls -la $LOG_DIR/*.log 2>/dev/null | wc -l >> $REPORT_FILE

# Send to Telegram
if [ -f "$REPORT_FILE" ]; then
    cat $REPORT_FILE
fi
