---
name: ordercli
description: Foodora-only CLI for checking past orders and active order status (Deliveroo WIP).
homepage: https://ordercli.sh
metadata:
  {
    "openclaw":
      {
        "emoji": "🛵",
        "requires": { "bins": ["ordercli"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "steipete/tap/ordercli",
              "bins": ["ordercli"],
              "label": "Install ordercli (brew)",
            },
            {
              "id": "go",
              "kind": "go",
              "module": "github.com/steipete/ordercli/cmd/ordercli@latest",
              "bins": ["ordercli"],
              "label": "Install ordercli (go)",
            },
          ],
      },
  }
---

# ordercli

## Overview

Check past orders and track active order status via CLI. Currently supports Foodora; Deliveroo support is planned.

**When to use:**
- Checking order history
- Tracking active order ETA/status
- Previewing reorder (without placing)
- Managing order delivery

**Key capabilities:**
- View active orders with status
- Browse order history
- Preview reorder (safe, no cart changes)
- Track delivery in real-time
- Session/browser-based authentication

## Workflow

```
1. Set country and login
2. Check active orders or history
3. Preview reorder if needed
4. Confirm to place order
5. Track delivery status
```

## Examples

**Set country:**
```bash
ordercli foodora countries
ordercli foodora config set --country AT
```

**Login with session:**
```bash
ordercli foodora session chrome --url https://www.foodora.at/ --profile "Default"
```

**View active orders:**
```bash
ordercli foodora orders
```

**Watch for updates:**
```bash
ordercli foodora orders --watch
```

**Browse history:**
```bash
ordercli foodora history --limit 20
ordercli foodora history show <orderCode>
```

**Preview reorder (safe):**
```bash
ordercli foodora reorder <orderCode>
```

**Place order (confirm first!):**
```bash
ordercli foodora reorder <orderCode> --confirm
```

**Track delivery:**
```bash
ordercli foodora order <orderCode>
```

Quick start (Foodora)

- `ordercli foodora countries`
- `ordercli foodora config set --country AT`
- `ordercli foodora login --email you@example.com --password-stdin`
- `ordercli foodora orders`
- `ordercli foodora history --limit 20`
- `ordercli foodora history show <orderCode>`

Orders

- Active list (arrival/status): `ordercli foodora orders`
- Watch: `ordercli foodora orders --watch`
- Active order detail: `ordercli foodora order <orderCode>`
- History detail JSON: `ordercli foodora history show <orderCode> --json`

Reorder (adds to cart)

- Preview: `ordercli foodora reorder <orderCode>`
- Confirm: `ordercli foodora reorder <orderCode> --confirm`
- Address: `ordercli foodora reorder <orderCode> --confirm --address-id <id>`

Cloudflare / bot protection

- Browser login: `ordercli foodora login --email you@example.com --password-stdin --browser`
- Reuse profile: `--browser-profile "$HOME/Library/Application Support/ordercli/browser-profile"`
- Import Chrome cookies: `ordercli foodora cookies chrome --profile "Default"`

Session import (no password)

- `ordercli foodora session chrome --url https://www.foodora.at/ --profile "Default"`
- `ordercli foodora session refresh --client-id android`

Deliveroo (WIP, not working yet)

- Requires `DELIVEROO_BEARER_TOKEN` (optional `DELIVEROO_COOKIE`).
- `ordercli deliveroo config set --market uk`
- `ordercli deliveroo history`

Notes

- Use `--config /tmp/ordercli.json` for testing.
- Confirm before any reorder or cart-changing action.
