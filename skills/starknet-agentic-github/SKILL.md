---
name: starknet-agentic-github
description: >
  Work with the Gaijin-01/starknet-agentic fork on GitHub. 
  Manage issues, PRs, CI runs, code review, and agent contributions.
  Use for: checking PR status or CI, creating/commenting on issues, 
  listing/filtering PRs or issues, viewing run logs, managing skills,
  and coordinating multi-agent work on this repository.
keywords:
  - starknet
  - starknet-agentic
  - github
  - cairo
  - smart-contracts
  - agent
  - openclaw
allowed-tools:
  - gh
  - read
  - exec
user-invocable: true
---

# Starknet Agentic GitHub Skill

Working with the **Gaijin-01/starknet-agentic** fork (Sefi's fork of keep-starknet-strange/starknet-agentic).

## Repository Context

This is a monorepo for AI agents on Starknet with:
- Cairo smart contracts (ERC-8004, Agent Account, Huginn Registry)
- TypeScript packages (MCP server, A2A adapter, wallet tools)
- Skills marketplace for agent capabilities
- Examples (DeFi agent, onboarding, cross-chain)

**Default branch:** `main`  
**Upstream:** `keep-starknet-strange/starknet-agentic`

## Common Operations

### Issues
```bash
# List issues
gh issue list --repo Gaijin-01/starknet-agentic

# Create issue
gh issue create --repo Gaijin-01/starknet-agentic --title "feat: ..." --body "..."

# Comment on issue
gh issue comment <issue-number> --repo Gaijin-01/starknet-agentic --body "..."
```

### Pull Requests
```bash
# List PRs
gh pr list --repo Gaijin-01/starknet-agentic

# Check PR status
gh pr view <pr-number> --repo Gaijin-01/starknet-agentic

# View PR checks
gh pr checks <pr-number> --repo Gaijin-01/starknet-agentic

# Create PR
gh pr create --repo Gaijin-01/starknet-agentic --title "..." --body "..." --base main
```

### CI/CD
```bash
# List workflow runs
gh run list --repo Gaijin-01/starknet-agentic

# View run logs
gh run view <run-id> --repo Gaijin-01/starknet-agentic --log

# Rerun failed job
gh run rerun <run-id> --repo Gaijin-01/starknet-agentic --failed
```

### Syncing with Upstream
```bash
# Add upstream if not exists
git remote add upstream https://github.com/keep-starknet-strange/starknet-agentic.git

# Fetch upstream
git fetch upstream

# Merge upstream main
git merge upstream/main

# Or rebase
git rebase upstream/main
```

## Agent Identity

When contributing to this repo, agents should:
1. Use conventional commits (`feat:`, `fix:`, `docs:`, etc.)
2. Link issues in PRs
3. Include acceptance tests
4. Follow AGENT.md roles when coordinating multi-agent work

## Key Files Reference

| File | Purpose |
|------|---------|
| `AGENT.md` | Agent mission & ecosystem context |
| `agents.md` | Multi-agent coordination & roles |
| `CLAUDE.md` | Development context & conventions |
| `skills/manifest.json` | Skills marketplace index |
| `docs/ROADMAP.md` | Project roadmap |
| `docs/GOOD_FIRST_ISSUES.md` | Starter tasks for contributors |

## Cairo Contract Workflow

For contract changes:
```bash
cd contracts/erc8004-cairo && scarb build && snforge test
cd contracts/agent-account && scarb build && snforge test
```

## TypeScript Workflow

```bash
pnpm install
pnpm build
pnpm test
```
