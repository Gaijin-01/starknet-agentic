# AVNU API Documentation

## Overview

AVNU is a DEX aggregator on Starknet that finds the best swap routes across multiple DEXs. It provides REST API and SDK for fetching quotes and executing swaps.

**Base URL:** `https://api.avnu.fi`

**Documentation:** https://docs.avnu.fi

**SDK:** `@avnu/avnu-sdk` (npm)

---

## Authentication

**Optional** - Most endpoints are public. For higher rate limits or sponsored transactions, use an API key.

```http
Header: x-api-key: your-api-key
```

---

## Rate Limits

| Tier | Limit | Requirements |
|------|-------|--------------|
| Public | 300 req/5min | None |
| Integrated | Higher limits | API key required |

---

## APIs

### 1. AVNU API
Used for swaps and token metadata.

**Base URL:** `https://api.avnu.fi`

### 2. Impulse API
Used for market data.

**Base URL:** Not specified in docs

---

## Endpoints

### Swap Endpoints

#### Get Swap Quotes
**Endpoint:** `GET /swap/v1/quotes`

Fetch optimized swap quotes across all Starknet liquidity sources.

**Request Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| sellTokenAddress | string | Yes | Token address to sell (hex format) |
| buyTokenAddress | string | Yes | Token address to buy (hex format) |
| sellAmount | string | No | Amount to sell (hex format) |
| buyAmount | string | No | Exact amount to buy (hex format) |
| takerAddress | string | No | Address executing the swap |
| size | integer | No | Max quotes to return (1-5, default: 1) |
| integratorFees | string | No | Fee in basis points (e.g., "30" for 0.3%) |
| integratorFeeRecipient | string | No | Fee recipient address |
| integratorName | string | No | Integration identifier |
| onlyDirect | boolean | No | Only direct swap routes (no multi-hop) |

**Note:** Either `sellAmount` or `buyAmount` is required.

**Response (200):**
```json
[
  {
    "quoteId": "string",
    "sellTokenAddress": "string",
    "sellAmount": "string",
    "sellAmountInUsd": 0,
    "buyTokenAddress": "string",
    "buyAmount": "string",
    "buyAmountInUsd": 0,
    "fee": {
      "feeToken": "string",
      "avnuFees": "string",
      "avnuFeesInUsd": 0,
      "avnuFeesBps": "string",
      "integratorFees": "string",
      "integratorFeesInUsd": 0,
      "integratorFeesBps": "string"
    },
    "chainId": "string",
    "blockNumber": "string",
    "expiry": 0,
    "routes": [
      {
        "name": "string",
        "address": "string",
        "percent": 0,
        "sellTokenAddress": "string",
        "buyTokenAddress": "string",
        "routes": []
      }
    ],
    "alternativeSwapCount": 0,
    "gasFees": "string",
    "gasFeesInUsd": 0,
    "priceImpact": 0,
    "sellTokenPriceInUsd": 0,
    "buyTokenPriceInUsd": 0,
    "estimatedSlippage": 0
  }
]
```

**Response Fields:**
| Field | Description |
|-------|-------------|
| quoteId | Unique UUID for executing the quote |
| sellAmount/buyAmount | Amounts in hex format (already includes fees) |
| routes | DEX routing paths with allocation percentages |
| gasFees | Estimated gas cost in STRK |
| priceImpact | Basis points (divide by 100 for percentage) |
| expiry | Unix timestamp when quote expires |

---

#### Build Swap Calls
**Endpoint:** `POST /swap/v1/build`

Returns transaction calls needed to execute a swap based on a quote.

**Request Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| quoteId | string | Yes | UUID from /quotes endpoint |
| takerAddress | string | No | Address executing swap |
| slippage | number | Yes | Max slippage (0-1, e.g., 0.01 for 1%) |
| includeApprove | boolean | Yes | Include approve call if needed |

**Example Request:**
```json
{
  "quoteId": "12345678-1234-1234-1234-123456789012",
  "takerAddress": "0x123...",
  "slippage": 0.01,
  "includeApprove": true
}
```

**Response (200):**
```json
{
  "chainId": "string",
  "calls": [
    {
      "contractAddress": "string",
      "entrypoint": "string",
      "calldata": ["string"]
    }
  ]
}
```

---

## SDK Usage

### Installation
```bash
npm install @avnu/avnu-sdk ethers
```

### Get Quotes (JavaScript/TypeScript)
```javascript
import { getQuotes } from '@avnu/avnu-sdk';
import { parseUnits } from 'ethers';

const ethAddress = "0x49d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7";
const strkAddress = "0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d";

const quotes = await getQuotes({
  sellTokenAddress: ethAddress,
  buyTokenAddress: strkAddress,
  sellAmount: parseUnits('0.001', 18),  // 0.001 ETH
  takerAddress: account.address,
  size: 3,  // Get top 3 quotes
});

console.log('Best quote:', quotes[0]);
console.log('Estimated output:', quotes[0].buyAmount);
console.log('Gas fees:', quotes[0].gasFees);
console.log('Route:', quotes[0].routes);
```

### Execute Swap
```javascript
import { executeSwap } from '@avnu/avnu-sdk';

const result = await executeSwap({
  provider: account,
  quote: quotes[0],
  slippage: 0.001,  // 0.1% slippage tolerance
});

console.log('Transaction hash:', result.transactionHash);
```

---

## Common Token Addresses (Starknet Mainnet)

| Token | Address |
|-------|---------|
| ETH | `0x49d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7` |
| STRK | `0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d` |
| USDC | `0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8` |
| USDT | `0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8` |

---

## Usage Examples

### Python (requests)
```python
import requests
import json

def get_quote(sell_token, buy_token, sell_amount, taker_address=None, api_key=None):
    """Fetch swap quotes from AVNU."""
    url = "https://api.avnu.fi/swap/v1/quotes"
    params = {
        "sellTokenAddress": sell_token,
        "buyTokenAddress": buy_token,
        "sellAmount": sell_amount,
        "size": 3,
    }
    if taker_address:
        params["takerAddress"] = taker_address
    
    headers = {}
    if api_key:
        headers["x-api-key"] = api_key
    
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()


def build_swap(quote_id, slippage=0.01, taker_address=None, api_key=None):
    """Build swap transaction calls."""
    url = "https://api.avnu.fi/swap/v1/build"
    payload = {
        "quoteId": quote_id,
        "slippage": slippage,
        "includeApprove": True,
    }
    if taker_address:
        payload["takerAddress"] = taker_address
    
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["x-api-key"] = api_key
    
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


# Example usage
if __name__ == "__main__":
    ETH = "0x49d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"
    STRK = "0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d"
    
    # Get quotes for swapping 0.001 ETH to STRK
    quotes = get_quote(
        sell_token=ETH,
        buy_token=STRK,
        sell_amount="0xDE0B6B3A7640000"  # 0.001 ETH in hex
    )
    
    print(f"Found {len(quotes)} quotes")
    best_quote = quotes[0]
    print(f"Buy amount: {best_quote['buyAmount']}")
    print(f"Price impact: {best_quote['priceImpact']}%")
```

### cURL
```bash
# Get quotes
curl "https://api.avnu.fi/swap/v1/quotes?sellTokenAddress=0x49d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7&buyTokenAddress=0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d&sellAmount=0xDE0B6B3A7640000&size=3"

# Build swap (POST)
curl -X POST "https://api.avnu.fi/swap/v1/build" \
  -H "Content-Type: application/json" \
  -d '{"quoteId":"...","slippage":0.01,"includeApprove":true}'
```

---

## Best Practices

1. **Quote Expiry**
   - Quotes expire quickly (usually within seconds)
   - Build and execute swaps immediately after getting a quote
   - Get a new quote if the transaction takes too long

2. **Slippage Setting**
   - Use 0.5-1% for stable pairs
   - Use 1-2% for volatile pairs
   - Higher slippage increases success rate but may result in worse execution

3. **Gas Estimation**
   - The `gasFees` field shows estimated gas in STRK
   - Factor this into your total swap cost

4. **Error Handling**
   ```python
   try:
       quotes = get_quote(...)
   except requests.exceptions.HTTPError as e:
       if e.response.status_code == 429:
           print("Rate limited - wait and retry")
       else:
           print(f"Error: {e}")
   ```

---

## Supported DEXs

AVNU aggregates liquidity from multiple Starknet DEXs:
- Ekubo
- JediSwap
- 10k
- SithSwap
- Nostra
- And more...

---

## Chain ID

**Starknet Mainnet:** `0x534e5f4d41494e` (hex for "SN_MAIN")

---

## Version

- v1.0.0 (2024)
