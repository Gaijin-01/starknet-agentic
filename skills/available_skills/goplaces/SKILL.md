---
name: goplaces
description: Query Google Places API (New) via the goplaces CLI for text search, place details, resolve, and reviews. Use for human-friendly place lookup or JSON output for scripts.
homepage: https://github.com/steipete/goplaces
metadata:
  {
    "openclaw":
      {
        "emoji": "📍",
        "requires": { "bins": ["goplaces"], "env": ["GOOGLE_PLACES_API_KEY"] },
        "primaryEnv": "GOOGLE_PLACES_API_KEY",
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "steipete/tap/goplaces",
              "bins": ["goplaces"],
              "label": "Install goplaces (brew)",
            },
          ],
      },
  }
---

# goplaces

## Overview

Modern Google Places API (New) CLI for place search, details, and reviews. Human-readable output by default, JSON output for scripts.

**When to use:**
- Searching for places (restaurants, cafes, services)
- Getting place details and reviews
- Resolving location text to coordinates
- Building location-aware features
- Finding nearby places with filters

**Key capabilities:**
- Text search with filters (open now, rating, price level)
- Location bias for nearby results
- Pagination support
- Place details with reviews
- Location resolution from text
- JSON output for scripting

## Workflow

```
1. Set GOOGLE_PLACES_API_KEY environment variable
2. Choose search type (text search or resolve)
3. Add filters as needed (open now, rating, location)
4. Execute search with output format
5. Parse results for display or further use
```

## Examples

**Search for open coffee shops nearby:**
```bash
goplaces search "coffee" --open-now --min-rating 4 --limit 5
```

**Search with location bias:**
```bash
goplaces search "pizza" --lat 40.8 --lng -73.9 --radius-m 3000
```

**Get place details with reviews:**
```bash
goplaces details <place_id> --reviews
```

**Resolve location text to coordinates:**
```bash
goplaces resolve "Soho, London" --limit 5
```

**JSON output for scripting:**
```bash
goplaces search "sushi" --json
```

**Paginate through results:**
```bash
goplaces search "pizza" --page-token "NEXT_PAGE_TOKEN"
```

Install

- Homebrew: `brew install steipete/tap/goplaces`

Config

- `GOOGLE_PLACES_API_KEY` required.
- Optional: `GOOGLE_PLACES_BASE_URL` for testing/proxying.

Common commands

- Search: `goplaces search "coffee" --open-now --min-rating 4 --limit 5`
- Bias: `goplaces search "pizza" --lat 40.8 --lng -73.9 --radius-m 3000`
- Pagination: `goplaces search "pizza" --page-token "NEXT_PAGE_TOKEN"`
- Resolve: `goplaces resolve "Soho, London" --limit 5`
- Details: `goplaces details <place_id> --reviews`
- JSON: `goplaces search "sushi" --json`

Notes

- `--no-color` or `NO_COLOR` disables ANSI color.
- Price levels: 0..4 (free → very expensive).
- Type filter sends only the first `--type` value (API accepts one).
