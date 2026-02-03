---
name: wacli
description: Send WhatsApp messages to other people or search/sync WhatsApp history via the wacli CLI (not for normal user chats).
homepage: https://wacli.sh
metadata:
  {
    "openclaw":
      {
        "emoji": "📱",
        "requires": { "bins": ["wacli"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "steipete/tap/wacli",
              "bins": ["wacli"],
              "label": "Install wacli (brew)",
            },
            {
              "id": "go",
              "kind": "go",
              "module": "github.com/steipete/wacli/cmd/wacli@latest",
              "bins": ["wacli"],
              "label": "Install wacli (go)",
            },
          ],
      },
  }
---

# wacli

<<<<<<< HEAD
Use `wacli` only when the user explicitly asks you to message someone else on WhatsApp or when they ask to sync/search WhatsApp history.
Do NOT use `wacli` for normal user chats; OpenClaw routes WhatsApp conversations automatically.
If the user is chatting with you on WhatsApp, you should not reach for this tool unless they ask you to contact a third party.
=======
## Overview

Send WhatsApp messages and search/sync history via CLI. Use for messaging third parties or searching history - NOT for routine user chats which Moltbot handles automatically.

**When to use:**
- Sending WhatsApp messages to other people
- Searching message history
- Syncing WhatsApp data
- Contacting third parties via WhatsApp

**Key capabilities:**
- Send text messages
- Send files to contacts/groups
- Search message history
- Sync and backfill history
- Find chats and conversations

## Workflow

```
1. Authenticate via QR code
2. Sync history if needed
3. Find target chat/group
4. Send message or search history
5. Confirm before sending
```

## Examples

**Authenticate:**
```bash
wacli auth
```

**Sync history:**
```bash
wacli sync --follow
```

**List chats:**
```bash
wacli chats list --limit 20 --query "contact name"
```

**Search messages:**
```bash
wacli messages search "invoice" --limit 20 --chat <jid>
```

**Search by date range:**
```bash
wacli messages search "order" --after 2025-01-01 --before 2025-12-31
```

**Send text message:**
```bash
wacli send text --to "+14155551212" --message "Hello! Are you free at 3pm?"
```

**Send to group:**
```bash
wacli send text --to "1234567890-123456789@g.us" --message "Running 5 min late."
```

**Send file:**
```bash
wacli send file --to "+14155551212" --file /path/agenda.pdf --caption "Agenda"
```

**Backfill history:**
```bash
wacli history backfill --chat <jid> --requests 2 --count 50
```
>>>>>>> de3edc587 (chore: stage changes before v2026.2.1 update)

Safety

- Require explicit recipient + message text.
- Confirm recipient + message before sending.
- If anything is ambiguous, ask a clarifying question.

Auth + sync

- `wacli auth` (QR login + initial sync)
- `wacli sync --follow` (continuous sync)
- `wacli doctor`

Find chats + messages

- `wacli chats list --limit 20 --query "name or number"`
- `wacli messages search "query" --limit 20 --chat <jid>`
- `wacli messages search "invoice" --after 2025-01-01 --before 2025-12-31`

History backfill

- `wacli history backfill --chat <jid> --requests 2 --count 50`

Send

- Text: `wacli send text --to "+14155551212" --message "Hello! Are you free at 3pm?"`
- Group: `wacli send text --to "1234567890-123456789@g.us" --message "Running 5 min late."`
- File: `wacli send file --to "+14155551212" --file /path/agenda.pdf --caption "Agenda"`

Notes

- Store dir: `~/.wacli` (override with `--store`).
- Use `--json` for machine-readable output when parsing.
- Backfill requires your phone online; results are best-effort.
- WhatsApp CLI is not needed for routine user chats; it’s for messaging other people.
- JIDs: direct chats look like `<number>@s.whatsapp.net`; groups look like `<id>@g.us` (use `wacli chats list` to find).
