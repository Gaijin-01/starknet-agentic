---
name: tech-int
description: Technology Intelligence Scanner — automated reconnaissance for bug bounty and security research. Discovers tech stack, versions, CVE matches, and IoT devices.
homepage: https://github.com/your-repo/tech-int
metadata:
  openclaw:
    emoji: "🕵️"
    requires:
      bins: ["python3", "curl", "nmap"]
      python: ["requests", "beautifulsoup4", "lxml", "aiohttp", "sqlalchemy"]
    install:
      - kind: pip
        packages: ["requests", "beautifulsoup4", "lxml", "aiohttp", "sqlalchemy", "celery", "redis"]
        label: "Install dependencies"
---

# Tech-Int Scanner 🕵️

Automated Technology Intelligence for Bug Bounty & Security Research.

## Overview

Tech-Int performs passive and active reconnaissance:
- Technology stack fingerprinting (CMS, frameworks, servers)
- Version detection and CVE matching
- IoT device discovery (cameras, routers, NAS)
- Local SQLite database for history and queries

## Architecture

```
tech-int/
├── cli.py           # Main entry point
├── core/            # Task orchestration
├── detectors/       # Technology-specific modules
│   ├── cms/         # WordPress, Drupal, Joomla, etc.
│   ├── server/      # Nginx, Apache, Caddy, etc.
│   ├── framework/   # React, Vue, Django, Flask, etc.
│   ├── iot/         # Cameras, routers, IoT
│   └── js/          # JavaScript libraries
├── db/              # SQLite storage
├── utils/           # Stealth client, proxies, delays
└── cve/             # CVE database sync
```

## Usage

```bash
# Single target scan
tech-int scan example.com

# Mass scan from list
tech-int scan list.txt --threads 10

# Search database
tech-int search "nginx <1.20"
tech-int search --cve "2025" --cvss ">8.0"

# Update CVE database
tech-int update-cve

# Export results
tech-int export --format json --output results.json
```

## Detection Modules

| Module | Detects |
|--------|---------|
| `cms` | WordPress, Drupal, Joomla, Typo3, etc. |
| `server` | Nginx, Apache, IIS, Caddy, OpenResty |
| `framework` | React, Vue, Angular, Django, Flask, etc. |
| `iot` | Hikvision, Axis, Ubiquiti, MikroTik, QNAP |
| `js` | jQuery, Bootstrap, React, Vue, etc. |

## Stealth Features

- Random User-Agent rotation
- Request delays (configurable)
- Proxy support (HTTP/SOCKS5)
- Respect for `robots.txt`

## Database Queries

```sql
-- Find all WordPress with CVEs
SELECT domain, version, cve_id, cvss FROM targets
WHERE cms = 'wordpress' AND cve_id IS NOT NULL;

-- High CVSS vulnerabilities
SELECT * FROM targets WHERE cvss > 8.0 ORDER BY cvss DESC;

-- IoT devices exposed
SELECT * FROM targets WHERE iot_device IS NOT NULL;
```

## Integration

Can be used as library:
```python
from tech_int import Scanner, Database

db = Database("tech_int.db")
scanner = Scanner(db)

for target in scanner.scan("example.com"):
    print(target.to_dict())
```

## Requirements

- Python 3.10+
- 512MB RAM minimum
- SQLite3

## References

- [NVD Database](https://nvd.nist.gov/)
- [Wappalyzer](https://www.wappalyzer.com/)
- [BuiltWith](https://builtwith.com/)
