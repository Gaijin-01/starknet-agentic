---
name: starknet-py
description: |
  Python SDK for Starknet. Provides access to Starknet network, smart contract interaction, and account management.
---

# Starknet.py Skill

Python SDK for Starknet blockchain interaction.

## Overview

The `starknet-py` skill provides a Python interface to interact with the Starknet blockchain. It wraps the official `starknet-py` SDK with a CLI interface for common operations like checking balances, account info, and contract interactions.

**Chain Info:**
- **Mainnet Chain ID:** `0x534e5f4d41494c` (SN_MAINNET)
- **Default RPC:** Lava.build (`https://rpc.starknet.lava.build:443`)
- **Python Version:** 3.12+

## Workflow

```
1. Connect → FullNodeClient connects to RPC endpoint
2. Query → Use client to fetch blocks, transactions, balances
3. Account → Load or create Account with KeyPair
4. Interact → Call/invoke contract functions
5. Deploy → Deploy new contracts to network
```

## Installation

```bash
pip install starknet-py --break-system-packages
```

## RPC Endpoints

| Network | URL |
|---------|-----|
| Mainnet | `https://rpc.starknet.lava.build:443` |
| Sepolia | `https://starknet-sepolia.public.blastapi.io/rpc/v0_6` |

## Quick Start

```python
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.account.account import Account
from starknet_py.contract import Contract
from starknet_py.net.signer.key_pair import KeyPair

# Connect to Starknet node
node_url = "https://rpc.starknet.lava.build:443"
client = FullNodeClient(node_url=node_url)

# Load account
key_pair = KeyPair.from_private_key("0x...")
account = Account(
    address="0x...",
    client=client,
    key_pair=key_pair
)

# Deploy contract
contract = Contract.from_abi("name", abi, address)
```

## Key Features

- **FullNodeClient** - Connect to any Starknet RPC endpoint
- **Account** - Account abstraction with key management
- **Contract** - Deploy and interact with contracts
- **KeyPair** - SECP256K1 key management
- **Data retrieval** - Blocks, transactions, events

## CLI Usage

```bash
# Check ETH balance (uses Lava.build RPC)
python3.12 scripts/cli.py balance 0x053c91253bc9682c04929ca02ed00b3e423f6714d2ea42d73d1b8f3f8d400005

# Check USDC balance
python3.12 scripts/cli.py balance-usdc 0x053c91253bc9682c04929ca02ed00b3e423f6714d2ea42d73d1b8f3f8d400005

# Account info
python3.12 scripts/cli.py account-info 0x053c91253bc9682c04929ca02ed00b3e423f6714d2ea42d73d1b8f3f8d400005

# Custom RPC
python3.12 scripts/cli.py --rpc https://rpc.starknet.lava.build:443 balance 0x...
```
