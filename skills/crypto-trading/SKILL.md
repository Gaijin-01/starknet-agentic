---
name: crypto-trading
description: On-chain metrics, whale tracking, and arbitrage detection for crypto trading using DEX APIs and blockchain explorers.
homepage: https://github.com
metadata: {"clawdbot":{"emoji":"🐋","requires":{"python":["httpx"]},"install":[{"id":"pip","kind":"pip","package":"httpx","bins":["python3 scripts/main.py"],"label":"Install deps (pip)"}]}}
---

# crypto-trading

## Overview

On-chain analytics and trading intelligence skill. Provides real-time data on token metrics, whale activity, and cross-DEX arbitrage opportunities.

**Key Capabilities:**
- **On-chain Metrics:** TVL, volume, fees, price, market cap for tokens/pools
- **Whale Tracking:** Monitor large transactions, track wallets, sentiment analysis
- **Arbitrage Detection:** Find price discrepancies across DEXs

**Data Sources:**
- DexScreener API (prices, volume, liquidity)
- Etherscan/BscScan (transactions, wallet activity)
- DEX APIs (Uniswap, SushiSwap, PancakeSwap, etc.)

## Requirements

- Python 3.10+
- httpx for async HTTP
- Optional: Etherscan/BscScan API keys for higher rate limits

### Environment Variables

```bash
# Optional API keys for higher rate limits
export ETHERSCAN_API_KEY="your_etherscan_key"
export BSCSCAN_API_KEY="your_bscscan_key"

# Default data directory
export CRYPTO_DATA_DIR="/home/wner/clawd/skills/crypto-trading/data"
```

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                  Crypto Trading Workflow                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Market Overview                                          │
│     - Get top pools by TVL/Volume                            │
│     - Track trending tokens                                  │
│     - Monitor chain TVL totals                               │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Token Analysis                                           │
│     - Fetch token metrics (price, TVL, volume)               │
│     - Compare across DEXs                                    │
│     - Track holder count and transactions                    │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Whale Monitoring                                         │
│     - Track large transactions                               │
│     - Monitor specific wallets                               │
│     - Analyze flow patterns                                  │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Arbitrage Detection                                      │
│     - Compare prices across DEXs                             │
│     - Calculate spread after fees                            │
│     - Estimate profit potential                              │
└─────────────────────────────────────────────────────────────┘
```

## Installation

```bash
# Clone skill
cd ~/clawd/skills/crypto-trading

# Install dependencies
pip install httpx

# Configure (optional)
export ETHERSCAN_API_KEY="your_key"

# Test setup
python3 scripts/main.py metrics --overview
```

## Usage

### CLI Commands

```bash
# Market overview
python3 scripts/main.py metrics --overview
python3 scripts/main.py metrics --overview --chains ethereum bsc arbitrum

# Token metrics
python3 scripts/main.py metrics --token 0x1234... --chain ethereum
python3 scripts/main.py metrics --search uniswap --limit 5

# Pool rankings
python3 scripts/main.py metrics --pools --chain ethereum --limit 10
python3 scripts/main.py metrics --trending --chain ethereum --limit 5

# Whale tracking
python3 scripts/main.py whale --transactions --chain ethereum --min-value 100000
python3 scripts/main.py whale --wallet 0xabcd... --chain ethereum
python3 scripts/main.py whale --add 0xabcd... --label "Smart Money" --tags institution
python3 scripts/main.py whale --list
python3 scripts/main.py whale --update --chains ethereum bsc

# Arbitrage detection
python3 scripts/main.py arbitrage --find --threshold 1.0
python3 scripts/main.py arbitrage --analyze ETH/USDT --quote USDT
python3 scripts/main.py arbitrage --find --threshold 0.5 --gas 30
```

### Python API

```python
from scripts.metrics import OnChainMetrics, SyncOnChainMetrics
from scripts.whale import WhaleTracker, SyncWhaleTracker
from scripts.arbitrage import ArbitrageDetector, SyncArbitrageDetector

# On-chain metrics
metrics = SyncOnChainMetrics()

# Get token metrics
token = metrics.get_token_metrics(
    token_address="0x1234...",
    chain="ethereum"
)
print(f"Price: ${token.price}")
print(f"TVL: ${token.tvl}")
print(f"24h Volume: ${token.volume_24h}")

# Search tokens
results = metrics.search_tokens("bitcoin", limit=5)

# Top pools
pools = metrics.get_top_pools(chain="ethereum", limit=10)

# Market overview
overview = metrics.get_market_overview(
    chains=["ethereum", "bsc", "arbitrum"]
)
print(f"Total TVL: ${overview['total_tvl']}")

# Whale tracking
tracker = SyncWhaleTracker()

# Add tracked wallet
tracker.add_tracked_wallet(
    address="0xabcd...",
    label="Smart Money",
    tags=["institution", "whale"]
)

# Get large transactions
txs = tracker.get_large_transactions(
    chain="ethereum",
    min_value_usd=500000
)

# Analyze flow
analysis = tracker.analyze_flow(txs)
print(f"Total volume: ${analysis['total_value_usd']}")
print(f"Net flow: ${analysis['net_flow']}")

# Get sentiment
sentiment = tracker.get_whale_sentiment(txs)
print(f"Sentiment: {sentiment['sentiment']}")

# Arbitrage detection
detector = SyncArbitrageDetector(
    gas_price_gwei=20.0,
    profit_threshold_percent=1.0
)

# Find opportunities
opps = detector.find_opportunities(
    min_spread_percent=0.5,
    max_results=10
)
for opp in opps[:5]:
    print(f"{opp.token_pair}: {opp.profit_percent:.2f}% profit")
    print(f"  Buy: {opp.buy_exchange} @ ${opp.buy_price}")
    print(f"  Sell: {opp.sell_exchange} @ ${opp.sell_price}")

# Analyze specific pair
analysis = detector.analyze_pair("ETH", "USDT")
print(f"Best buy: {analysis['best_buy']}")
print(f"Best sell: {analysis['best_sell']}")
print(f"Recommendation: {analysis['recommendation']}")
```

## Examples

### Daily Crypto Digest

```bash
#!/bin/bash
# crypto_digest.sh
cd ~/clawd/skills/crypto-trading

echo "=== Market Overview ==="
python3 scripts/main.py metrics --overview --chains ethereum bsc arbitrum --limit 5

echo ""
echo "=== Top Trending ==="
python3 scripts/main.py metrics --trending --limit 10

echo ""
echo "=== Whale Activity ==="
python3 scripts/main.py whale --transactions --chain ethereum --min-value 500000 --limit 10

echo ""
echo "=== Arbitrage Opportunities ==="
python3 scripts/main.py arbitrage --find --threshold 1.0 --limit 5
```

### Watch for Whale Buys

```python
from scripts.whale import SyncWhaleTracker

tracker = SyncWhaleTracker()

# Add known whale wallets
whales = [
    "0x1234...",
    "0xabcd...",
]

for whale in whales:
    tracker.add_tracked_wallet(whale, tags=["whale"])

# Get transactions
txs = tracker.get_wallet_transactions(whales[0], chain="ethereum")

# Filter for buys (inflows)
buys = [tx for tx in txs if tx.value_usd > 100000]
print(f"Found {len(buys)} large buys")

for buy in buys[:5]:
    print(f"{buy.token_symbol}: ${buy.value_usd:,.0f}")
```

### Track New Token Launches

```python
from scripts.metrics import SyncOnChainMetrics

metrics = SyncOnChainMetrics()

# Check for new pools
new_pools = metrics.get_new_pools(chain="ethereum", limit=10)

print("=== New Pools ===")
for pool in new_pools:
    print(f"{pool.token0_symbol}/{pool.token1_symbol}")
    print(f"  TVL: ${pool.tvl:,.0f}")
    print(f"  Volume: ${pool.volume_24h:,.0f}")
    print(f"  APR: {pool.apr:.1f}%")
```

### Automated Alerting

```python
from scripts.arbitrage import SyncArbitrageDetector
from scripts.whale import SyncWhaleTracker
import asyncio

async def check_opportunities():
    detector = SyncArbitrageDetector(profit_threshold_percent=1.5)
    
    opportunities = detector.find_opportunities(max_results=20)
    
    # Filter for high-quality opportunities
    good_opps = [
        o for o in opportunities
        if o.profit_percent > 2.0 and o.execution_risk == "low"
    ]
    
    if good_opps:
        print("🚨 Arbitrage Alert!")
        for opp in good_opps[:3]:
            print(f"  {opp.token_pair}: {opp.profit_percent:.2f}%")
            print(f"    {opp.buy_exchange} → {opp.sell_exchange}")
    
    detector.close()

# Run periodically
asyncio.run(check_opportunities())
```

### Portfolio Monitoring

```python
from scripts.metrics import SyncOnChainMetrics

PORTFOLIO = {
    "ETH": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
    "USDC": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
    "UNI": "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
}

metrics = SyncOnChainMetrics()

print("=== Portfolio Values ===")
total = 0

for symbol, address in PORTFOLIO.items():
    token = metrics.get_token_metrics(address, "ethereum")
    if token:
        print(f"{symbol}: ${token.price:.2f}")
        print(f"  24h Change: {token.price_change_24h:+.2f}%")
        print(f"  TVL: ${token.tvl:,.0f}")
        total += token.price  # Assuming 1 token for demo

print(f"\nTotal tracked tokens: {len(PORTFOLIO)}")
```

## File Structure

```
crypto-trading/
├── __init__.py
├── scripts/
│   ├── main.py          # CLI entry point
│   ├── metrics.py       # On-chain metrics (async)
│   ├── whale.py         # Whale tracking (async)
│   └── arbitrage.py     # Arbitrage detection
├── data/
│   ├── tracked_wallets.json  # Tracked wallet storage
│   └── price_cache.json      # Price cache
└── SKILL.md
```

## Configuration

### Whale Thresholds

| Chain | Min USD Value |
|-------|---------------|
| Ethereum | $100,000 |
| BSC | $50,000 |
| Arbitrum | $100,000 |
| Base | $50,000 |
| Polygon | $25,000 |

### Arbitrage Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Gas price | 20 Gwei | Network gas price |
| Profit threshold | 1.0% | Minimum spread to report |
| Min liquidity | $10,000 | Minimum pool liquidity |
| Slippage | 1.0% | Estimated slippage |

### Rate Limits

- DexScreener: 10 requests/second
- Etherscan: 5 requests/second (free tier)
- BscScan: 5 requests/second (free tier)

## Troubleshooting

### No Data Returned

```bash
# Check API connectivity
curl -s https://api.dexscreener.com/latest/dex/pairs | head -c 500

# Verify chain name
python3 scripts/main.py metrics --trending --chain ethereum
```

### Rate Limit Errors

```bash
# Add API keys for higher limits
export ETHERSCAN_API_KEY="your_key"

# Reduce request frequency
# Wait between requests
```

### Whale Tracking Empty

```bash
# Increase min_value threshold
python3 scripts/main.py whale --transactions --min-value 50000

# Check different chain
python3 scripts/main.py whale --transactions --chain bsc
```

### Arbitrage Not Found

```bash
# Lower threshold
python3 scripts/main.py arbitrage --find --threshold 0.5

# Check specific pair
python3 scripts/main.py arbitrage --analyze ETH/USDT
```

## Integration

### With Trading Bots

```python
from scripts.arbitrage import SyncArbitrageDetector

detector = SyncArbitrageDetector(profit_threshold_percent=1.0)

while True:
    opportunities = detector.find_opportunities(max_results=5)
    
    for opp in opportunities:
        if opp.profit_percent > 2.0 and opp.execution_risk == "low":
            # Execute trade
            execute_arbitrage(opp)
    
    sleep(60)  # Check every minute
```

### With Price Alerts

```python
from scripts.metrics import SyncOnChainMetrics

metrics = SyncOnChainMetrics()

TARGET_TOKENS = {
    "0x1234...": {"target_price": 1.50, "direction": "below"},
}

for address, config in TARGET_TOKENS.items():
    token = metrics.get_token_metrics(address)
    
    if config["direction"] == "below" and token.price <= config["target_price"]:
        print(f"🚨 {token.symbol} below ${config['target_price']}!")
        # Send alert
```

## Version

- v1.0.0 (2025-01-17): Initial release with on-chain metrics, whale tracking, and arbitrage detection
