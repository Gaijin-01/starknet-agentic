# Starknet Shielded Pool

Privacy-preserving confidential transactions on Starknet using ZK-SNARKs.

## Quick Start

### 1. Python Demo (Works Now)
```bash
cd /home/wner/clawd/skills/starknet-privacy

# Run basic shielded pool demo
python3.12 scripts/cli.py demo

# Run ZK-SNARK demo (mock proofs)
source .venv/bin/activate
python3.12 scripts/zk_circuit.py
```

### 2. Cairo Contract (Requires Scarb)
```bash
# Compile contract
~/.local/bin/scarb-new build

# Output: target/dev/starknet_shielded_pool.sierra.json
```

### 3. Deploy to Starknet (Requires Wallet)
```bash
# Using Starkli
starkli deploy --network sepolia \
  --class-hash target/dev/starknet_shielded_pool_ShieldedPool.contract_class_hash
```

## Project Structure

```
starknet-privacy/
├── scripts/
│   ├── shielded_pool.py     # Core privacy pool logic
│   ├── cli.py               # Command-line interface
│   ├── zk_circuit.py        # ZK-SNARK circuit (mock)
│   └── sdk.py               # Python SDK
├── contracts/
│   └── starknet_shielded_pool/
│       ├── src/lib.cairo    # Cairo contract
│       └── README.md        # Deployment guide
├── tests/
│   └── test_pool.py         # Unit tests
├── ZK_SNARK_INTEGRATION.md  # ZK integration guide
└── COMPILE_STATUS.md        # Cairo compiler status
```

## Features

| Feature | Status | Description |
|---------|--------|-------------|
| Basic Pool | ✅ Working | Deposit, transfer, withdraw |
| ZK-SNARK | 🔄 Mock | Circuit defined, proof generation |
| Cairo Contract | ✅ Compiled | With Scarb 2.15.1 |
| On-chain Deploy | ⏳ Pending | Requires wallet + Sepolia ETH |

## Commands

```bash
# Python CLI
python3.12 scripts/cli.py demo              # Run demo
python3.12 scripts/cli.py deposit --amount 100  # Deposit
python3.12 scripts/cli.py transfer --help      # Transfer help

# Cairo
~/.local/bin/scarb-new build                # Compile contract

# ZK-SNARK (mock)
source .venv/bin/activate
python3.12 scripts/zk_circuit.py            # Run ZK demo
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│              SHIELDED POOL                      │
├─────────────────────────────────────────────────┤
│  User deposits ETH → receives encrypted note    │
│  User spends note → generates ZK proof         │
│  Smart contract verifies proof on-chain        │
│  Recipient receives encrypted note             │
├─────────────────────────────────────────────────┤
│  Privacy: Commitments (not amounts) on-chain    │
│  Security: ZK proofs verify correctness         │
│  Finality: Starknet settlement (~5 min)         │
└─────────────────────────────────────────────────┘
```

## Dependencies

- Python 3.12+
- Scarb 2.15.1+ (for Cairo)
- Starknet wallet (for deployment)
- Sepolia ETH (for testing)

## Documentation

- [Cairo Contract](./contracts/starknet_shielded_pool/README.md)
- [ZK-SNARK Integration](./ZK_SNARK_INTEGRATION.md)
- [CLI Usage](./scripts/cli.py --help)

## Next Steps

1. ✅ Basic pool logic working
2. 🔄 Install Garaga for real ZK proofs
3. ⏳ Deploy to Starknet Sepolia
4. ⏳ Add full ZK verification on-chain
5. ⏳ Audit security

## License

MIT
