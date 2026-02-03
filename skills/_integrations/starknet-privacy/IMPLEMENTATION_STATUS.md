# Privacy Pool Implementation Status

## ✅ COMPLETED (Scarb 2.8.1 / Cairo 2.8.0)

### Contract: `contracts/starknet_shielded_pool_forge/src/lib.cairo`

**Features implemented:**
- ✅ Basic storage with `LegacyMap` (deprecated but working)
- ✅ `deposit(commitment)` - stores commitment, returns index
- ✅ `spend(nullifier, new_commitment)` - nullifier tracking
- ✅ `set_merkle_root()` - admin function for off-chain tree integration
- ✅ View functions: `get_merkle_root()`, `is_nullifier_used()`, etc.
- ✅ Pedersen hash helpers for commitment/nullifier computation

**Compilation:**
```bash
cd contracts/starknet_shielded_pool_forge
~/.local/bin/scarb build
# ✅ Compiles successfully
```

**Generated artifacts:**
- `target/release/starknet_shielded_pool_sierra.json` - Sierra bytecode
- `target/release/starknet_shielded_pool_casm.json` - CASM (for testnet deploy)

---

## 🔄 IN PROGRESS

### Off-chain Merkle Tree
**File:** `scripts/merkle_tree.py`

**Status:**
- ✅ Basic sparse Merkle tree implementation
- ✅ Commitment/nullifier generation
- ⚠️ Pedersen hash is simulated (SHA256-based)
- ⚠️ Merkle proof verification fails with real contract

**Next steps:**
- [ ] Use `starknet.py` or `garaga` for real Pedersen hash
- [ ] Implement incremental tree updates
- [ ] Generate proof format compatible with Cairo contract

---

## 📋 ROADMAP

### NOW (Scarb 2.8.1) - TESTBED
```
├── [x] Minimal Cairo contract (LegacyMap, no events)
├── [x] Off-chain Merkle tree (simulated)
├── [ ] Real Pedersen hash (starknet.py)
├── [ ] Deploy to testnet (Starknet Goerli)
└── [ ] Basic integration tests
```

### LATER (Scarb 2.14.0+) - PRODUCTION
```
├── [ ] Upgrade to starknet="2.15.0+" for modern Map, events
├── [ ] Full event emission (Deposit/Transfer/Withdrawal)
├── [ ] Garaga ZK verifier integration (Groth16/Plonk)
├── [ ] On-chain Merkle tree (sparse Patricia tree)
├── [ ] Production audit & deployment
└── [ ] Integration with OpenClaw (starknet-py)
```

---

## 📁 FILES

```
starknet-privacy/
├── contracts/
│   └── starknet_shielded_pool_forge/
│       ├── Scarb.toml          # starknet=">=2.0.0"
│       ├── src/
│       │   └── lib.cairo       # Minimal ShieldedPool contract
│       └── target/             # Compiled artifacts
├── scripts/
│   └── merkle_tree.py          # Off-chain Merkle tree
└── README.md
```

---

## 🔗 DEPENDENCIES

| Component | Version | Status |
|-----------|---------|--------|
| Scarb | 2.8.1 | ✅ Working |
| Cairo | 2.8.0 | ✅ Working |
| starknet | 2.8.0 | ✅ Available |
| starknet.py | - | ⚠️ Not installed (Python 3.14) |
| Garaga | 2.14.0+ | ❌ Requires Scarb 2.14.0+ |

---

## 🚀 NEXT STEPS

1. **Testnet deployment** (when ready):
   ```bash
   # Requires starknet.py and testnet account
   starknet deploy --sierra target/release/starknet_shielded_pool_sierra.json
   ```

2. **Real Pedersen hash** (for proper off-chain simulation):
   - Install `garaga` (requires Scarb 2.14.0+)
   - Or use `starknet.py` with proper Python (3.10-3.12)

3. **Scarb upgrade** (when OpenClaw integration is stable):
   - Backup current `~/.local/bin/scarb`
   - Install Scarb 2.14.0+
   - Migrate contract to new patterns

---

## 📊 CONTRACT FUNCTIONS

| Function | Type | Description |
|----------|------|-------------|
| `deposit(commitment)` | external | Store commitment, return index |
| `spend(nullifier, new_commitment)` | external | Double-spend protection |
| `set_merkle_root(root)` | external | Admin: update tree root |
| `is_nullifier_used(nullifier)` | view | Check spent status |
| `get_merkle_root()` | view | Get current root |
| `get_next_index()` | view | Get next leaf index |
| `get_owner()` | view | Get admin address |
| `is_commitment_valid(commitment)` | view | Check if note exists |

---

*Last updated: 2026-02-03*
*Scarb 2.8.1 | Cairo 2.8.0*
