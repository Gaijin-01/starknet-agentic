# Starknet Shielded Pool Contracts

Privacy-preserving smart contracts for confidential transactions on Starknet.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Shielded Pool Architecture                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   User → Deposit(ETH) → CommitmentHash                          │
│                              ↓                                   │
│                     Merkle Tree Storage                         │
│                              ↓                                   │
│                     Note Created (encrypted)                    │
│                              ↓                                   │
│   User → Transfer → NullifierPublished                          │
│                    NewNoteCreated (encrypted)                   │
│                              ↓                                   │
│   User → Withdraw → ETH Released                                │
│                    Nullifier Prevents Double-Spend              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Files

```
contracts/
├── ShieldedPool.sol        # Main Solidity contract (for testing)
├── ShieldedPool.cairo      # Cairo implementation (for Starknet)
├── Scarb.toml              # Cairo project config
└── test/
    └── ShieldedPool.t.sol  # Forge tests
```

## Quick Start

### 1. Install Dependencies

```bash
# Foundry (for Solidity testing)
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Scarb (for Cairo/Starknet)
curl --proto '=https' --tlsv1.2 -sSf https://docs.swmansion.com/scarb/install.sh | sh -s -- --no-modify-path
```

### 2. Run Tests (Solidity version)

```bash
cd contracts
forge test
```

### 3. Deploy to Starknet (Cairo version)

```bash
cd contracts

# Initialize Scarb project (if not done)
scarb new starknet_shielded_pool

# Copy Cairo files to src/
cp ShieldedPool.cairo starknet_shielded_pool/src/

# Build
cd starknet_shielded_pool
scarb build

# Deploy to Sepolia testnet
starkli deploy \
    --network sepolia \
    --class-hash target/dev/starknet_shielded_pool_ShieldedPool.contract_class_hash \
    --constructor-args <owner-address>
```

## Contract Functions

### Deposit
```solidity
pool.deposit{value: 1 ether}(commitmentHash);
// Returns: commitmentHash (save this!)
// Emits: Deposited event
```

### Transfer (Private)
```solidity
pool.transfer(
    nullifier,           // Prevents double-spend
    commitmentOld,       // Note to spend
    commitmentNew,       // New note
    merkleProof,         // Proof of commitment inclusion
    encryptedRecipient   // Encrypted recipient data
);
```

### Withdraw
```solidity
pool.withdraw(
    nullifier,       // Proof of ownership
    commitment,      // Original note
    merkleProof,     // Merkle proof
    amount,          // Amount to withdraw
    recipient        // ETH recipient
);
```

## Integration with Python SDK

The Python SDK (`starknet-privacy` skill) can interact with these contracts:

```python
from starknet_py.net import FullNodeClient
from starknet_py.contract import Contract

# Load deployed contract
client = FullNodeClient(node_url="https://rpc.starknet.lava.build:443")
contract = Contract(
    address=DEPLOYED_ADDRESS,
    abi=SHIELDED_POOL_ABI,
    client=client
)

# Deposit
pool_balance_before = await contract.functions["get_pool_balance"].call()

# Call functions
await contract.functions["deposit"].execute(commitment, value=amount_wei)
```

## Security Considerations

⚠️ **Important:**

1. **Deposit/Withdrawal visibility**: While amounts are hidden in transfers, deposit and withdrawal transactions are visible on-chain
2. **Metadata leakage**: Transaction timing and gas patterns may leak information
3. **Nullifier set**: Must be maintained off-chain for scalability
4. **Merkle tree**: In production, use incremental Merkle tree for gas efficiency

## Testing on Localnet

```bash
# Start local Starknet node
starknet-devnet --port 5050

# Deploy
starkli deploy \
    --network local \
    --class-hash <compiled_class_hash>

# Interact
cast send <contract> "deposit(bytes32)" <commitment> --value 1ether
```

## Resources

- [Starknet Documentation](https://docs.starknet.io/)
- [Cairo Language](https://www.cairo-lang.org/)
- [OpenZeppelin Cairo Contracts](https://github.com/OpenZeppelin/cairo-contracts)
- [Garaga Library](https://github.com/keep-starknet-strange/garaga)

## License

MIT
