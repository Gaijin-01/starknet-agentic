# Testnet Readiness Estimate

## Executive Summary

| Skill | Status | Implementation | Hours to Complete | Dependencies |
|-------|--------|----------------|-------------------|--------------|
| starknet-privacy | 25% | Mock/Simulated | 40-60 | Cairo 2.12+, Garaga, SnarkJS |
| starknet-py | 60% | Partial Implementation | 8-12 | starknet-py (installed) |
| starknet-mini-pay | 70% | Mostly Functional | 12-16 | starknet-py, qrcode, telegram-bot |

---

## starknet-privacy

### Status: 25% Complete

**What's Implemented:**
- Python simulation layer (`shielded_pool.py`, `notes.py`, `merkle_tree.py`)
- CLI interface (`cli.py`)
- Mock ZK proof generator (`zk_proof_generator.py`)
- SDK wrapper (`sdk.py`) - stubs for async operations

**Stubs Found:**
| File | Stub Type | Description |
|------|-----------|-------------|
| `scripts/shielded_pool.py` | PARTIAL | Uses simulated Pedersen hash (SHA256), not real Cairo Pedersen |
| `scripts/garaga_integration.py` | STUB | Checks for garaga, fails gracefully if not installed |
| `scripts/sdk.py` | PARTIAL | `_get_account()` returns incomplete Account (no address derivation) |
| `scripts/zk_circuit.py` | MOCK | MockZKProver returns fake proofs, no real crypto |
| `contracts/payment_request.cairo` | MISSING | File does not exist |
| `scripts/deploy.py` | STUB | Requires compiled contract artifacts that don't exist |

**Missing Python Dependencies:**
```bash
pip install garaga --break-system-packages  # Python 3.10-3.12 only (has 3.14 conflict)
pip install starknet-py  # Already present
```

**Starknet Dependencies:**
- **Scarb**: 2.14.0+ (for Cairo 2.12 contracts) - NOT INSTALLED
- **Starknet Foundry (Forge)**: For testing Cairo contracts - NOT INSTALLED
- **snarkjs**: For ZK proof generation (npm) - NOT INSTALLED
- **Node.js**: For snarkjs workflow - May not be available

**Hours to Complete:**
- **Minimum**: 40 hours (2 weeks full-time)
- **With Testing**: 60 hours (3 weeks)

**Breakdown:**
| Component | Hours | Notes |
|-----------|-------|-------|
| Cairo Contract Development | 16 | ShieldedPool, Verifier, Token |
| Garaga Integration (ZK) | 12 | Requires Python downgrade or Docker |
| Trust Setup & Prover | 8 | Download ptau, generate keys |
| SDK Completion | 4 | Fix async methods, account derivation |
| Integration Tests | 8 | End-to-end with testnet |
| Documentation | 4 | Deployment guides |

---

## starknet-py

### Status: 60% Complete

**What's Implemented:**
- Basic CLI (`cli.py`) with balance, account-info commands
- Network configuration (mainnet/sepolia)
- Token addresses (ETH, USDC, STRK)
- Simple call_contract wrapper

**Stubs Found:**
| File | Stub Type | Description |
|------|-----------|-------------|
| `scripts/cli.py` | PARTIAL | `deploy`, `call`, `invoke` commands just print notes |
| `scripts/starknet_client.py` | MISSING | File does not exist |
| ERC20 ABI | PARTIAL | Only `transfer` and `balanceOf` implemented |

**Missing Python Dependencies:**
```bash
pip install starknet-py --break-system-packages  # Already in requirements
```

**Starknet Dependencies:**
- None additional - uses starknet-py which handles RPC

**Hours to Complete:**
- **Minimum**: 8 hours (1 day)
- **With Testing**: 12 hours (1.5 days)

**Breakdown:**
| Component | Hours | Notes |
|-----------|-------|-------|
| Implement `call` command | 2 | Parse ABI, call contract |
| Implement `invoke` command | 3 | Account signing, fee estimation |
| Implement `deploy` command | 2 | Declare + Deploy flow |
| Add Account class | 2 | Key derivation, address from pubkey |
| Error handling | 1 | RPC error codes |

---

## starknet-mini-pay

### Status: 70% Complete

**What's Implemented:**
- Core `MiniPay` class with transfer functionality
- QR code generator (`qr_generator.py`)
- Payment link builder (`link_builder.py`)
- Invoice manager with SQLite persistence (`invoice.py`)
- CLI with async handling (`cli.py`)
- Telegram bot stub (`telegram_bot.py` - referenced in SKILL.md but file exists)

**Stubs Found:**
| File | Stub Type | Description |
|------|-----------|-------------|
| `scripts/telegram_bot.py` | INCOMPLETE | Referenced but not fully implemented |
| `scripts/mini_pay_fixed.py` | FUNCTIONAL | Actually well-implemented |
| `scripts/mini_pay.py` | LEGACY | Old version, `mini_pay_fixed.py` is the working one |

**Missing Python Dependencies:**
```bash
pip install qrcode[pil] --break-system-packages
pip install python-telegram-bot --break-system-packages  # For future bot
pip install aiosqlite --break-system-packages
```

**Starknet Dependencies:**
- **starknet-py**: Already required and used

**Hours to Complete:**
- **Minimum**: 12 hours
- **With Testing**: 16 hours

**Breakdown:**
| Component | Hours | Notes |
|-----------|-------|-------|
| Telegram Bot | 6 | Full bot commands, webhook setup |
| Multi-token Support | 2 | STRK, USDC complete, add DAI |
| Error Handling | 2 | Better error messages, retries |
| Batch Payments | 2 | Multiple transfers in one tx |
| Tests | 4 | Integration tests with testnet |

---

## TOTAL ESTIMATE

| Phase | Hours | Days | Description |
|-------|-------|------|-------------|
| **Minimum** | 60 hours | 7.5 days | Core functionality only |
| **With Testing** | 88 hours | 11 days | Full QA and edge cases |

### Parallel Work Streams

| Stream | Skills | Duration |
|--------|--------|----------|
| A | starknet-py CLI completion | Day 1 |
| B | starknet-mini-pay (excluding bot) | Days 1-2 |
| C | starknet-privacy Cairo contracts | Days 2-5 |
| D | ZK integration + Testing | Days 5-7 |
| E | Integration Testing | Days 7-11 |

---

## CRITICAL PATH

### 1. First Blocker: Python Version Incompatibility

**Problem:** `garaga` library requires Python 3.10-3.12, but current environment runs Python 3.14.

**Impact:** Blocks all ZK-SNARK functionality in starknet-privacy.

**Solution Options:**

| Option | Time | Pros | Cons |
|--------|------|------|------|
| Use Docker with Python 3.12 | 2 hours | Clean separation | Docker overhead |
| Use snarkjs directly (Node.js) | 4 hours | No Python version issues | Extra tooling |
| Wait for garaga 3.14 support | Unknown | Native | Blocks progress |

**Recommended:** Use Docker for garaga + Cairo contracts, snarkjs for proofs.

---

### 2. Second Blocker: Missing Cairo Contracts

**Problem:** No compiled Cairo contracts exist. The `contracts/` directory is empty or missing artifacts.

**Impact:** Cannot deploy shielded pool to testnet without contracts.

**Required Contracts:**
| Contract | Purpose | Status |
|----------|---------|--------|
| `ShieldedPool` | Main pool contract | Not written |
| `Verifier` | ZK proof verifier | Not written |
| `ERC20` | Token wrapper | Can use existing |
| `TokenBridge` | Deposit/withdraw | Not written |

**Solution:**
1. Install Scarb 2.14.0+
2. Write Cairo contracts (2-3 days)
3. Compile and test locally (1 day)
4. Deploy to testnet (1 day)

---

### 3. Third Blocker: No Testnet Account

**Problem:** No funded testnet account configured.

**Impact:** Cannot execute any on-chain transactions.

**Solution:**
1. Get testnet ETH from faucet: https://starknet-faucet.pk Consulting
2. Fund via bridge: https://starkgate.app
3. Configure environment:
```bash
export STARKNET_PRIVATE_KEY=...
export STARKNET_ACCOUNT_ADDRESS=...
```

---

## DEPENDENCY INSTALLATION

### Quick Install (starknet-py + mini-pay only)

```bash
cd /home/wner/clawd/skills/_integrations/starknet-py
pip install -e . --break-system-packages

cd /home/wner/clawd/skills/_integrations/starknet-mini-pay
pip install -r requirements.txt --break-system-packages
```

### Full Install (including ZK)

```bash
# Install Scarb (Cairo toolchain)
curl --proto '=https' --tlsv1.2 -sSf https://docs.starknet.io/release横向_2.14.0/install.sh | sh

# Install Node.js for snarkjs
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
npm install -g snarkjs

# Docker for garaga (optional)
docker run --rm -it python:3.12-slim bash
pip install garaga
```

---

## RECOMMENDED PATH FORWARD

### Week 1: Foundation
1. ✅ Day 1: Complete starknet-py CLI (8 hours)
2. ✅ Days 1-2: Finish starknet-mini-pay core (12 hours)
3. ✅ Days 2-5: Write Cairo contracts (32 hours)
4. ✅ Days 5-6: Local testing with starknet-devnet (16 hours)

### Week 2: ZK Integration
5. ✅ Days 6-7: Trust setup, proof generation (16 hours)
6. ✅ Days 7-8: Deploy to testnet (16 hours)
7. ✅ Days 8-11: Integration testing, bug fixes (32 hours)

### Total: 132 hours (3.3 weeks with buffer)

---

## Files Referenced

- `/home/wner/clawd/skills/_integrations/starknet-privacy/SKILL.md`
- `/home/wner/clawd/skills/_integrations/starknet-privacy/scripts/cli.py`
- `/home/wner/clawd/skills/_integrations/starknet-privacy/scripts/shielded_pool.py`
- `/home/wner/clawd/skills/_integrations/starknet-privacy/scripts/garaga_integration.py`
- `/home/wner/clawd/skills/_integrations/starknet-privacy/scripts/sdk.py`
- `/home/wner/clawd/skills/_integrations/starknet-privacy/scripts/zk_proof_generator.py`
- `/home/wner/clawd/skills/_integrations/starknet-privacy/ZK_SNARK_INTEGRATION.md`
- `/home/wner/clawd/skills/_integrations/starknet-py/SKILL.md`
- `/home/wner/clawd/skills/_integrations/starknet-py/scripts/cli.py`
- `/home/wner/clawd/skills/_integrations/starknet-mini-pay/SKILL.md`
- `/home/wner/clawd/skills/_integrations/starknet-mini-pay/scripts/cli.py`
- `/home/wner/clawd/skills/_integrations/starknet-mini-pay/scripts/mini_pay_fixed.py`
- `/home/wner/clawd/skills/_integrations/starknet-mini-pay/scripts/qr_generator.py`
- `/home/wner/clawd/skills/_integrations/starknet-mini-pay/scripts/link_builder.py`
- `/home/wner/clawd/skills/_integrations/starknet-mini-pay/scripts/invoice.py`

---

*Generated: 2026-02-06*
*For: Testnet Deployment Readiness Assessment*
