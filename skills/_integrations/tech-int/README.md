# Tech-Int Scanner 🕵️

Technology Intelligence Scanner for Bug Bounty & Security Research.

## Quick Start

```bash
# Install dependencies
pip install requests beautifulsoup4 lxml aiohttp sqlalchemy

# Scan single target
python3 scripts/cli.py scan example.com

# Mass scan
python3 scripts/cli.py scan -f domains.txt --threads 10

# Scan with browser (JS rendering for SPA/React/Vue)
python3 scripts/cli.py scan example.com --browser

# Search results
python3 scripts/cli.py search --cve "2025"

# Update CVE database
python3 scripts/cli.py update-cve
```

## Structure

```
tech-int/
├── scripts/
│   ├── cli.py           # Main CLI entry point
│   └── __init__.py
├── core/
│   ├── scanner.py       # Main scanner orchestrator
│   └── __init__.py
├── detectors/
│   ├── cms/             # CMS detection modules
│   ├── server/          # Web server detection
│   ├── framework/       # Framework detection
│   ├── iot/             # IoT device detection
│   └── js/              # JavaScript library detection
├── db/
│   ├── database.py      # SQLite storage
│   ├── models.py        # Data models
│   └── __init__.py
├── utils/
│   ├── stealth.py       # Stealth client with delays/proxies
│   └── __init__.py
├── cve/
│   ├── cve_db.py        # CVE database management
│   └── __init__.py
├── references/          # Reference data (signatures, patterns)
├── SKILL.md            # This file
└── README.md
```

## Features

- ✅ Technology fingerprinting (CMS, servers, frameworks)
- ✅ Version detection and CVE matching
- ✅ IoT device discovery
- ✅ Stealth mode with random delays and User-Agents
- ✅ Browser mode for JavaScript rendering (SPA, React, Vue)
- ✅ SQLite database for history and queries
- ✅ Mass scanning with threading
- ✅ Export to JSON/CSV

## Database Queries

```bash
# Find WordPress with CVEs
python3 scripts/cli.py search --query "wordpress"

# High CVSS vulnerabilities
python3 scripts/cli.py search --cve "2025" | head -20

# Export results
python3 scripts/cli.py export --format json -o results.json
```

## Stealth Mode

Enable stealth for reconnaissance:
- Random User-Agent rotation
- Configurable request delays
- Proxy support (HTTP/SOCKS5)
- Respect for `robots.txt`

```bash
python3 scripts/cli.py scan example.com --stealth
```

## Browser Mode

Use OpenClaw browser tool for JavaScript rendering (SPA, React, Vue, Angular):
- Renders JavaScript-heavy pages
- Bypass basic bot detection
- Slower but more comprehensive

```bash
python3 scripts/cli.py scan example.com --browser
```

## Integration

Use as library in other tools:

```python
from tech_int import Scanner, Database

db = Database("tech_int.db")
scanner = Scanner(db, threads=5, stealth=True)

result = scanner.scan_single("example.com")
print(result.to_dict())
```

## License

MIT
