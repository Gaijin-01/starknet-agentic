# Blockchain Dev Scripts

Utility scripts for blockchain development workflow.

## Scripts

### Shell Scripts

| Script | Purpose |
|--------|---------|
| `project-init.sh` | Initialize new blockchain project (Solidity/Rust/Cairo/Move/Go/Vyper) |
| `compile-and-test.sh` | Compile + run tests, auto-detects language |
| `deploy-contract.sh` | Deploy smart contract to any network |
| `audit-security.sh` | Run Slither, Mythril, Echidna security analysis |
| `zk-prover.sh` | Generate ZK proofs (Circom/Noir/Gnark) |

### Python Scripts

| Script | Purpose |
|--------|---------|
| `agent-loop.py` | Autonomous ReAct/Plan-and-Execute/OODA agent loop |
| `memory-manager.py` | Vector DB memory for code patterns & past solutions |

## Quick Start

```bash
# Make scripts executable
chmod +x *.sh
chmod +x *.py

# Initialize a Solidity project
./project-init.sh solidity my-defi

# Deploy
./deploy-contract.sh MyContract sepolia --verify

# Run security audit
./audit-security.sh all

# Run ZK proof generation
./zk-prover.sh circuits/voting.circom witness.json

# Start autonomous agent
python3 agent-loop.py --task "Deploy a Uniswap V3 clone" --mode react
```

## Configuration

Create `.env` file:
```bash
PRIVATE_KEY=0x...
SEPOLIA_RPC=https://...
ETHERSCAN_API_KEY=...
```

## Requirements

- **Solidity**: Foundry (`forge`), Hardhat, or both
- **Rust/Cargo**: Rust toolchain + Anchor CLI
- **Cairo**: Scarb, Starknet Foundry
- **Move**: Aptos CLI or Sui CLI
- **Go**: Go 1.21+
- **Python**: 3.10+ with LangChain for memory/agent scripts
