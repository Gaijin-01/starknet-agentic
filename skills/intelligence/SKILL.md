# intelligence

Unified intelligence gathering skill. Merges research, prices, crypto-trading, and ct-intelligence.

## Overview

**Merged Skills:**
- `research` → web search and news
- `prices` → crypto prices from CoinGecko
- `crypto-trading` → onchain metrics and whale tracking
- `ct-intelligence` → Crypto Twitter competitor tracking

## Architecture

```
intelligence/
├── main.py           # Unified entry point
├── search.py         # Web research (Brave/Serper/DuckDuckGo)
├── prices.py         # Crypto price data (CoinGecko)
├── onchain.py        # Onchain metrics (DEX, whales)
├── ct.py             # CT tracking (trends, sentiment)
├── config.yaml       # Configuration
└── data/             # Cache and storage
```

## Usage

```bash
# Research
python3 main.py search "Starknet ecosystem news"

# Prices
python3 main.py prices --tokens btc,eth,strk
python3 main.py prices --trend 24h

# Onchain
python3 main.py onchain whales --token eth
python3 main.py onchain arbitrage --token sol

# CT Intelligence
python3 main.py ct trends --hours 24
python3 main.py ct sentiment "Bitcoin halving"
python3 main.py ct track --add @VitalikButerin

# All-in-one report
python3 main.py report "Starknet"
```

## API

```python
from intelligence import Intelligence

intel = Intelligence()

# Search
results = intel.search("crypto news")

# Prices
prices = intel.prices(["btc", "eth", "strk"])

# Onchain
whales = intel.onchain_whales("eth")

# CT
trends = intel.ct_trends(hours=24)
sentiment = intel.ct_sentiment("DeFi summer")
```

## Configuration

`config.yaml`:
```yaml
search:
  provider: "brave"
  api_key_env: "BRAVE_API_KEY"

prices:
  provider: "coingecko"
  cache_minutes: 5

onchain:
  providers: ["dexscreener", "birdeye"]
  whale_threshold: 100000  # $100K+ transactions

ct:
  tracked_accounts:
    - "@VitalikButerin"
    - "@CryptoHayes"
  sentiment_keywords:
    bullish: ["moon", "lfg", "bullish", "up only"]
    bearish: ["dump", "rugged", "scam", "bearish"]
```

## Sub-modules

### search.py
Web search using Brave/Serper/DuckDuckGo.

### prices.py  
Crypto prices from CoinGecko API with caching.

### onchain.py
Onchain data: DEX volumes, whale transactions, arbitrage opportunities.

### ct.py
Crypto Twitter tracking: trends, sentiment, account monitoring.

## Migration

This skill was consolidated from:
- skills/research (v1.0.0)
- skills/prices (v1.0.0)
- skills/crypto-trading (v1.0.0)
- skills/ct-intelligence (v1.0.0)

Old skills kept as aliases for backward compatibility.
