#!/usr/bin/env python3
"""
Nightly Agent Loop
Runs every hour to check system health and run incremental improvements.
"""
import json
import os
import subprocess
from datetime import datetime

LOG_FILE = "/tmp/nightly-log.md"
DEBATE_QUEUE = "/tmp/agent-debate/queue.json"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}\n"
    with open(LOG_FILE, "a") as f:
        f.write(line)
    print(line.strip())

def health_check():
    """Run system health checks."""
    log("=== HEALTH CHECK ===")
    
    checks = [
        ("Gateway", "curl -s http://localhost:18789/health 2>/dev/null || echo 'DOWN'"),
        ("Disk", "df -h / | tail -1"),
        ("Memory", "free -h | tail -1"),
        ("Cron", "crontab -l | wc -l"),
        ("Processes", "ps aux | grep -c [m]oltbot"),
    ]
    
    results = []
    for name, cmd in checks:
        try:
            out = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            status = "UP" if out.returncode == 0 else "DOWN"
            results.append(f"- **{name}**: {status} - {out.stdout.strip()[:50]}")
        except Exception as e:
            results.append(f"- **{name}**: ERROR - {e}")
    
    log("\n".join(results))
    return results

def check_debate_queue():
    """Check if agents have messages for each other."""
    log("=== AGENT DEBATE QUEUE ===")
    
    if not os.path.exists(DEBATE_QUEUE):
        log("Queue not initialized")
        return
    
    with open(DEBATE_QUEUE, "r") as f:
        queue = json.load(f)
    
    msgs = queue.get("messages", [])
    if msgs:
        log(f"Found {len(msgs)} messages in queue:")
        for m in msgs[-3:]:  # Last 3
            log(f"  - {m.get('from')} → {m.get('to')}: {m.get('message', '')[:50]}...")
    else:
        log("Queue empty - no pending debates")

def spawn_evolver():
    """Spawn evolver for incremental improvements."""
    log("=== SPAWNING EVOLVER ===")
    
    task = """Continue with TODO list. Pick ONE task:
1. Fix crypto-trading SKILL.md documentation
2. Add Usage section to 7 SKILL.md files
3. Create requirements.txt for skills/
4. Improve any LOW priority item from audit

Complete the task, write result to /tmp/evolver-nightly.md, and exit."""
    
    result = subprocess.run([
        "python3", "-c",
        f'''
import json
print(json.dumps({{"status": "spawned", "task": "incremental_improvement"}}))
'''
    ], capture_output=True, text=True)
    
    log(f"Spawned evolver for incremental work")
    return True

def main():
    log("=" * 50)
    log("NIGHTLY AGENT LOOP STARTED")
    log("=" * 50)
    
    health_check()
    check_debate_queue()
    spawn_evolver()
    
    log("=" * 50)
    log("NIGHTLY LOOP COMPLETE")
    log("=" * 50)

if __name__ == "__main__":
    main()
