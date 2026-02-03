---
name: starknet-whale-tracker
description: |
  Starknet Whale Intelligence System — real-time monitoring of smart money, mempool, and arbitrage opportunities. Track whale wallets, detect large movements, and signal trading opportunities in the Starknet ecosystem.
---

# Starknet Whale Tracker

Real-time intelligence system for tracking whale wallets, mempool transactions, and arbitrage opportunities in the Starknet ecosystem.

## Overview

A comprehensive tool for monitoring smart money movements on Starknet. Designed for traders, protocols, and researchers who need to stay ahead of large transactions and market-moving events.

**When to use:**
- Tracking known whale wallets for alpha
- Monitoring mempool for large pending transactions
- Detecting arbitrage opportunities between DEXs
- Building copy-trading signals
- Protocol analytics and market surveillance

## Features

### 🐋 Whale Wallet Tracking
- Database of known smart money wallets
- Real-time balance and position tracking
- Historical movement analysis
- Alert on significant changes

### 📡 Mempool Monitoring
- Pending transaction monitoring
- Large transfer detection
- MEV opportunity identification
- Sandwich attack detection

### 💰 Arbitrage Detection
- Cross-DEX price monitoring
- Triangular arbitrage signals
- Flash loan opportunity detection
- Profit estimation

### 📊 Analytics Dashboard
- Wallet portfolio analysis
- Transaction history
- Profit/loss tracking
- Custom alerts and webhooks

## Architecture

```
starknet-whale-tracker/
├── starknet_rpc.py       # RPC + indexing layer
├── whale_db.py           # Known wallets database
├── mempool_monitor.py    # Pending transaction watcher
├── arbitrage.py          # Opportunity detection
├── signals.py            # Alert engine
├── api.py                # REST API + webhooks
├── cli.py                # Command-line interface
├── config.py             # Configuration
└── SKILL.md              # This file
```

## Workflow

1. **Initialize**
   - Configure RPC endpoints
   - Set up whale wallet database
   - Configure alert destinations

2. **Monitor**
   - Watch for new blocks
   - Track pending transactions
   - Analyze price differences across DEXs

3. **Detect**
   - Identify whale movements
   - Flag large transactions
   - Calculate arbitrage opportunities

4. **Alert**
   - Send notifications (Telegram, webhook)
   - Log to database
   - Trigger automated actions

## Quick Start

### Installation
```bash
cd /home/wner/clawd/skills/starknet-whale-tracker
pip install starknet.py aiohttp python-telegram-bot
```

### CLI Usage
```bash
# Start monitoring
python cli.py start --mode all

# Track specific wallet
python cli.py track --address 0x123...

# Check arbitrage opportunities
python cli.py arbitrage --dex jediswap --dex ekubo

# Get whale activity summary
python cli.py summary --hours 24
```

### API Server
```bash
python api.py --host 0.0.0.0 --port 8080
```

### Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /whales | List tracked wallets |
| POST | /whales | Add new wallet |
| GET | /activity | Recent whale activity |
| GET | /arbitrage | Current opportunities |
| POST | /webhook | Receive alerts |

## Configuration

### config.yaml
```yaml
starknet:
  rpc_url: https://starknet-mainnet.g.alchemy.com/v2/YOUR_KEY
  indexer_url: https://api.starknet.io/v1

whales:
  default_tags:
    - deployer
    - large_holder
    - protocol_treasury
  alert_threshold: 1000  # STRK

mempool:
  enabled: true
  min_value_strk: 100
  max_block_wait: 5

arbitrage:
  enabled: true
  min_profit_percent: 0.5
  dexes:
    - jediswap
    - ekubo
    -10k

alerts:
  telegram:
    enabled: true
    bot_token: YOUR_BOT_TOKEN
    chat_id: YOUR_CHAT_ID
  webhook:
    enabled: false
    url: https://your-webhook.com/alerts
```

## Whale Database

### Adding Whales
```python
from whale_db import WhaleDatabase

db = WhaleDatabase()

# Add individual wallet
db.add_wallet(
    address="0x123...",
    tags=["deployer", "large_holder"],
    notes="Starknet Foundation"
)

# Import from file
db.import_from_csv("whales.csv")
```

### Querying Whales
```python
# Get all tagged wallets
whales = db.get_by_tag("large_holder")

# Get recent activity
activity = db.get_activity(address="0x123...", hours=24)

# Get portfolio summary
portfolio = db.get_portfolio("0x123...")
```

## Mempool Monitoring

### Real-time Tracking
```python
from mempool_monitor import MempoolMonitor

monitor = MempoolMonitor(
    rpc_url=RPC_URL,
    min_value=1000,  # STRK
    alert_callback=send_alert
)

await monitor.start()
```

### Detected Events
| Event | Description |
|-------|-------------|
| large_transfer | Single transfer > threshold |
| contract_deployment | New contract deployment |
| dex_trade | Trade on tracked DEX |
| flash_loan | Flash loan execution |

## Arbitrage Detection

### Finding Opportunities
```python
from arbitrage import ArbitrageScanner

scanner = ArbitrageScanner(
    min_profit=0.5,  # percent
    dexes=["jediswap", "ekubo"]
)

opportunities = await scanner.scan()

for op in opportunities:
    print(f"Profit: {op.profit_usd}")
    print(f"Path: {op.path}")
```

### Arbitrage Types
- **Direct**: A → B (same token)
- **Triangular**: A → B → C → A
- **Triangular Cross**: A → B → C (different amounts)

## Signal System

### Creating Alerts
```python
from signals import SignalEngine

signals = SignalEngine()

# Define custom signal
@signals.on("large_transfer")
async def handle_transfer(event):
    await notify_telegram(f"🐋 {event.address}: {event.value} STRK")

signals.start()
```

### Alert Types
| Type | Trigger |
|------|---------|
| whale_move | Balance change > 10% |
| large_deposit | Deposit > 10k STRK |
| new_position | New token > 1% portfolio |
| arbitrage | Profit > threshold |

## Starknet Integration

### RPC Methods Used
- `starknet_call` - Read contract state
- `starknet_getStorageAt` - Get storage values
- `starknet_getBlockWithTxs` - Block data
- `starknet_getTransactions` - Transaction history

### Indexer Integration
- Starknet Indexer API for historical data
- Event filtering for specific contracts
- Token transfer tracking

### Libraries
- `starknet.py` - Python SDK for Starknet
- `starknet-rs` - Rust SDK (optional)
- `cairo-lang` - Contract interaction

## API Reference

### Python SDK

```python
from tracker import StarknetWhaleTracker

tracker = StarknetWhaleTracker(
    rpc_url=RPC_URL,
    db_path="./whales.db"
)

# Track a wallet
await tracker.track_wallet(
    address="0x...",
    tags=["whale"],
    alert_on=["large_transfer", "new_position"]
)

# Get activity
activity = await tracker.get_activity(
    address="0x...",
    since="24h"
)

# Stream events
async for event in tracker.stream():
    print(event)
```

### REST API

```bash
# Get tracked whales
curl https://localhost:8080/whales

# Add new whale
curl -X POST https://localhost:8080/whales \
  -H "Content-Type: application/json" \
  -d '{"address": "0x...", "tags": ["whale"]}'

# Get opportunities
curl https://localhost:8080/arbitrage

# Webhook for alerts
curl -X POST https://localhost:8080/webhook \
  -d '{"event": "whale_move", "data": {...}}'
```

## Monetization

### Free Tier
- 5 tracked wallets
- Daily summary
- Public API access

### Premium Tier ($50-100/mo)
- Unlimited wallets
- Real-time alerts
- API access
- Custom strategies

### Enterprise
- Dedicated infrastructure
- Custom integrations
- SLA guarantee
- 24/7 support

## Use Cases

### Trading Signals
```
User: "Alert when whales buy $BROTHER"
System: Monitors whale wallets → Sends Telegram alert
Result: Early signal for potential moves
```

### Protocol Analytics
```
User: "Track all large transfers to treasury"
System: Filters mempool → Generates daily report
Result: Market intelligence for research
```

### Copy Trading
```
User: "Copy trades from wallet 0x123..."
System: Monitors wallet → Executes via smart contract
Result: Automated copy-trading bot
```

## Deployment

### Docker
```dockerfile
FROM python:3.11

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

CMD ["python", "api.py"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  tracker:
    build: .
    ports:
      - "8080:8080"
    environment:
      - RPC_URL=${RPC_URL}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_TOKEN}
    volumes:
      - ./data:/app/data
```

### Cron Integration
```bash
# Hourly summary
0 * * * * python cli.py summary --hours 1 --telegram

# Daily report
0 9 * * * python cli.py report --telegram
```

## Best Practices

1. **RPC Management**
   - Use multiple RPC endpoints for redundancy
   - Rate limit requests appropriately
   - Cache frequently accessed data

2. **Database**
   - Regular backups of whale database
   - Index frequently queried fields
   - Archive old activity data

3. **Alert Handling**
   - Deduplicate similar alerts
   - Rate limit notifications
   - Test alert delivery

4. **Security**
   - Secure API keys and tokens
   - Limit webhook access
   - Audit whale database changes

## Troubleshooting

| Issue | Solution |
|-------|----------|
| RPC rate limits | Add more endpoints, reduce polling |
| Missing alerts | Check webhook delivery, spam folder |
| High memory usage | Archive old data, optimize queries |
| Slow queries | Add database indexes |

## Examples

### Complete Tracking Session
```python
import asyncio
from tracker import StarknetWhaleTracker

async def main():
    tracker = StarknetWhaleTracker(
        rpc_url="https://starknet-mainnet.g.alchemy.com/v2/...",
        telegram_token="..."
    )
    
    # Add known whale
    await tracker.add_whale(
        address="0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004d7",
        tags=["foundation", "large_holder"],
        alert_on=["large_transfer", "new_position"]
    )
    
    # Start monitoring
    await tracker.start()
    
    # Stream events
    async for event in tracker.stream():
        print(f"{event.type}: {event.data}")

asyncio.run(main())
```

### Arbitrage Scanner
```python
from arbitrage import ArbitrageScanner

async def find_opportunities():
    scanner = ArbitrageScanner(
        min_profit_percent=1.0,
        dexes=["jediswap", "ekubo", "10k"]
    )
    
    opportunities = await scanner.full_scan()
    
    for op in opportunities[:5]:
        print(f"Profit: ${op.profit_usd}")
        print(f"Path: {' → '.join(op.path)}")
        print(f"Confidence: {op.confidence}%")
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit pull request

## Real Integrations

### Ekubo API Client

The tracker uses the `ekubo_client.py` module for real-time pool data and prices.

**Module:** `scripts.ekubo_client.EkuboClient`

**API Base URL:** `https://prod-api.ekubo.org`

**Key Endpoints:**
| Method | Description |
|--------|-------------|
| `get_tokens()` | List all tokens on Starknet |
| `get_token(chain_id, address)` | Get specific token metadata |
| `get_overview_pairs()` | Get top trading pairs by TVL |
| `get_tvl_stats()` | Get TVL statistics |
| `get_volume_stats()` | Get volume statistics |
| `get_prices(tokens)` | Get USD prices for tokens |

**Client Usage:**
```python
from scripts.ekubo_client import EkuboClient

async def get_ekubo_data():
    async with EkuboClient() as client:
        # Get top pairs
        pairs = await client.get_overview_pairs()
        
        # Get specific token price
        price = await client.get_price(token_address)
        
        # Get liquidity depth
        depth = await client.get_liquidity_depth(token_a, token_b)
```

**Configuration:**
```bash
# Environment variable (optional)
EKUBO_API_KEY=your-api-key
```

**Starknet Chain ID:** `1` (mainnet)

### Arbitrage Tracker

The `arbitrage_tracker.py` module provides arbitrage detection using real Ekubo data:

```python
from scripts.arbitrage_tracker import ArbitrageTracker

async def find_opportunities():
    async with ArbitrageTracker(min_profit_percent=0.5) as tracker:
        opportunities = await tracker.get_arbitrage_opportunities()
        return opportunities
```

**Features:**
- Real-time price comparison across DEXs
- Liquidity depth filtering
- Profit estimation
- Confidence scoring

---

### CoinGecko Price Feeds

For cross-referencing and additional market data, use the prices skill's `coingecko_client.py`:

**Module:** `prices.scripts.coingecko_client.CoinGeckoClient`

**API Base URL:** `https://api.coingecko.com/api/v3`

**Key Methods:**
| Method | Description |
|--------|-------------|
| `get_prices(ids)` | Get token prices |
| `get_ohlcv(id, days)` | Get OHLCV chart data |
| `get_top_coins(limit)` | Get top coins by market cap |

**Client Usage:**
```python
from prices.scripts.coingecko_client import CoinGeckoClient

async def get_market_prices():
    async with CoinGeckoClient() as client:
        # Get multiple prices
        prices = await client.get_prices(
            ["bitcoin", "ethereum", "starknet"],
            currency="usd",
            include_24h_change=True
        )
        
        # Get OHLCV for analysis
        ohlcv = await client.get_ohlcv("bitcoin", days="7")
```

---

### AVNU Swap API (Optional)

For executing swaps and getting best routes.

**API Base URL:** `https://api.avnu.fi`

**Key Endpoints:**
| Endpoint | Description |
|----------|-------------|
| `GET /swap/v1/quotes` | Get swap quotes |
| `POST /swap/v1/build` | Build swap transaction calls |

**Rate Limits:**
- Public: 300 requests per 5 minutes
- Integrated: Higher limits with API key

---

## Configuration

### Environment Variables

```bash
# Ekubo (optional, currently public)
EKUBO_API_KEY=

# CoinGecko (optional, for higher rate limits)
COINGECKO_API_KEY=

# AVNU (optional)
AVNU_API_KEY=
```

### config.yaml Integration

```yaml
apis:
  ekubo:
    enabled: true
    base_url: "https://prod-api.ekubo.org"
    chain_id: 1  # Starknet mainnet
  
  coingecko:
    enabled: true
    base_url: "https://api.coingecko.com/api/v3"
    api_key: ${COINGECKO_API_KEY}
    rate_limit_delay: 1.5  # seconds between requests
  
  avnu:
    enabled: false  # Set true for swap execution
    base_url: "https://api.avnu.fi"
    api_key: ${AVNU_API_KEY}
```

---

## Usage Examples

### Complete Price Monitoring Setup
```python
import asyncio
from scripts.ekubo_client import EkuboClient
from prices.scripts.coingecko_client import CoinGeckoClient

async def monitor_prices():
    async with EkuboClient() as ekubo, CoinGeckoClient() as cg:
        # Get Ekubo pool data
        pairs = await ekubo.get_overview_pairs()
        
        # Cross-reference with CoinGecko
        prices = await cg.get_prices(
            ["starknet", "ethereum"],
            include_24h_change=True
        )
        
        # Detect price discrepancies
        for pair in pairs:
            print(f"Pair: {pair.token0}/{pair.token1}")
            print(f"Depth: {pair.depth0}")

asyncio.run(monitor_prices())
```

### Whale Activity with Price Context
```python
async def get_whale_activity_with_prices():
    async with EkuboClient() as ekubo:
        # Get current prices for context
        strk_price = await ekubo.get_strk_price()
        eth_price = await ekubo.get_eth_price()
        
        print(f"STRK: ${strk_price}")
        print(f"ETH: ${eth_price}")
        
        # Get top pools for whale movement context
        pairs = await ekubo.get_overview_pairs()
        return pairs
```

---

## Rate Limit Handling

All clients implement automatic rate limiting:

```python
class EkuboClient:
    # Default: No explicit rate limiting (public API)
    # Monitor response headers for 429 errors

class CoinGeckoClient:
    # Default: 1.5 second delay between requests
    # Automatic retry on 429 with exponential backoff

class AVNUClient:
    # Default: 300 req/5min for public
    # Use API key for higher limits
```

---

## License

MIT License - See LICENSE file for details.

---

**Version:** 1.1.0  
**Last Updated:** 2026-02-01  
**Author:** Clawd / Sefirot
