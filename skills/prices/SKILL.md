# Prices Skill

## Overview
Universal price fetching skill. Works with crypto (CoinGecko, CoinMarketCap) and traditional finance (Yahoo Finance, Alpha Vantage).

## Supported Providers
- coingecko (default for crypto, free tier)
- coinmarketcap (requires API key)
- yahoo_finance (stocks, free)
- alpha_vantage (stocks, requires API key)

## Config
Set in `config.yaml`:
```yaml
apis:
  prices:
    provider: "coingecko"  # or yahoo_finance
    env_key: null
    rate_limit: 30

assets:
  crypto:
    - id: "starknet"
      symbol: "STRK"
      display: "strk"
  stocks:
    - symbol: "AAPL"
      display: "Apple"
```

## Usage
```bash
# Get specific asset price
python scripts/prices.py --asset STRK

# Get all tracked assets
python scripts/prices.py --all

# Format for post
python scripts/prices.py --asset STRK --format post
```

## Output
```json
{
  "asset": "STRK",
  "price": 0.085,
  "change_24h": -2.5,
  "change_7d": 5.2,
  "timestamp": "2026-01-21T15:00:00"
}
```

## Troubleshooting

```bash
# Check config
python scripts/prices.py --validate

# Debug mode
python scripts/prices.py --asset STRK --debug

# List tracked assets
python scripts/prices.py --list
```

## Version

- v1.0.0 (2026-01-17): Initial release


```
