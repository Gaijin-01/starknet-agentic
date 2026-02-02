# AVNU Python Client

Python client for AVNU DEX aggregator on Starknet.

## Overview

This skill provides Python bindings for the AVNU SDK, enabling agents to execute gasless token swaps with best price routing on Starknet.

## Features

- Gasless swaps (pay in any token)
- Best price routing across DEXs
- DCA order creation and management
- Native STRK staking integration

## Usage

```python
from avnu_client import AVNUClient

client = AVNUClient(
    rpc_url="https://rpc.starknet.lava.build:443",
    account_address="0x...",
    private_key="0x...",
)

# Get quote
quotes = await client.get_quote(
    sell_token="ETH",
    buy_token="STRK",
    sell_amount=0.01,
)

# Execute swap
result = await client.swap(
    quote=quotes[0],
    slippage=0.01,
)
```

## Scripts

```bash
# Run swap example
python scripts/avnu_client.py --swap --sell ETH --buy STRK --amount 0.01

# Check prices
python scripts/avnu_client.py
```

## Dependencies --prices

- starknet.py
- aiohttp

## License

MIT
