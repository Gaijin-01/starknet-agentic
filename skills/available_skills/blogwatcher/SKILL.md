---
name: blogwatcher
description: Monitor blogs and RSS/Atom feeds for updates using the blogwatcher CLI.
homepage: https://github.com/Hyaxia/blogwatcher
metadata:
  {
    "openclaw":
      {
        "emoji": "📰",
        "requires": { "bins": ["blogwatcher"] },
        "install":
          [
            {
              "id": "go",
              "kind": "go",
              "module": "github.com/Hyaxia/blogwatcher/cmd/blogwatcher@latest",
              "bins": ["blogwatcher"],
              "label": "Install blogwatcher (go)",
            },
          ],
      },
  }
---

# blogwatcher

## Overview

Track blog and RSS/Atom feed updates with the `blogwatcher` CLI. Monitor multiple sources for new content and track read/unread status.

**When to use:**
- Monitoring blogs for new posts
- Tracking RSS/Atom feed updates
- Keeping up with multiple content sources
- Finding new articles across subscriptions
- Managing reading lists

**Key capabilities:**
- Add and remove blog sources
- Scan for new articles
- Track read/unread status
- Multi-feed monitoring
- Export article lists

## Workflow

```
1. Add blog/RSS feed to watchlist
2. Periodically scan for updates
3. Review new articles
4. Mark articles as read
5. Remove feeds when no longer needed
```

## Examples

**Install blogwatcher:**
```bash
go install github.com/Hyaxia/blogwatcher/cmd/blogwatcher@latest
```

**Add a blog to watchlist:**
```bash
blogwatcher add "My Blog" https://example.com/feed
```

**List tracked blogs:**
```bash
blogwatcher blogs
```

**Scan for updates:**
```bash
blogwatcher scan
```

**List all articles:**
```bash
blogwatcher articles
```

**Mark article as read:**
```bash
blogwatcher read 1
```

**Mark all articles as read:**
```bash
blogwatcher read-all
```

**Remove a blog:**
```bash
blogwatcher remove "My Blog"
```

Install

- Go: `go install github.com/Hyaxia/blogwatcher/cmd/blogwatcher@latest`

Quick start

- `blogwatcher --help`

Common commands

- Add a blog: `blogwatcher add "My Blog" https://example.com`
- List blogs: `blogwatcher blogs`
- Scan for updates: `blogwatcher scan`
- List articles: `blogwatcher articles`
- Mark an article read: `blogwatcher read 1`
- Mark all articles read: `blogwatcher read-all`
- Remove a blog: `blogwatcher remove "My Blog"`

Example output

```
$ blogwatcher blogs
Tracked blogs (1):

  xkcd
    URL: https://xkcd.com
```

```
$ blogwatcher scan
Scanning 1 blog(s)...

  xkcd
    Source: RSS | Found: 4 | New: 4

Found 4 new article(s) total!
```

Notes

- Use `blogwatcher <command> --help` to discover flags and options.
