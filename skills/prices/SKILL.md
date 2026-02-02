# Prices Skill

## Overview
Universal price fetching skill. Works with crypto (CoinGecko, CoinMarketCap) and traditional finance (Yahoo Finance, Alpha Vantage).

## Supported Providers
- **coingecko** (default for crypto, free tier available)
- **coinmarketcap** (requires API key)
- **yahoo_finance** (stocks, free)
- **alpha_vantage** (stocks, requires API key)

---

## API Integration

### CoinGecko Client

The prices skill uses `coingecko_client.py` for real API integration.

**Module:** `scripts.coingecko_client.CoinGeckoClient`

**API Base URL:** `https://api.coingecko.com/api/v3`

**Documentation:** https://docs.coingecko.com

#### Key Methods

| Method | Description |
|--------|-------------|
| `get_price(token_id)` | Get single token price |
| `get_prices(token_ids)` | Get multiple token prices |
| `get_ohlcv(token_id, days)` | Get OHLCV chart data |
| `get_top_coins(limit)` | Get top coins by market cap |
| `get_starknet_price()` | Get STRK price |
| `get_bitcoin_price()` | Get BTC price |
| `get_ethereum_price()` | Get ETH price |

#### Rate Limits

| Plan | Requests/minute | Notes |
|------|-----------------|-------|
| Free | 10-50 | Limited endpoints |
| Pro | 150-1000+ | Full access |

**Important:** Free tier has strict rate limits. The client uses `rate_limit_delay: 1.5` seconds by default.

#### Configuration

```yaml
apis:
  prices:
    provider: "coingecko"
    env_key: "COINGECKO_API_KEY"  # Optional, for pro plans
```

#### Environment Variables

```bash
export COINGECKO_API_KEY="your-api-key"
```

#### Usage with Python Client

```python
from scripts.coingecko_client import CoinGeckoClient

async def get_crypto_prices():
    async with CoinGeckoClient(
        api_key=None,  # Add key for higher limits
        rate_limit_delay=1.5,
    ) as client:
        # Get single price
        btc = await client.get_bitcoin_price()
        
        # Get multiple prices
        prices = await client.get_prices(
            ["bitcoin", "ethereum", "starknet"],
            include_24h_change=True,
        )
        
        # Get OHLCV data
        ohlcv = await client.get_ohlcv("bitcoin", days="7")
        
        # Get market data
        markets = await client.get_top_coins(limit=10)
```

#### Example Response

```json
{
  "bitcoin": {
    "usd": 65000,
    "usd_24h_change": 2.5,
    "usd_market_cap": 1300000000000
  }
}
```

#### Error Handling

```python
try:
    prices = await client.get_prices(["bitcoin"])
except ValueError as e:
    if "Rate limit" in str(e):
        print("Too many requests. Waiting...")
        await asyncio.sleep(10)
    else:
        print(f"Error: {e}")
```

### PriceService Wrapper

The `prices.py` module provides a `PriceService` wrapper:

```python
from scripts.prices import PriceService

async def get_prices():
    async with PriceService() as service:
        # Get single price
        price = await service.get_price("bitcoin")
        
        # Get multiple prices
        prices = await service.get_prices(["ethereum", "starknet"])
        
        # Get OHLCV data
        ohlcv = await service.get_ohlcv("bitcoin", days="7")
```

---

### Onchain DEX Prices (GeckoTerminal)

For DEX token prices on Starknet and other chains.

**Base URL:** `https://api.coingecko.com/api/v3`

#### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/onchain/simple/networks/{network}/token_price` | GET | Get token price by address |
| `/onchain/networks/{network}/pools` | GET | Get pools on network |
| `/onchain/networks/{network}/trending_pools` | GET | Get trending pools |
| `/onchain/networks/{network}/pools/{address}/ohlcv/{timeframe}` | GET | Get pool OHLCV |

#### Usage

```python
async def get_starknet_token_price(token_address):
    async with CoinGeckoClient() as client:
        prices = await client._request(
            f"/onchain/simple/networks/starknet/token_price",
            params={
                "token_addresses": token_address,
                "vs_currencies": "usd",
            }
        )
        return prices
```

---

### CoinMarketCap API (Optional)

**Base URL:** `https://pro-api.coinmarketcap.com/v2`

**Documentation:** https://coinmarketcap.com/api/documentation

#### Configuration

```yaml
apis:
  prices:
    provider: "coinmarketcap"
    env_key: "COINGECKO_API_KEY"  # Reuse for CMC
    rate_limit: 30
```

#### Rate Limits

| Plan | Requests/month | Requests/minute |
|------|----------------|-----------------|
| Hobbyist | 10,000 | 333 |
| Startup | 50,000 | 500 |
| Business | 200,000+ | Custom |

---

### Yahoo Finance (Stocks/Forex)

**No API key required** - Free tier available.

```python
import yfinance as yf

# Get stock price
stock = yf.Ticker("AAPL")
price = stock.history(period="1d")["Close"][-1]
```

---

### Alpha Vantage (Stocks/Forex/Crypto)

**API Key Required:** https://www.alphavantage.co/support/#api-key

#### Configuration

```yaml
apis:
  prices:
    provider: "alpha_vantage"
    env_key: "ALPHA_VANTAGE_API_KEY"
```

#### Rate Limits

- Free: 5 requests per minute
- Premium: Higher limits available

---

## Config

Set in `config.yaml`:
```yaml
apis:
  prices:
    provider: "coingecko"  # Primary provider
    env_key: null  # Override for pro tiers
    rate_limit: 30  # Soft rate limit

assets:
  crypto:
    - id: "starknet"
      symbol: "STRK"
      display: "strk"
    - id: "ethereum"
      symbol: "ETH"
      display: "eth"
  stocks:
    - symbol: "AAPL"
      display: "Apple"
```

---

## Usage

### Main Entry Point

Run the price service directly:
```bash
cd /home/wner/clawd/skills/prices
python main.py
```

This will fetch real prices and display them in a table.

### CLI Usage

```bash
# Get specific asset price
python scripts/prices.py --asset STRK

# Get all tracked assets
python scripts/prices.py --all

# Format for post
python scripts/prices.py --asset STRK --format post

# Get top N coins
python scripts/prices.py --top 10
```

### Python Usage

```python
from prices.scripts.coingecko_client import CoinGeckoClient

async def get_price_data():
    async with CoinGeckoClient() as client:
        # Get prices with 24h change
        data = await client.get_prices(
            ["bitcoin", "ethereum", "starknet"],
            include_24h_change=True,
        )
        return data
```

### Direct Import

```python
from prices.scripts.coingecko_client import CoinGeckoClient, OHLCVData

async def main():
    client = CoinGeckoClient()
    
    # Simple price
    price = await client.get_price("bitcoin")
    
    # OHLCV for charts
    ohlcv = await client.get_ohlcv("bitcoin", days="30")
    
    await client.close()
```

---

## Output

### JSON Format

```json
{
  "asset": "STRK",
  "price": 0.085,
  "change_24h": -2.5,
  "change_7d": 5.2,
  "timestamp": "2026-01-21T15:00:00"
}
```

### OHLCV Format

```python
# List of OHLCVData objects
[
    OHLCVData(timestamp=1709395200000, open=61942, high=62211, low=61721, close=61845),
    OHLCVData(timestamp=1709409600000, open=61828, high=62139, low=61726, close=62139),
]
```

---

## Troubleshooting

```bash
# Check config
python scripts/prices.py --validate

# Debug mode
python scripts/prices.py --asset STRK --debug

# List tracked assets
python scripts/prices.py --list

# Test API connection
python scripts/prices.py --ping
```

### Common Issues

| Issue | Solution |
|-------|----------|
| 429 Too Many Requests | Increase `rate_limit_delay` to 2-3 seconds |
| Missing prices | Check token ID is correct (e.g., "starknet", not "STRK") |
| Timeout errors | Increase `timeout` in client initialization |
| Stale data | Check `last_updated` field in response |

---

## Environment Variables

```bash
# CoinGecko Pro API Key
export COINGECKO_API_KEY="your-api-key"

# CoinMarketCap API Key  
export CMC_API_KEY="your-api-key"

# Alpha Vantage API Key
export ALPHA_VANTAGE_API_KEY="your-api-key"
```

---

## Best Practices

1. **Rate Limiting**
   - Free CoinGecko: Use 1.5-2 second delays
   - Cache prices for 30-60 seconds
   - Batch requests when possible

2. **Error Handling**
   ```python
   async def safe_price_fetch(client, token_ids):
       try:
           return await client.get_prices(token_ids)
       except ValueError as e:
           if "Rate limit" in str(e):
               await asyncio.sleep(10)
               return await client.get_prices(token_ids)
       except Exception as e:
           print(f"Failed to fetch prices: {e}")
           return {}
   ```

3. **Caching**
   ```python
   from functools import lru_cache
   import asyncio
   
   @lru_cache(maxsize=128)
   async def cached_price(token_id: str) -> dict:
       async with CoinGeckoClient() as client:
           return await client.get_price(token_id)
   ```

---

## Version

- v1.2.0 (2026-02-01): Integrated real CoinGecko client with async support
- v1.1.0 (2026-02-01): Added CoinGecko client with OHLCV support
- v1.0.0 (2026-01-17): Initial release
