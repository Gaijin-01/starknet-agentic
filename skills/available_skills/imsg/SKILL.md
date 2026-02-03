---
name: imsg
description: iMessage/SMS CLI for listing chats, history, watch, and sending.
homepage: https://imsg.to
metadata:
  {
    "openclaw":
      {
        "emoji": "📨",
        "os": ["darwin"],
        "requires": { "bins": ["imsg"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "steipete/tap/imsg",
              "bins": ["imsg"],
              "label": "Install imsg (brew)",
            },
          ],
      },
  }
---

# imsg

## Overview

Read and send iMessage/SMS messages using the macOS Messages app via CLI. Useful for notifications, alerts, or messaging workflows that integrate with Messages.

**When to use:**
- Sending iMessage/SMS notifications from scripts
- Reading recent chat history
- Monitoring chats for specific content
- Automating message delivery
- Integrating Messages with other tools

**Key capabilities:**
- List recent chats
- View message history
- Watch for new messages in real-time
- Send messages with text and attachments
- Search chat history

**Requirements:**
- macOS with Messages.app signed in
- Full Disk Access for terminal
- Automation permission for sending

## Workflow

```
1. Verify Messages.app is signed in and has permissions
2. List chats to find the target conversation
3. Read history if needed
4. Send message or monitor for new messages
5. Confirm delivery (if sending)
```

## Examples

**List recent chats (JSON format):**
```bash
imsg chats --limit 10 --json
```

**View chat history:**
```bash
imsg history --chat-id 1 --limit 20 --attachments --json
```

**Watch for new messages:**
```bash
imsg watch --chat-id 1 --attachments
```

**Send a text message:**
```bash
imsg send --to "+14155551212" --text "Hello from Moltbot"
```

**Send with attachment:**
```bash
imsg send --to "+14155551212" --text "Here's the file" --file /path/pic.jpg
```

Requirements

- Messages.app signed in
- Full Disk Access for your terminal
- Automation permission to control Messages.app (for sending)

Common commands

- List chats: `imsg chats --limit 10 --json`
- History: `imsg history --chat-id 1 --limit 20 --attachments --json`
- Watch: `imsg watch --chat-id 1 --attachments`
- Send: `imsg send --to "+14155551212" --text "hi" --file /path/pic.jpg`

Notes

- `--service imessage|sms|auto` controls delivery.
- Confirm recipient + message before sending.
