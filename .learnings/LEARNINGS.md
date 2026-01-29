## [LRN-20260124-001] subagent_execution

**Logged**: 2026-01-24T15:40:00Z
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
Spawned sub-agents failed to execute tasks - returned empty message histories

### Details
Attempted to run three sub-agent tasks in parallel using `sessions_spawn`:
1. `skills-full-update` - Add all skills to config
2. `cron-research-privacy-blockchains` - Add cron jobs
3. `mcp-servers-integration` - Integrate MCP servers

All sub-agents accepted the task (returned "accepted" status with sessionKey) but produced empty message histories when queried with sessions_history immediately after spawning.

**Root Cause (from docs):**
- `sessions_spawn` is **always non-blocking** - returns immediately with `{status: "accepted", runId, childSessionKey}`
- Sub-agents run asynchronously in background (lane: `subagent`)
- Results are announced back to requester chat when complete
- Checking `sessions_history` immediately shows empty because sub-agent hasn't started/executed yet

### Context
- Used sessions_spawn tool with main agent
- Tasks were well-defined with clear requirements
- Sub-agents showed in sessions_list with updated timestamps but no actual work done
- No error occurred - this is expected async behavior

### Suggested Action
1. **Understand async nature**: Sub-agents are designed to run in background and announce back
2. **Don't poll sessions_history**: Let sub-agents complete and announce results naturally
3. **Watch for announce messages**: Results appear in requester chat channel
4. **Use `/subagents` commands**: `/subagents list` or `/subagents log <id>` to monitor progress
5. **Set timeout**: Use `runTimeoutSeconds` to prevent infinite runs

### Metadata
- Source: conversation
- Related Files: /home/wner/.clawdbot/clawdbot.json
- Tags: subagent, execution, debugging
- See Also: ERR-20260124-001 (if created)

---
