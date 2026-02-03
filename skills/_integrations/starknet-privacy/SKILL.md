---
name: starknet-privacy
description: |
  Privacy protocols for Starknet: confidential transactions, shielded pools, and note-based privacy using ZK-SNARKs.
version: 1.0.0
updated: 2026-02-01
---

# Starknet Privacy Skill

Privacy-preserving protocols for Starknet using confidential notes, shielded pools, and ZK-SNARKs.

## Overview

Enable private transactions on Starknet through:
- **Confidential Notes** - Encrypted UTXO-style notes
- **Shielded Pools** - Privacy pools (like Zcash shielded pool)
- **ZK-SNARKs** - Zero-knowledge proofs via Garaga library
- **Selective Privacy** - Choose transparent or shielded transfers

## Architecture

```
User → Shielded Pool (encrypted notes)
      ↓
    Contract stores encrypted note + nullifier
      ↓
    Event emitted for recipient
      ↓
    Recipient scans events, decrypts note
      ↓
    Private balance confirmed
```

## Workflow

### 1. Setup Phase
```python
from starknet_privacy import ShieldedPool, ConfidentialNote

# Initialize the shielded pool
pool = ShieldedPool(
    name="my-pool",
    merkle_depth=16
)

# Or use SDK for contract interaction
from sdk import ShieldedPoolSDK

sdk = ShieldedPoolSDK(
    contract_address="0x...",  # Deployed contract
    rpc_url="https://rpc.starknet.lava.build:443"
)
```

### 2. Deposit Flow (Transparent → Shielded)
1. Generate note commitment: `create_commitment(value, secret, salt)`
2. Call `pool.deposit(amount, owner_secret)` or `sdk.deposit(commitment, amount)`
3. Transaction confirmed on Starknet
4. Receive encrypted note commitment

### 3. Transfer Flow (Shielded → Shielded)
1. Fetch owned notes `pool.get_balance:(secret)`
2. Generate merkle proof: `generate_merkle_proof(commitments, index)`
3. Create transfer: `pool.create_transfer(from_commitment, to_address, amount, secret)`
4. Publish nullifier (prevents double-spend)
5. New encrypted note created for recipient

### 4. Withdraw Flow (Shielded → Transparent)
1. Select note to withdraw
2. Generate merkle proof
3. Call `pool.withdraw(commitment, secret, recipient)` or `sdk.withdraw(...)`
4. Nullifier published, note burned
5. ETH sent to recipient

### 5. Verification
```python
# Verify pool integrity at any time
integrity = pool.verify_integrity()
print(f"Valid: {integrity['valid']}")
print(f"Issues: {integrity['issues']}")

# Check nullifier status via SDK
used = await sdk.is_nullifier_used(nullifier)
```

## Error Handling

All functions include error handling for common cases:

| Error | Cause | Solution |
|-------|-------|----------|
| `ValueError: Amount must be positive` | Invalid deposit amount | Check amount > 0 |
| `ValueError: Note not found` | Unknown commitment | Verify commitment exists |
| `ValueError: Insufficient balance` | Note value < amount | Use different note |
| `ValueError: Note already spent` | Nullifier already published | Use different note |
| `ValueError: Invalid secret` | Wrong decryption key | Use correct secret |

```python
try:
    result = pool.deposit(amount, secret)
except ValueError as e:
    print(f"Deposit failed: {e}")
    # Handle specific error case

try:
    result = pool.create_transfer(commitment, recipient, amount, secret)
except ValueError as e:
    if "not found" in str(e):
        # Note doesn't exist
        pass
    elif "already spent" in str(e):
        # Note was already used
        pass
    elif "Insufficient" in str(e):
        # Not enough balance
        pass
```

## Components

| Component | Purpose |
|-----------|---------|
| Note Registry | Stores encrypted notes |
| Nullifier Set | Prevents double-spending |
| Garaga | ZK-SNARK circuit library |
| Shielded Pool | Pool for private deposits/withdrawals |

## Dependencies

```bash
# Garaga library for ZK-SNARKs on Starknet
pip install garaga --break-system-packages

# For CLI operations
pip install starknet-py --break-system-packages
```

## Quick Start

### 1. Deposit to Shielded Pool

```python
from starknet_privacy import ShieldedPool

pool = ShieldedPool(
    registry_address="0x...",
    rpc_url="https://rpc.starknet.lava.build:443"
)

# Deposit with privacy
tx = pool.deposit(
    amount=100_000_000,  # in wei
    secret_key=0x...,    # for note encryption
    recipient_address=0x...
)
await tx.wait()
```

### 2. Create Confidential Note

```python
from starknet_privacy import ConfidentialNote

note = ConfidentialNote.create(
    value=50_000_000,
    secret=0x...,           # Only owner can decrypt
    nullifier_salt=0x...    # For nullifier
)

# Note is encrypted and stored in registry
```

### 3. Spend Note (Private Transfer)

```python
from starknet_privacy import NoteSpend

spend = NoteSpend(
    note=note,
    recipient_address=0x...,    # New owner
    nullifier_secret=0x...,      # Prove ownership
    merkle_path=[...],           # Membership proof
    zk_proof={...}               # ZK-SNARK proof
)

tx = spend.execute()
await tx.wait()
```

### 4. Withdraw from Shielded Pool

```python
from starknet_privacy import ShieldedWithdrawal

withdrawal = ShieldedWithdrawal(
    note=note,
    recipient_address=0x...,
    zk_proof={...}  # Proof of valid note
)

tx = withdrawal.execute()
await tx.wait()
```

## CLI Usage

```bash
# Status and pool info
python3.12 scripts/cli.py status

# Run demo
python3.12 scripts/cli.py demo

# Deposit 100 ETH to shielded pool (auto-generates secret)
python3.12 scripts/cli.py deposit --amount 100

# Check balance (need your secret)
python3.12 scripts/cli.py balance --secret 0x...

# Private transfer between notes
python3.12 scripts/cli.py transfer --from-note 0x... --to-address 0x... --amount 50 --secret 0x...

# Withdraw from shielded pool
python3.12 scripts/cli.py withdraw --commitment 0x... --secret 0x... --recipient 0x...

# Create standalone confidential note
python3.12 scripts/cli.py create-note --value 10

# Check pool integrity
python3.12 scripts/cli.py integrity

# Export/Import pool state (for persistence)
python3.12 scripts/cli.py export --output my_pool.json
python3.12 scripts/cli.py import --input my_pool.json
```

### Demo Flow

```bash
# 1. Run demo to see full workflow
python3.12 scripts/cli.py demo

# 2. Deposit 100 ETH (auto-generates secret)
python3.12 scripts/cli.py deposit --amount 100

# 3. Check balance
python3.12 scripts/cli.py balance --secret <your-secret>

# 4. Transfer 50 ETH (creates new notes)
python3.12 scripts/cli.py transfer --from-note <commitment> --to-address 0x... --amount 50 --secret <your-secret>

# 5. Check integrity
python3.12 scripts/cli.py integrity
```

## Privacy Levels

| Level | Description | Visibility |
|-------|-------------|------------|
| **Transparent** | Normal Starknet tx | All public |
| **Shielded** | In shielded pool | Only owner knows balance |
| **Confidential** | Encrypted notes | Amount & owner encrypted |
| **Anonymous** | Hidden sender | Even sender hidden (future) |

## Key Concepts

### Nullifier
Prevents double-spending by publishing a hash of the note + secret.

### Merkle Tree
Stores all notes in a Merkle tree for membership proofs.

### ZK-SNARK Proof
Proves note validity without revealing:
- Note value
- Note owner
- Transaction details

## Garaga Integration

Garaga provides circuits for:
- Note commitment
- Nullifier computation
- Merkle membership proof
- Range proofs (amount > 0)

## Shielded Pool Flow

```
1. Deposit:
   User → ETH → Shielded Pool Contract
          ↓
        Encrypted note created
          ↓
        Event emitted

2. Transfer:
   Sender note → Nullifier published
          ↓
        New encrypted note for recipient
          ↓
        Event emitted

3. Withdraw:
   Shielded Pool → ETH → Recipient
          ↓
        Nullifier prevents re-use
```

## Security Considerations

- **Deposit/Withdrawal privacy**: Visible on-chain
- **Transfer privacy**: Full confidentiality
- **Metadata**: Transaction metadata may leak timing
- **Counterparties**: Know each other if revealed

## Troubleshooting

### Installation Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: No module named 'starknet_py'` | starknet-py not installed | `pip install starknet-py --break-system-packages` |
| `ModuleNotFoundError: No module named 'garaga'` | garaga not installed | `pip install garaga --break-system-packages` |
| `cryptography` import fails | Missing cryptography lib | `pip install cryptography` |

### Runtime Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `[INSUFFICIENT_BALANCE] Insufficient balance: X < Y` | Note value < amount | Use larger note or combine notes |
| `[NOTE_NOT_FOUND] Note not found: 0x...` | Unknown commitment | Verify commitment exists with `pool.get_balance(secret)` |
| `[NOTE_SPENT] Note already spent` | Nullifier already published | Use different note |
| `[INVALID_SECRET] Invalid secret for note` | Wrong decryption key | Use correct secret key |

### Contract Deployment

| Issue | Cause | Solution |
|-------|-------|----------|
| `Class hash computation failed` | Missing Cairo tooling | Use wallet UI or starknet-rs |
| `Transaction stuck in PENDING` | Network congestion | Wait or increase max_fee |
| `DECLARE_FAILED` | Contract class already exists | Use different class hash |

### Debug Commands

```bash
# Check pool integrity
python3 scripts/cli.py integrity

# Verify note exists
python3 -c "
from shielded_pool import ShieldedPool
pool = ShieldedPool()
pool.import_state()  # Load saved state
print(f'Total notes: {len(pool.notes)}')
print(f'Spent nullifiers: {len(pool.nullifiers)}')
"

# Export state for debugging
python3 scripts/cli.py export --output debug_pool.json
```

## Resources

- [SNIP-10: Privacy-Preserving Transactions](https://community.starknet.io/t/snip-10)
- [Garaga Library](https://github.com/keep-starknet-strange/garaga)
- [Privacy on Starknet (NOKLabs)](https://medium.com/@NOKLabs)
