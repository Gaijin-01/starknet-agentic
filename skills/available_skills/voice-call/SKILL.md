---
name: voice-call
description: Start voice calls via the OpenClaw voice-call plugin.
metadata:
  {
    "openclaw":
      {
        "emoji": "📞",
        "skillKey": "voice-call",
        "requires": { "config": ["plugins.entries.voice-call.enabled"] },
      },
  }
---

# Voice Call

## Overview

Start voice calls via the Moltbot voice-call plugin. Supports multiple providers (Twilio, Telnyx, Plivo) and mock mode for testing.

**When to use:**
- Initiating voice calls from Moltbot
- Text-to-speech phone calls
- Call status monitoring
- Multi-provider support

**Key capabilities:**
- Initiate calls with message
- Text-to-speech delivery
- Call status checks
- Multiple provider support
- Mock mode for testing

## Workflow

```
1. Ensure voice-call plugin is enabled
2. Configure provider credentials
3. Use CLI or tool to initiate call
4. Monitor call status
5. End call when done
```

## Examples

**CLI - Make a call:**
```bash
moltbot voicecall call --to "+15555550123" --message "Hello from Moltbot"
```

**CLI - Check status:**
```bash
moltbot voicecall status --call-id <id>
```

**Tool - Initiate call:**
```json
{
  "action": "initiate_call",
  "message": "Your appointment reminder",
  "to": "+15555550123"
}
```

**Tool - Speak to user:**
```json
{
  "action": "speak_to_user",
  "callId": "abc123",
  "message": "Your order has arrived"
}
```

**Tool - End call:**
```json
{
  "action": "end_call",
  "callId": "abc123"
}
```

**Tool - Get status:**
```json
{
  "action": "get_status",
  "callId": "abc123"
}
```

## CLI

```bash
openclaw voicecall call --to "+15555550123" --message "Hello from OpenClaw"
openclaw voicecall status --call-id <id>
```

## Tool

Use `voice_call` for agent-initiated calls.

Actions:

- `initiate_call` (message, to?, mode?)
- `continue_call` (callId, message)
- `speak_to_user` (callId, message)
- `end_call` (callId)
- `get_status` (callId)

Notes:

- Requires the voice-call plugin to be enabled.
- Plugin config lives under `plugins.entries.voice-call.config`.
- Twilio config: `provider: "twilio"` + `twilio.accountSid/authToken` + `fromNumber`.
- Telnyx config: `provider: "telnyx"` + `telnyx.apiKey/connectionId` + `fromNumber`.
- Plivo config: `provider: "plivo"` + `plivo.authId/authToken` + `fromNumber`.
- Dev fallback: `provider: "mock"` (no network).
