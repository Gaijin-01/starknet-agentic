# CoinGecko API Documentation

## Overview

CoinGecko provides comprehensive cryptocurrency data including prices, market cap, volume, and OHLCV charts.

**Base URL:** `https://api.coingecko.com/api/v3`

**API Key:** Required for higher rate limits (header: `x-cg-pro-api-key`)

**Documentation:** https://docs.coingecko.com

---

## Authentication

```http
Header: x-cg-pro-api-key: YOUR_API_KEY
```

Required for pro endpoints and higher rate limits.

---

## Rate Limits

| Plan | Requests/minute | Notes |
|------|-----------------|-------|
| Free | 10-50 | Limited endpoints |
| Analyst | 150 | Most endpoints |
| Lite | 500 | All endpoints |
| Pro | 1000+ | Full access |

---

## Endpoints

### Simple Endpoints

#### 1. Get Simple Price
**Endpoint:** `GET /simple/price`

Query the prices of one or more coins by their API IDs.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| ids | string | Yes | Coin IDs (comma-separated) |
| vs_currencies | string | Yes | Target currency (e.g., `usd`, `eth`) |
| include_24hr_change | boolean | No | Include 24h change (default: false) |
| include_24hr_vol | boolean | No | Include 24h volume |
| include_market_cap | boolean | No | Include market cap |
| include_last_updated_at | boolean | No | Include timestamp |
| precision | string | No | Decimal places (0-18, or `full`) |

**Response (200):**
```json
{
  "bitcoin": {
    "usd": 65000,
    "usd_24h_change": 2.5,
    "usd_market_cap": 1300000000000,
    "usd_24h_vol": 35000000000,
    "last_updated_at": 1710000000
  },
  "ethereum": {
    "usd": 3500,
    "usd_24h_change": 1.2
  }
}
```

---

#### 2. Get Token Price by Contract Address
**Endpoint:** `GET /simple/token_price/{id}`

Query token prices by contract address on a given platform.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Asset platform (e.g., `ethereum`, `starknet`) |

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| contract_addresses | string | Yes | Token addresses (comma-separated) |
| vs_currencies | string | Yes | Target currency |
| include_24hr_change | boolean | No | Include 24h change |
| include_24hr_vol | boolean | No | Include 24h volume |
| include_market_cap | boolean | No | Include market cap |
| include_last_updated_at | boolean | No | Include timestamp |
| precision | string | No | Decimal places |

**Response (200):**
```json
{
  "0x123...abc": {
    "usd": 1.5,
    "usd_24h_change": -0.5
  }
}
```

---

#### 3. Get Supported VS Currencies
**Endpoint:** `GET /simple/supported_vs_currencies`

Returns all supported fiat and crypto currencies.

**Response (200):**
```json
["usd", "eur", "gbp", "jpy", "btc", "eth", ...]
```

---

### Coins Endpoints

#### 4. List Coins
**Endpoint:** `GET /coins/list`

Returns all supported coins with ID, name, and symbol.

**Response (200):**
```json
[
  {
    "id": "bitcoin",
    "symbol": "btc",
    "name": "Bitcoin"
  },
  {
    "id": "ethereum",
    "symbol": "eth",
    "name": "Ethereum"
  }
]
```

---

#### 5. Get Coins Markets
**Endpoint:** `GET /coins/markets`

Returns market data (price, market cap, volume) for coins.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| vs_currency | string | Yes | Target currency |
| ids | string | No | Coin IDs to filter |
| category | string | No | Category filter |
| order | string | No | Sort field (market_cap_desc, etc.) |
| per_page | integer | No | Results per page (1-250) |
| page | integer | No | Page number |
| sparkline | boolean | No | Include sparkline data |
| price_change_percentage | string | No | 24h,7d,14d,30d,200d,1y |

**Response (200):**
```json
[
  {
    "id": "bitcoin",
    "symbol": "btc",
    "name": "Bitcoin",
    "image": "https://assets.coingecko.com/...",
    "current_price": 65000,
    "market_cap": 1300000000000,
    "market_cap_rank": 1,
    "fully_diluted_valuation": 1470000000000,
    "total_volume": 35000000000,
    "high_24h": 66000,
    "low_24h": 64000,
    "price_change_24h": 1500,
    "price_change_percentage_24h": 2.36,
    "market_cap_change_24h": 50000000000,
    "circulating_supply": 19600000,
    "total_supply": 21000000,
    "max_supply": 21000000,
    "ath": 69000,
    "ath_change_percentage": -5.8,
    "ath_date": "2024-03-14T...",
    "atl": 67.81,
    "atl_change_percentage": 100000,
    "last_updated": "2024-04-07T..."
  }
]
```

---

#### 6. Get Coin Data by ID
**Endpoint:** `GET /coins/{id}`

Returns all metadata for a coin.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Coin API ID (e.g., `bitcoin`) |

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| localization | boolean | No | Include localized descriptions |
| tickers | boolean | No | Include ticker data |
| market_data | boolean | No | Include market data |
| community_data | boolean | No | Include community metrics |
| developer_data | boolean | No | Include developer metrics |
| sparkline | boolean | No | Include sparkline |

**Response (200):** Full coin object with all metadata

---

#### 7. Get Coin OHLC
**Endpoint:** `GET /coins/{id}/ohlc`

Returns OHLCV chart data (candlestick).

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Coin API ID |

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| vs_currency | string | Yes | Target currency |
| days | integer | Yes | Days of data (1, 7, 14, 30, 90, 180, 365, max) |

**Response (200):**
```json
[
  [1709395200000, 61942, 62211, 61721, 61845],
  [1709409600000, 61828, 62139, 61726, 62139],
  [1709424000000, 62171, 62210, 61821, 62068]
]
```

**Format:** `[timestamp, open, high, low, close]`

---

#### 8. Get Coin Market Chart
**Endpoint:** `GET /coins/{id}/market_chart`

Returns historical market data (price, market cap, volume).

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Coin API ID |

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| vs_currency | string | Yes | Target currency |
| days | integer | Yes | Days of data |
| interval | string | No | Daily or hourly |

**Response (200):**
```json
{
  "prices": [
    [1710000000000, 65000.00],
    [1710086400000, 65500.00]
  ],
  "market_caps": [
    [1710000000000, 1300000000000]
  ],
  "total_volumes": [
    [1710000000000, 35000000000]
  ]
}
```

---

#### 9. Get Coin Market Chart (Range)
**Endpoint:** `GET /coins/{id}/market_chart/range`

Returns historical market data within a specific date range.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Coin API ID |

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| vs_currency | string | Yes | Target currency |
| from | integer | Yes | UNIX timestamp (start) |
| to | integer | Yes | UNIX timestamp (end) |

**Response (200):** Same as market_chart

---

#### 10. Get Coin History
**Endpoint:** `GET /coins/{id}/history`

Returns historical data at a specific date.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Coin API ID |

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| date | string | Yes | Date (DD-MM-YYYY) |
| localization | boolean | No | Include localized data |

**Response (200):** Historical coin data

---

### Onchain DEX Endpoints (GeckoTerminal)

#### 11. Get Onchain Token Price
**Endpoint:** `GET /onchain/simple/networks/{network}/token_price`

Get token price by contract address.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| network | string | Yes | Network ID (e.g., `starknet`) |

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| token_addresses | string | Yes | Token addresses (comma-separated) |
| include_24hr_change | boolean | No | Include 24h change |

**Response (200):**
```json
{
  "0x123...abc": {
    "usd": 1.5,
    "usd_24h_change": -0.5
  }
}
```

---

#### 12. Get Network Pools
**Endpoint:** `GET /onchain/networks/{network}/pools`

Get top pools on a network.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| network | string | Yes | Network ID |

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| sort | string | No | Sort field (volume_24h, tvl, etc.) |
| page | integer | No | Page number |
| size | integer | No | Results per page |

**Response (200):** Array of pool objects

---

#### 13. Get Pool OHLCV
**Endpoint:** `GET /onchain/networks/{network}/pools/{pool_address}/ohlcv/{timeframe}`

Get OHLCV chart for a pool.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| network | string | Yes | Network ID |
| pool_address | string | Yes | Pool contract address |
| timeframe | string | Yes | 1h, 1d, 1w, 1m |

**Response (200):** OHLCV array

---

#### 14. Get Trending Pools
**Endpoint:** `GET /onchain/networks/trending_pools`

Get trending pools across all networks.

**Response (200):** Array of trending pool objects

---

### Global Data Endpoints

#### 15. Get Global Data
**Endpoint:** `GET /global`

Returns global cryptocurrency market data.

**Response (200):**
```json
{
  "data": {
    "active_cryptocurrencies": 12000,
    "upcoming_icos": 50,
    "ongoing_icos": 25,
    "ended_icos": 3500,
    "markets": 850,
    "total_market_cap": 2500000000000,
    "total_volume": 100000000000,
    "market_cap_percentage": {
      "btc": 52.0,
      "eth": 17.0
    },
    "market_cap_change_percentage_24h_usd": 2.5
  }
}
```

---

#### 16. Get Exchange Rates
**Endpoint:** `GET /exchange_rates`

Returns BTC exchange rates with other currencies.

**Response (200):**
```json
{
  "rates": {
    "usd": { "name": "US Dollar", "unit": "$", "value": 65000 },
    "eur": { "name": "Euro", "unit": "€", "value": 60000 }
  }
}
```

---

#### 17. Search
**Endpoint:** `GET /search`

Search for coins, categories, and markets.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| query | string | Yes | Search term |

**Response (200):**
```json
{
  "coins": [...],
  "exchanges": [...],
  "categories": [...]
}
```

---

#### 18. Get Trending
**Endpoint:** `GET /search/trending`

Returns trending search data.

**Response (200):** Trending coins, NFTs, categories

---

### Ping

#### 19. Ping Server
**Endpoint:** `GET /ping`

Check API server status.

**Response (200):**
```json
{ "gecko_says": "(3) Everything is awesome!" }
```

---

## Usage Examples

### Python (requests)
```python
import requests

def get_price(coin_id, currency="usd"):
    url = f"https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": coin_id,
        "vs_currencies": currency,
        "include_24hr_change": True
    }
    response = requests.get(url, params=params)
    return response.json()
```

### Python (aiohttp)
```python
import aiohttp

async def get_prices(coin_ids, currency="usd"):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": ",".join(coin_ids),
                "vs_currencies": currency,
                "include_24hr_change": True,
                "include_market_cap": True
            }
        ) as resp:
            return await resp.json()
```

### Get OHLCV Data
```python
import requests

def get_ohlcv(coin_id, days=7, currency="usd"):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc"
    params = {"vs_currency": currency, "days": days}
    response = requests.get(url, params=params)
    return response.json()  # [[timestamp, open, high, low, close], ...]
```

### cURL
```bash
# Get single price
curl "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"

# Get multiple prices with 24h change
curl "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,starknet&vs_currencies=usd&include_24hr_change=true"

# Get OHLCV
curl "https://api.coingecko.com/api/v3/coins/bitcoin/ohlc?vs_currency=usd&days=7"

# Get market data
curl "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10"
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad request (invalid parameters) |
| 401 | Unauthorized (missing API key) |
| 429 | Rate limit exceeded |
| 500 | Internal server error |

---

## Best Practices

1. **Rate Limiting**
   - Use exponential backoff on 429 errors
   - Cache responses when possible
   - Use the API key for higher limits

2. **Caching**
   - Cache price data for 30-60 seconds
   - Cache OHLCV for longer periods
   - Implement request deduplication

3. **Error Handling**
   ```python
   import asyncio
   import aiohttp
   
   async def fetch_with_retry(url, max_retries=3):
       for i in range(max_retries):
           try:
               async with aiohttp.ClientSession() as session:
                   async with session.get(url) as resp:
                       if resp.status == 429:
                           await asyncio.sleep(2 ** i)
                           continue
                       return await resp.json()
           except Exception as e:
               await asyncio.sleep(2 ** i)
       raise Exception(f"Failed after {max_retries} retries")
   ```

---

## Starknet-Specific Notes

For Starknet tokens, use the `onchain` endpoints with `network=starknet`:

```python
# Get STRK price
GET /onchain/simple/networks/starknet/token_price?token_addresses=0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d&vs_currencies=usd
```

---

## Version

- v3.0.0 (2024)
- API Version: `v3`
