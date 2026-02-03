---
name: apple-notes
description: Manage Apple Notes via the `memo` CLI on macOS (create, view, edit, delete, search, move, and export notes). Use when a user asks OpenClaw to add a note, list notes, search notes, or manage note folders.
homepage: https://github.com/antoniorodr/memo
metadata:
  {
    "openclaw":
      {
        "emoji": "📝",
        "os": ["darwin"],
        "requires": { "bins": ["memo"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "antoniorodr/memo/memo",
              "bins": ["memo"],
              "label": "Install memo via Homebrew",
            },
          ],
      },
  }
---

# Apple Notes CLI

## Overview

Manage Apple Notes directly from the terminal using the `memo` CLI. Create, view, edit, delete, search, move notes between folders, and export to HTML/Markdown.

**When to use:**
- Quick note capture from terminal
- Searching notes across all folders
- Organizing notes into folders
- Exporting notes for backup or processing
- Integration with terminal-based workflows

**Key capabilities:**
- List and filter notes by folder
- Fuzzy search across all notes
- Create notes with titles
- Edit existing notes interactively
- Move notes between folders
- Export to HTML/Markdown

## Workflow

```
1. Verify memo CLI is installed
2. Grant Automation access to Notes.app
3. List or search notes as needed
4. Create/edit/move notes as requested
5. Export if backup or conversion needed
```

## Examples

**List all notes:**
```bash
memo notes
```

**Filter by folder:**
```bash
memo notes -f "Work"
```

**Search notes (fuzzy):**
```bash
memo notes -s "meeting"
```

**Add a new note:**
```bash
memo notes -a "Note Title"
```

**Edit existing note:**
```bash
memo notes -e
```

**Move note to folder:**
```bash
memo notes -m
```

**Export to HTML/Markdown:**
```bash
memo notes -ex
```

Setup

- Install (Homebrew): `brew tap antoniorodr/memo && brew install antoniorodr/memo/memo`
- Manual (pip): `pip install .` (after cloning the repo)
- macOS-only; if prompted, grant Automation access to Notes.app.

View Notes

- List all notes: `memo notes`
- Filter by folder: `memo notes -f "Folder Name"`
- Search notes (fuzzy): `memo notes -s "query"`

Create Notes

- Add a new note: `memo notes -a`
  - Opens an interactive editor to compose the note.
- Quick add with title: `memo notes -a "Note Title"`

Edit Notes

- Edit existing note: `memo notes -e`
  - Interactive selection of note to edit.

Delete Notes

- Delete a note: `memo notes -d`
  - Interactive selection of note to delete.

Move Notes

- Move note to folder: `memo notes -m`
  - Interactive selection of note and destination folder.

Export Notes

- Export to HTML/Markdown: `memo notes -ex`
  - Exports selected note; uses Mistune for markdown processing.

Limitations

- Cannot edit notes containing images or attachments.
- Interactive prompts may require terminal access.

Notes

- macOS-only.
- Requires Apple Notes.app to be accessible.
- For automation, grant permissions in System Settings > Privacy & Security > Automation.
