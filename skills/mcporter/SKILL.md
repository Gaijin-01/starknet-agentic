---
name: mcporter
description: Use the mcporter CLI to list, configure, auth, and call MCP servers/tools directly (HTTP or stdio), including ad-hoc servers, config edits, and CLI/type generation.
homepage: http://mcporter.dev
metadata: {"clawdbot":{"emoji":"📦","requires":{"bins":["mcporter"]},"install":[{"id":"node","kind":"node","package":"mcporter","bins":["mcporter"],"label":"Install mcporter (node)"}]}}
---

# mcporter

## Overview

Use `mcporter` to work with MCP (Model Context Protocol) servers directly. This skill enables seamless integration with MCP tools, allowing you to list available servers, configure authentication, call tools programmatically, and generate client code.

**Key Capabilities:**
- List and discover MCP servers
- Call server tools with various argument formats
- Configure server authentication (OAuth)
- Generate CLI wrappers and TypeScript types
- Daemon mode for persistent server connections
- Support for HTTP and stdio transport modes

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    Mcporter Workflow                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Server Discovery                                        │
│     - mcporter list                                         │
│     - mcporter list <server> --schema                       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Authentication Setup (if needed)                        │
│     - mcporter auth <server | url> [--reset]                │
│     - mcporter config import|login|logout                   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Tool Invocation                                         │
│     ┌─────────────────────────────────────────────────────┐ │
│     │ mcporter call <server.tool> [args]                  │ │
│     │ - Selector syntax: tool=value                       │ │
│     │ - Function syntax: "func(arg: \"value\")"            │ │
│     │ - JSON payload: --args '{"key": "value"}'           │ │
│     └─────────────────────────────────────────────────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Code Generation (optional)                              │
│     - mcporter generate-cli --server <name>                 │
│     - mcporter emit-ts <server> --mode client|types         │
└─────────────────────────────────────────────────────────────┘
```

## Quick start
- `mcporter list`
- `mcporter list <server> --schema`
- `mcporter call <server.tool> key=value`

Call tools
- Selector: `mcporter call linear.list_issues team=ENG limit:5`
- Function syntax: `mcporter call "linear.create_issue(title: \"Bug\")"`
- Full URL: `mcporter call https://api.example.com/mcp.fetch url:https://example.com`
- Stdio: `mcporter call --stdio "bun run ./server.ts" scrape url=https://example.com`
- JSON payload: `mcporter call <server.tool> --args '{"limit":5}'`

Auth + config
- OAuth: `mcporter auth <server | url> [--reset]`
- Config: `mcporter config list|get|add|remove|import|login|logout`

Daemon
- `mcporter daemon start|status|stop|restart`

Codegen
- CLI: `mcporter generate-cli --server <name>` or `--command <url>`
- Inspect: `mcporter inspect-cli <path> [--json]`
- TS: `mcporter emit-ts <server> --mode client|types`

Notes
- Config default: `./config/mcporter.json` (override with `--config`).
- Prefer `--output json` for machine-readable results.

## Examples

### Server Discovery
```bash
# List all configured servers
mcporter list

# List server tools with schemas
mcporter list linear --schema

# List with JSON output for parsing
mcporter list --output json
```

### Basic Tool Calls
```bash
# Simple selector syntax (key=value)
mcporter call linear.list_issues team=ENG limit:5

# Function-call syntax with escaping
mcporter call "linear.create_issue(title: \"Bug found in login\")"

# Multiple arguments
mcporter call github.create_repo name=myrepo private=true description="Test"
```

### Advanced Tool Calls
```bash
# HTTP server call with full URL
mcporter call https://api.example.com/mcp.fetch url:https://example.com

# Stdio-based ad-hoc server
mcporter call --stdio "bun run ./scrape-server.ts" url=https://news.ycombinator.com

# JSON payload for complex arguments
mcporter call github.create_issue \
  --args '{"owner": "owner", "repo": "repo", "title": "Bug", "body": "Description"}' \
  --output json
```

### Authentication Management
```bash
# Authenticate to a server
mcporter auth linear

# Reset authentication
mcporter auth linear --reset

# Authenticate with custom URL
mcporter auth https://api.example.com/mcp

# List config
mcporter config list

# Import config from file
mcporter config import ./config.json
```

### Daemon Mode
```bash
# Start daemon for persistent connections
mcporter daemon start

# Check daemon status
mcporter daemon status

# Restart daemon
mcporter daemon restart

# Stop daemon
mcporter daemon stop
```

### Code Generation
```bash
# Generate CLI wrapper for a server
mcporter generate-cli --server linear
mcporter generate-cli --command https://api.example.com/mcp

# Inspect generated CLI
mcporter inspect-cli ./linear-cli --json

# Generate TypeScript types
mcporter emit-ts linear --mode types

# Generate full client
mcporter emit-ts linear --mode client
```

### Integration with Scripts
```bash
#!/bin/bash
# Create GitHub issue from script
mcporter call github.create_issue \
  --args "{\"owner\":\"$OWNER\",\"repo\":\"$REPO\",\"title\":\"$TITLE\",\"body\":\"$BODY\"}" \
  --output json | jq -r '.issue.number'

#!/bin/bash
# Fetch and process data
mcporter call https://api.example.com/mcp.analyze \
  url:https://example.com \
  --output json | jq '.result.sentiment'
```

### Workflow Examples
```bash
# Linear integration workflow
# 1. List issues
ISSUES=$(mcporter call linear.list_issues filter=active --output json)

# 2. Create new issue
mcporter call "linear.create_issue(title: \"Fix $BUG\", description: \"$DESC\")"

# 3. Add comment
mcporter call linear.add_comment issueId=$ISSUE_ID body="Fixed in commit $COMMIT"

# Cross-server workflow
# 1. Fetch data via HTTP MCP
DATA=$(mcporter call https://api.example.com/mcp.fetch url:https://example.com --output json)

# 2. Process with local stdio server
mcporter call --stdio "node processor.js" data="$DATA" --output json

# 3. Create ticket in Linear
mcporter call linear.create_issue title="Automated import" description="$DATA"
```

## Troubleshooting

### Server Not Found
```bash
# Check server is configured
mcporter config list

# Add server config
mcporter config add --name myserver --url https://mcp.example.com

# Verify server is running
curl https://mcp.example.com/health
```

### Authentication Failed
```bash
# Reset auth and re-authenticate
mcporter auth myserver --reset
mcporter auth myserver

# Check token validity
mcporter call myserver.whoami

# Check config file permissions
ls -la ./config/mcporter.json
```

### Tool Call Failed
```bash
# Check tool schema
mcporter list myserver --schema | grep tool_name

# Verify arguments
mcporter call myserver.tool --args '{}' --verbose

# Try simple call first
mcporter call myserver.simple_tool param=value
```

### Stdio Server Issues
```bash
# Check server script exists
cat ./server.ts | head -5

# Test server directly
bun run ./server.ts --help

# Increase timeout for slow servers
mcporter call --stdio "python server.py" slow_task=True --timeout 60
```

### JSON Output Issues
```bash
# Ensure --output json is specified
mcporter call linear.list_issues --output json

# Check for parse errors
mcporter call linear.list_issues --output json 2>&1 | jq .

# Validate JSON manually
mcporter call linear.list_issues > output.json
cat output.json | jq .
```
