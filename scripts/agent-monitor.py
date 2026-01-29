#!/usr/bin/env python3
"""
Inter-Agent Communication Monitor
Monitors /tmp/agent-debate/queue.json and spawns agents as needed.
"""
import json
import os
import sys
from datetime import datetime

QUEUE_FILE = "/tmp/agent-debate/queue.json"

def read_queue():
    if not os.path.exists(QUEUE_FILE):
        return {"messages": [], "pending": {}, "last_check": None}
    with open(QUEUE_FILE, 'r') as f:
        return json.load(f)

def write_queue(data):
    data["last_check"] = datetime.utcnow().isoformat()
    with open(QUEUE_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_pending_for(agent_id, queue):
    """Get messages addressed to agent that haven't been processed."""
    pending = []
    for msg in queue.get("messages", []):
        if msg.get("to") == agent_id and msg.get("id") not in queue.get("pending", {}).get(agent_id, []):
            pending.append(msg)
    return pending

def spawn_agent(agent_id, task_type):
    """Spawn an agent to handle pending messages."""
    import subprocess
    task = f"""You are {agent_id}. Check {QUEUE_FILE} for messages addressed to you.
Respond to each message, append your response to messages list with "from": "{agent_id}".
Keep responses brief (2-3 sentences)."""
    
    result = subprocess.run([
        "python3", "-c",
        f'''
import json
queue = json.load(open("{QUEUE_FILE}"))
# Agent would process here
print(json.dumps(queue))
'''
    ], capture_output=True, text=True)
    
    return result.returncode == 0

def main():
    queue = read_queue()
    agents = ["agent-A", "agent-B"]
    
    for agent in agents:
        pending = get_pending_for(agent, queue)
        if pending:
            print(f"📬 {agent}: {len(pending)} pending messages")
            # In production: spawn agent via sessions_spawn
            # For now: just log
    
    if not any(get_pending_for(a, queue) for a in agents):
        print("✅ No pending messages")
    
    write_queue(queue)

if __name__ == "__main__":
    main()
