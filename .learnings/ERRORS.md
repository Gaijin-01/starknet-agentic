## [ERR-20260124-001] sessions_spawn_async_behavior

**Logged**: 2026-01-24T15:40:00Z
**Priority**: low
**Status**: resolved
**Area**: infra

### Summary
sessions_spawn creates sub-agents that execute asynchronously - not a bug, expected behavior

### Error
```
sessions_history returned: {"sessionKey": "...", "messages": []}
All spawned sub-agents (3 tasks) produced empty execution histories
```

### Context
- Command: sessions_spawn with agentId="main", detailed task descriptions
- Expected: Sub-agents execute tasks immediately
- Actual: Sub-agents run in background, announce back when done

### Resolution
- **Resolved**: 2026-01-24T15:45:00Z
- Root cause: `sessions_spawn` is intentionally non-blocking (returns immediately)
- Sub-agents run in `subagent` lane asynchronously
- Results are announced to requester chat when complete
- No error occurred - was misunderstanding of async design

### Suggested Fix
Not needed - this is working as designed. For synchronous execution, consider:
1. Running tasks directly in main session
2. Waiting for sub-agent announce messages
3. Using `/subagents log <id>` to monitor progress

### Metadata
- Reproducible: N/A - expected behavior
- Related Files: /home/wner/.clawdbot/clawdbot.json
- Tags: subagent, sessions_spawn, async

---
