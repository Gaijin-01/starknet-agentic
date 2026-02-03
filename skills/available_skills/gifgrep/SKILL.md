---
name: gifgrep
description: Search GIF providers with CLI/TUI, download results, and extract stills/sheets.
homepage: https://gifgrep.com
metadata:
  {
    "openclaw":
      {
        "emoji": "🧲",
        "requires": { "bins": ["gifgrep"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "steipete/tap/gifgrep",
              "bins": ["gifgrep"],
              "label": "Install gifgrep (brew)",
            },
            {
              "id": "go",
              "kind": "go",
              "module": "github.com/steipete/gifgrep/cmd/gifgrep@latest",
              "bins": ["gifgrep"],
              "label": "Install gifgrep (go)",
            },
          ],
      },
  }
---

# gifgrep

## Overview

<<<<<<< HEAD
GIF-Grab (gifgrep workflow)

- Search → preview → download → extract (still/sheet) for fast review and sharing.
=======
Search GIF providers (Tenor, Giphy) via CLI or TUI, download results, and extract still frames or sprite sheets from GIFs.

**When to use:**
- Finding GIFs for chat/messages
- Extracting frames from GIFs
- Creating sprite sheets for documentation
- Batch GIF operations
- GIF metadata lookup

**Key capabilities:**
- CLI and TUI search interfaces
- Multiple GIF providers
- Still frame extraction
- Sprite sheet generation
- JSON and pipe-friendly output

## Workflow

```
1. Search for GIFs via CLI or TUI
2. Preview results
3. Download or extract frames
4. Use in chat, docs, or projects
```

## Examples

**Quick search:**
```bash
gifgrep cats --max 5
```

**Get URLs only:**
```bash
gifgrep cats --format url | head -n 5
```

**JSON output for scripts:**
```bash
gifgrep search --json cats | jq '.[0].url'
```

**Interactive TUI:**
```bash
gifgrep tui "office handshake"
```

**Download a GIF:**
```bash
gifgrep cats --download --max 1 --format url
```

**Extract still frame:**
```bash
gifgrep still ./clip.gif --at 1.5s -o still.png
```

**Create sprite sheet:**
```bash
gifgrep sheet ./clip.gif --frames 9 --cols 3 -o sheet.png
```

**Use specific provider:**
```bash
gifgrep search --source tenor "funny cat"
```
>>>>>>> de3edc587 (chore: stage changes before v2026.2.1 update)

Quick start

- `gifgrep cats --max 5`
- `gifgrep cats --format url | head -n 5`
- `gifgrep search --json cats | jq '.[0].url'`
- `gifgrep tui "office handshake"`
- `gifgrep cats --download --max 1 --format url`

TUI + previews

- TUI: `gifgrep tui "query"`
- CLI still previews: `--thumbs` (Kitty/Ghostty only; still frame)

Download + reveal

- `--download` saves to `~/Downloads`
- `--reveal` shows the last download in Finder

Stills + sheets

- `gifgrep still ./clip.gif --at 1.5s -o still.png`
- `gifgrep sheet ./clip.gif --frames 9 --cols 3 -o sheet.png`
- Sheets = single PNG grid of sampled frames (great for quick review, docs, PRs, chat).
- Tune: `--frames` (count), `--cols` (grid width), `--padding` (spacing).

Providers

- `--source auto|tenor|giphy`
- `GIPHY_API_KEY` required for `--source giphy`
- `TENOR_API_KEY` optional (Tenor demo key used if unset)

Output

- `--json` prints an array of results (`id`, `title`, `url`, `preview_url`, `tags`, `width`, `height`)
- `--format` for pipe-friendly fields (e.g., `url`)

Environment tweaks

- `GIFGREP_SOFTWARE_ANIM=1` to force software animation
- `GIFGREP_CELL_ASPECT=0.5` to tweak preview geometry
