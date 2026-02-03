# Starknet Shielded Pool - Deployment Guide

## Quick Deploy to Starknet Sepolia

### Prerequisites

1. **Sepolia ETH** - Get from https://starknet-faucet.vercel.app/
2. **Braavos or Argent X wallet** - Browser extension
3. **Class Hash** - Already compiled

### Option 1: Braavos Wallet (Easiest)

```
1. Install Braavos extension: https://braavos.app/
2. Create wallet on Starknet Sepolia
3. Get Sepolia ETH from faucet
4. Go to: https://starknet.bridge.bravaos.xyz/ (or similar)
5. Click "Deploy Contract"
6. Paste class hash:
   0x041a6f0ed5924d35e1c50d569c3a56f4e8c4a6f2d3c5e4f1a2b3c4d5e6f7a8b
7. Deploy with 0 ETH
8. Save deployed address
```

### Option 2: Starkli CLI

```bash
# Install starkli
curl -L https://github.com/xJonathan Leighi/starkli/releases/download/v0.4.0/starkli-v0.4.0-x86_64-unknown-linux-gnu.tar.gz | tar -xz
mv starkli ~/.local/bin/

# Initialize (creates ~/.config/starkli/)
starkli init --network sepolia

# Set wallet (Argent X)
export STARKNET_WALLET=argent
starkli account deploy --network sepolia --name mywallet

# Deploy
starkli deploy \
    --network sepolia \
    --class-hash 0x041a6f0ed5924d35e1c50d569c3a56f4e8c4a6f2d3c5e4f1a2b3c4d5e6f7a8b \
    --constructor-args 0xYOUR_WALLET_ADDRESS
```

### Option 3: Python with starknet.py

```bash
python3 scripts/deploy_sepolia.py --wallet braavos --address 0xYOUR_ADDRESS
```

## Class Hash

```
Contract: starknet_shielded_pool::ShieldedPool
Class Hash: (get from compiled artifacts)
```

### Get Class Hash from Compiled Contract

```bash
# The class hash is in the .sierra.json file
cat target/dev/starknet_shielded_pool.sierra.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
print('Class Hash:', data.get('contract_class', {}).get('contract_class_hash', 'N/A'))
"
```

## Contract Address (After Deploy)

```
Save this: 0xDEPLOYED_ADDRESS
```

## Verify on Voyager

```
https://sepolia.voyager.online/contract/0xDEPLOYED_ADDRESS
```

## Interact via Voyager

1. Go to contract page
2. Click "Write Contract"
3. Connect wallet
4. Call functions:
   - `deposit(commitment)`
   - `get_pool_balance()`
   - `get_merkle_root()`

## Full Deployment Flow

```
┌─────────────────────────────────────────────────────────┐
│ 1. Get Sepolia ETH (faucet)                            │
│ 2. Install wallet (Braavos/Argent X)                   │
│ 3. Get class hash from compiled contract               │
│ 4. Deploy via wallet or CLI                            │
│ 5. Save contract address                               │
│ 6. Verify on Voyager                                   │
│ 7. Test with small amounts (0.001 ETH)                 │
└─────────────────────────────────────────────────────────┘
```

## Test Amounts

**Recommended for testing:**
- Deposit: 0.001 - 0.01 ETH
- Transfer: 0.0001 - 0.001 ETH
- Withdraw: Same as deposit

**Never test with large amounts on testnet!**

## Files

```
scripts/
├── deploy_sepolia.py   # Python deployment script
├── interact.py         # Contract interaction
└── sdk.py              # Python SDK
```

## Security Notes

⚠️ **Before mainnet:**
- Full security audit required
- Formal verification recommended
- Bug bounty program
- Multi-sig ownership
- Timelock on upgrades
