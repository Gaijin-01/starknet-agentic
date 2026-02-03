---
name: nano-pdf
description: Edit PDFs with natural-language instructions using the nano-pdf CLI.
homepage: https://pypi.org/project/nano-pdf/
metadata:
  {
    "openclaw":
      {
        "emoji": "📄",
        "requires": { "bins": ["nano-pdf"] },
        "install":
          [
            {
              "id": "uv",
              "kind": "uv",
              "package": "nano-pdf",
              "bins": ["nano-pdf"],
              "label": "Install nano-pdf (uv)",
            },
          ],
      },
  }
---

# nano-pdf

## Overview

Edit PDFs using natural language instructions. The CLI parses your instruction and applies changes to a specific page without needing to know PDF internals or specialized editing tools.

**When to use:**
- Fixing typos in PDFs
- Updating titles or headings on specific pages
- Changing numbers or dates in forms/documents
- Simple text replacements without full PDF editing software
- Quick edits when you don't have the original source document

**Key capabilities:**
- Natural language instruction parsing
- Page-specific edits (0-based indexing)
- No external dependencies or PDF libraries needed
- Original formatting preserved where possible

## Workflow

```
1. Identify the PDF and the specific page needing edits
2. Note the page number (check if 0-based or 1-based)
3. Formulate a clear, specific instruction
4. Run nano-pdf edit command
5. Verify the output PDF
6. If off by one, retry with adjusted page number
```

## Examples

**Change a title on page 1:**
```bash
nano-pdf edit report.pdf 1 "Change the title to 'Q3 Financial Results'"
```

**Fix a typo in the subtitle:**
```bash
nano-pdf edit presentation.pptx.pdf 3 "Fix the typo 'teh' to 'the' in the subtitle"
```

**Update a date on a form:**
```bash
nano-pdf edit form.pdf 0 "Change the date from '2024-01-01' to '2024-12-31'"
```

**Update a version number:**
```bash
nano-pdf edit document.pdf 0 "Update version from 'v1.0' to 'v2.0' in the header"
```

## Quick start

```bash
nano-pdf edit deck.pdf 1 "Change the title to 'Q3 Results' and fix the typo in the subtitle"
```

Notes:

- Page numbers are 0-based or 1-based depending on the tool’s version/config; if the result looks off by one, retry with the other.
- Always sanity-check the output PDF before sending it out.
