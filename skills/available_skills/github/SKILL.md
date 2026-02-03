---
name: github
description: "Interact with GitHub using the `gh` CLI. Use `gh issue`, `gh pr`, `gh run`, and `gh api` for issues, PRs, CI runs, and advanced queries."
metadata:
  {
    "openclaw":
      {
        "emoji": "🐙",
        "requires": { "bins": ["gh"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "gh",
              "bins": ["gh"],
              "label": "Install GitHub CLI (brew)",
            },
            {
              "id": "apt",
              "kind": "apt",
              "package": "gh",
              "bins": ["gh"],
              "label": "Install GitHub CLI (apt)",
            },
          ],
      },
  }
---

# GitHub Skill

## Overview

Interact with GitHub using the `gh` CLI. Manage issues, pull requests, workflow runs, and perform advanced queries via the API.

**When to use:**
- Checking PR status and CI results
- Creating and managing issues
- Viewing workflow runs and logs
- Querying GitHub data programmatically
- Repository operations from CLI

**Key capabilities:**
- Pull request checks and reviews
- Issue creation and management
- Workflow run monitoring
- API access for advanced queries
- JSON/JQ output filtering

## Workflow

```
1. Authenticate with GitHub (gh auth login)
2. Navigate to repository or specify --repo
3. Execute gh command for desired operation
4. Parse output (text, JSON, or JQ)
5. Take action based on results
```

## Examples

**Check PR CI status:**
```bash
gh pr checks 55 --repo owner/repo
```

**List recent workflow runs:**
```bash
gh run list --repo owner/repo --limit 10
```

**View run details:**
```bash
gh run view <run-id> --repo owner/repo
```

**View failed step logs:**
```bash
gh run view <run-id> --repo owner/repo --log-failed
```

**List issues:**
```bash
gh issue list --repo owner/repo --json number,title,state
```

**Create an issue:**
```bash
gh issue create --repo owner/repo --title "Bug: X fails" --body "Description"
```

**Advanced API query:**
```bash
gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'
```

**Filter JSON output:**
```bash
gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'
```

## Pull Requests

Check CI status on a PR:

```bash
gh pr checks 55 --repo owner/repo
```

List recent workflow runs:

```bash
gh run list --repo owner/repo --limit 10
```

View a run and see which steps failed:

```bash
gh run view <run-id> --repo owner/repo
```

View logs for failed steps only:

```bash
gh run view <run-id> --repo owner/repo --log-failed
```

## API for Advanced Queries

The `gh api` command is useful for accessing data not available through other subcommands.

Get PR with specific fields:

```bash
gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'
```

## JSON Output

Most commands support `--json` for structured output. You can use `--jq` to filter:

```bash
gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'
```
