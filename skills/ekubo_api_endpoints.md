# Ekubo Protocol API Documentation

## Overview

Ekubo Protocol is an AMM (Automated Market Maker) infrastructure on Starknet featuring super-concentrated liquidity. The API provides REST endpoints for querying protocol data.

**Base URL:** `https://prod-api.ekubo.org`

**OpenAPI Specification:** `/openapi.json`

**Contact:** eng@ekubo.org

**Documentation:** https://docs.ekubo.org

---

## Authentication

No authentication required for public endpoints.

---

## Endpoints

### Meta Endpoints

#### 1. List Tokens
**Endpoint:** `GET /tokens`

Returns a list of tokens for the given chain ID.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| chainId | integer | No | The ID of the network (Starknet mainnet: 1) |
| search | string | No | Token symbol search |
| pageSize | integer | No | Number of tokens to return (default: 1000, max: 10000) |
| afterToken | string | No | Pagination cursor (format: `chainId:tokenAddress`) |
| minVisibilityPriority | integer | No | Filter by visibility priority (-100 to 100) |

**Response (200):**
```json
[
  {
    "chain_id": "string",
    "name": "string",
    "symbol": "string",
    "decimals": 0,
    "address": "string",
    "visibility_priority": 0,
    "sort_order": 0,
    "total_supply": 0,
    "logo_url": "string",
    "usd_price": 0,
    "bridgeInfos": {}
  }
]
```

---

#### 2. Batch Get Tokens
**Endpoint:** `GET /tokens/batch`

Fetch metadata for a specific set of tokens.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string[] | Yes | Token identifiers (format: `chainId:tokenAddress`) |

**Response (200):** Same as /tokens endpoint.

---

#### 3. Get Token by Address
**Endpoint:** `GET /tokens/{chainId}/{tokenAddress}`

Returns metadata for a specific token on the given chain.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| chainId | integer | Yes | Network ID |
| tokenAddress | string | Yes | Token address (hex or decimal) |

**Response (200):** Token metadata object

**Response (404):**
```json
{
  "status": 404,
  "error": "Token not found"
}
```

---

#### 4. Get Closest Block
**Endpoint:** `GET /blocks/{chainId}/closest`

Returns the block whose timestamp is nearest to the provided timestamp.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| chainId | integer | Yes | Network ID |

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| timestamp | string | Yes | ISO 8601 timestamp (e.g., `2025-11-10T00:00:00Z`) |

**Response (200):**
```json
{
  "number": 0,
  "timestamp": "string"
}
```

---

#### 5. Get Block
**Endpoint:** `GET /blocks/{chainId}/{blockTag}`

Get information about a particular block.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| chainId | integer | Yes | Network ID |
| blockTag | integer or "latest" | Yes | Block number or "latest" |

**Response (200):**
```json
{
  "number": 0,
  "timestamp": "string"
}
```

---

### Stats Endpoints

#### 6. Get Overview Pairs
**Endpoint:** `GET /overview/pairs`

Returns stats for the top trading pairs.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| chainId | integer | No | Network ID |
| minTvlUsd | number | No | Minimum USD TVL required (default: 1000) |

**Response (200):**
```json
{
  "topPairs": [
    {
      "chain_id": "string",
      "token0": {},
      "token1": {},
      "volume0_24h": "string",
      "volume1_24h": "string",
      "fees0_24h": "string",
      "fees1_24h": "string",
      "tvl0_total": "string",
      "tvl1_total": "string",
      "tvl0_delta_24h": "string",
      "tvl1_delta_24h": "string",
      "depth0": "string",
      "depth1": "string",
      "min_depth_percent": 0
    }
  ]
}
```

---

#### 7. Get Revenue Stats
**Endpoint:** `GET /overview/revenue`

Returns the revenue stats for the protocol.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| chainId | integer | No | Network ID |

**Response (200):**
```json
{
  "revenueByTokenByDate": [
    {
      "token": "string",
      "revenue": "string",
      "chain_id": "string",
      "date": "string"
    }
  ],
  "revenueByToken_24h": [
    {
      "token": "string",
      "revenue": "string",
      "chain_id": "string"
    }
  ]
}
```

---

#### 8. Get TVL Stats
**Endpoint:** `GET /overview/tvl`

Returns the Total Value Locked stats.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| chainId | integer | No | Network ID |

**Response (200):**
```json
{
  "tvlByToken": [
    {
      "token": "string",
      "balance": "string",
      "chain_id": "string"
    }
  ],
  "tvlDeltaByTokenByDate": [
    {
      "token": "string",
      "date": "string",
      "delta": "string",
      "chain_id": "string"
    }
  ]
}
```

---

#### 9. Get Volume Stats
**Endpoint:** `GET /overview/volume`

Returns the trading volume stats.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| chainId | integer | No | Network ID |

**Response (200):**
```json
{
  "volumeByTokenByDate": [
    {
      "token": "string",
      "volume": "string",
      "fees": "string",
      "chain_id": "string",
      "date": "string"
    }
  ],
  "volumeByToken_24h": [
    {
      "token": "string",
      "volume": "string",
      "fees": "string",
      "chain_id": "string"
    }
  ]
}
```

---

#### 10. Get Pair TVL
**Endpoint:** `GET /pair/{chainId}/{tokenA}/{tokenB}/tvl`

Returns TVL stats for a specific trading pair.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| chainId | integer | Yes | Network ID |
| tokenA | string | Yes | First token address |
| tokenB | string | Yes | Second token address |

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| tickSpacing | integer | No | Pool tick spacing |
| fee | string | No | Pool fee (hex or decimal) |
| extension | string | No | Extension address |
| coreAddress | string | No | Core contract address |
| amplification | integer | No | Stableswap amplification |
| centerTick | integer | No | Stableswap center tick |

**Response (200):** Pair TVL object

---

#### 11. Get Pair Volume
**Endpoint:** `GET /pair/{chainId}/{tokenA}/{tokenB}/volume`

Returns volume stats for a specific trading pair.

**Path Parameters:** Same as above

**Query Parameters:** Same as above

**Response (200):** Pair volume object

---

## Rate Limits

Not explicitly documented. Use reasonable request intervals.

---

## Error Responses

All endpoints return standard HTTP error codes:
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

---

## Usage Examples

### Python (aiohttp)
```python
import aiohttp

async def get_tokens():
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://prod-api.ekubo.org/tokens",
            params={"chainId": 1, "pageSize": 100}
        ) as resp:
            return await resp.json()
```

### cURL
```bash
# Get tokens list
curl "https://prod-api.ekubo.org/tokens?chainId=1&pageSize=100"

# Get specific token
curl "https://prod-api.ekubo.org/tokens/1/0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"

# Get overview pairs
curl "https://prod-api.ekubo.org/overview/pairs?chainId=1"
```

---

## Starknet Chain ID

- **Mainnet:** `1`
- **Testnet:** Not explicitly documented

---

## Notes

- All token amounts are in raw units (not decimals-adjusted)
- USD prices are provided where available
- The API uses OpenAPI 3.1 specification
- Responses are in JSON format
