---
name: gemini
description: Gemini CLI for one-shot Q&A, summaries, and generation.
homepage: https://ai.google.dev/
metadata:
  {
    "openclaw":
      {
        "emoji": "♊️",
        "requires": { "bins": ["gemini"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "gemini-cli",
              "bins": ["gemini"],
              "label": "Install Gemini CLI (brew)",
            },
          ],
      },
  }
---

# Gemini CLI

## Overview

Google's Gemini AI model via CLI for one-shot queries, summaries, and content generation. Runs in non-interactive mode for automation-friendly usage without sustained conversations.

**When to use:**
- Quick Q&A without API setup
- Summarizing text or documents
- Generating content from prompts
- Code explanation or generation
- Translation tasks
- Simple AI tasks where Claude isn't available

**Key capabilities:**
- One-shot queries (positional prompt)
- Multiple model selection
- JSON output for structured responses
- Extension management
- No persistent conversation state

## Workflow

```
1. Formulate clear, specific prompt
2. Choose appropriate model (or use default)
3. Run gemini with prompt
4. Parse output (text or JSON)
5. Iterate with refined prompts if needed
```

## Examples

**Basic question:**
```bash
gemini "What is the capital of Australia?"
```

**With specific model:**
```bash
gemini --model gemini-1.5-pro "Explain quantum computing in simple terms"
```

**JSON output for structured data:**
```bash
gemini --output-format json "List 5 programming languages with their paradigms"
```

**Summarize text from file:**
```bash
gemini "Summarize this document: $(cat report.txt)"
```

**Generate a list:**
```bash
gemini "Generate 10 ideas for a productivity app"
```

## Notes

Use Gemini in one-shot mode with a positional prompt (avoid interactive mode).

Quick start

- `gemini "Answer this question..."`
- `gemini --model <name> "Prompt..."`
- `gemini --output-format json "Return JSON"`

Extensions

- List: `gemini --list-extensions`
- Manage: `gemini extensions <command>`

Notes

- If auth is required, run `gemini` once interactively and follow the login flow.
- Avoid `--yolo` for safety.
