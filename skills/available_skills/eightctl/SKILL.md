---
name: eightctl
description: Control Eight Sleep pods (status, temperature, alarms, schedules).
homepage: https://eightctl.sh
metadata:
  {
    "openclaw":
      {
        "emoji": "🎛️",
        "requires": { "bins": ["eightctl"] },
        "install":
          [
            {
              "id": "go",
              "kind": "go",
              "module": "github.com/steipete/eightctl/cmd/eightctl@latest",
              "bins": ["eightctl"],
              "label": "Install eightctl (go)",
            },
          ],
      },
  }
---

# eightctl

## Overview

Control Eight Sleep pod temperature, schedules, and alarms via CLI. Manage smart bed settings programmatically for sleep optimization and automation.

**When to use:**
- Adjusting bed temperature from scripts
- Setting up sleep schedules
- Managing alarms for wake times
- Checking pod status
- Integrating with home automation
- Sleep routine automation

**Key capabilities:**
- Temperature control (on/off, specific degrees)
- Alarm management (list, create, dismiss)
- Schedule management
- Audio control
- Base angle adjustment
- Pod status monitoring

**Requirements:**
- Eight Sleep pod with account
- Authentication via config or environment

## Workflow

```
1. Authenticate with Eight Sleep credentials
2. Check current pod status
3. Adjust temperature or manage alarms
4. Verify changes applied
5. Set up schedules if needed
```

## Examples

**Check pod status:**
```bash
eightctl status
```

**Turn on and set temperature to 20°C:**
```bash
eightctl on
eightctl temp 20
```

**Turn off pod:**
```bash
eightctl off
```

**List alarms:**
```bash
eightctl alarm list
```

**Create a new alarm:**
```bash
eightctl alarm create --time 07:00 --days Mon,Tue,Wed,Thu,Fri
```

**Dismiss active alarm:**
```bash
eightctl alarm dismiss
```

**List schedules:**
```bash
eightctl schedule list
```

**Create a temperature schedule:**
```bash
eightctl schedule create --start 22:00 --temp 18 --end 07:00 --temp 20
```

**Control audio:**
```bash
eightctl audio play
eightctl audio pause
```

Auth

- Config: `~/.config/eightctl/config.yaml`
- Env: `EIGHTCTL_EMAIL`, `EIGHTCTL_PASSWORD`

Quick start

- `eightctl status`
- `eightctl on|off`
- `eightctl temp 20`

Common tasks

- Alarms: `eightctl alarm list|create|dismiss`
- Schedules: `eightctl schedule list|create|update`
- Audio: `eightctl audio state|play|pause`
- Base: `eightctl base info|angle`

Notes

- API is unofficial and rate-limited; avoid repeated logins.
- Confirm before changing temperature or alarms.
