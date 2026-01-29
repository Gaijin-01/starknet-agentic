# Research Skill

## Overview
Universal web search skill. Works with any search provider.

## Supported Providers
- brave (default, requires API key)
- serper (Google results via serper.dev)
- duckduckgo (free, no API key)

## Config
Set in `config.yaml`:
```yaml
apis:
  search:
    provider: "brave"
    env_key: "BRAVE_API_KEY"
    rate_limit: 100
```

## Usage
```bash
# Search by topic
python scripts/research.py --query "starknet news"

# Search with topic from config
python scripts/research.py --topic

# Output to file
python scripts/research.py --query "AI agents" --output results.json
```

## Output
Returns list of results:
```json
{
  "query": "starknet news",
  "provider": "brave",
  "timestamp": "2026-01-21T15:00:00",
  "results": [
    {
      "title": "...",
      "url": "...",
      "snippet": "...",
      "published": "..."
    }
  ]
}
```

## Troubleshooting

```bash
# Check config
python scripts/research.py --validate

# Debug mode
python scripts/research.py --query "test" --debug

# Check API keys
echo $BRAVE_API_KEY
```

## Version

- v1.0.0 (2026-01-17): Initial release


```
