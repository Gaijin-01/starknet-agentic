---
name: blockchain-dev
description: |
  Полный автономный агент для блокчейн-разработки (2026). Поддержка Solidity, Rust, Cairo, Move, Go, TypeScript/JavaScript, Vyper, Circom/Noir. Инструменты: Hardhat, Foundry, Anchor, Scarb, ethers.js, viem, web3.js, ethers-rs, LangGraph, AutoGen, CrewAI. Автономный режим: ReAct, Plan-and-Execute, OODA-loop, stateful workflows, memory (vector DB), tool-calling (API, nodes, wallets). Cron/scheduling: встроенный cron, on-chain (Gelato, Chainlink), cloud cron. Используй для: смарт-контрактов, DeFi протоколов, ZK-систем, кросс-чейн мостов, автономных агентов, тестирования, деплоя, аудита безопасности.
---

# Blockchain Developer Agent (2026)

## Overview

A comprehensive autonomous agent for blockchain development (2026). Supports Solidity, Rust, Cairo, Move, Go, TypeScript/JavaScript, Vyper, and Circom/Noir for ZK circuits.

**When to use:**
- Smart contract development (DeFi, NFTs, tokens, protocols)
- Cross-chain bridges and interoperability
- Zero-knowledge proof systems (ZK rollups, voting, privacy)
- Autonomous on-chain agents with AI orchestration
- Security auditing and testing
- Multi-chain deployment and monitoring

**Key capabilities:**
- Multi-language support: EVM (Solidity), Solana (Rust), Starknet (Cairo), Move (Aptos/Sui)
- Agent frameworks: LangGraph, AutoGen, CrewAI for autonomous operation
- Memory systems: Vector DB for long-term, short-term context buffers
- Tool calling: Blockchain APIs, node interaction, wallet operations
- Scheduling: On-chain (Gelato, Chainlink) and cloud-based cron

## Workflow

1. **Initialize Project**
   - Select blockchain/framework based on requirements
   - Set up development environment (Hardhat, Anchor, Scarb, etc.)

2. **Design & Plan**
   - Define smart contract architecture
   - Choose patterns (upgradeable, proxy, diamond)
   - Plan testing strategy (unit, fuzz, formal verification)

3. **Develop**
   - Write contracts with security best practices
   - Implement tests alongside code
   - Use NatSpec for documentation

4. **Test & Audit**
   - Run unit tests with 100% coverage
   - Execute fuzz testing (Echidna, Foundry)
   - Run security tools (Slither, Mythril, Certora)

5. **Deploy**
   - Deploy to testnet first
   - Verify on Etherscan/Sonarscan
   - Mainnet deployment with multi-sig

6. **Monitor**
   - Set up event monitoring
   - Configure alerting for unusual activity
   - Implement upgrade timelocks

## Examples

### DeFi Protocol Development
```
User: "Create an AMM DEX with concentrated liquidity"
Agent:
  1. Plans: [Design architecture, Implement core, Add tests, Deploy]
  2. Creates Uniswap V3-like contract with tick ranges
  3. Writes Forge tests for full range scenarios
  4. Deploys to Sepolia and verifies
```

### ZK Application
```
User: "Create a ZK rollup contract for voting"
Agent:
  1. Researches Circom/Noir circuits for voting proofs
  2. Implements vote circuit + Solidity verifier
  3. Tests proof generation/verification locally
  4. Deploys to Goerli testnet
```

### Cross-Chain Bridge
```
User: "Create a bridge from Ethereum to Solana"
Agent:
  1. Designs two-way bridge architecture
  2. Implements Ethereum lock/unlock contracts
  3. Creates Solana mint/burn program
  4. Runs integration tests
  5. Security audit with Slither
```

### Autonomous Trading Agent
```
User: "Build an agent for DEX arbitrage"
Agent:
  1. Sets up LangGraph with memory + tools
  2. Implements price monitoring and order execution
  3. Vector DB for pattern recognition
  4. Deploys with cloud cron and monitoring
```

## Быстрый старт

### Смарт-контракты (EVM)
```bash
# Создать проект Hardhat
npx hardhat init my-contract --template ts
cd my-contract

# Скомпилировать
npx hardhat compile

# Тесты
npx hardhat test

# Деплой
npx hardhat run scripts/deploy.ts --network sepolia
```

### Solana (Rust)
```bash
# Anchor проект
anchor init my-program
cd my-program

# Сборка
anchor build

# Тесты
anchor test

# Деплой
anchor deploy --provider.cluster mainnet
```

### Starknet (Cairo)
```bash
# Scarb проект
scarb new my-starknet-contract

# Компиляция
scarb build

# Тесты
scarb test

# Тестовыйnet
starknet-devnet --port 5050
```

### ZK- circuits (Circom / Noir)
```bash
# Circom
circom circuits/mycircuit.circom --output circuits/r1cs

# Noir
nargo check
nargo prove
nargo verify
```

## Языки программирования

### Solidity (Ethereum + L2)
- **Фреймворки**: Hardhat, Foundry, Remix
- **Библиотеки**: ethers.js v6, viem, web3.js
- **Стандарты**: ERC-20, ERC-721, ERC-1155, ERC-4626
- **L2**: Optimism, Arbitrum, Base, zkSync
- **Тестирование**: Forge, Hardhat, Slither

### Rust (Solana, Polkadot, Near, Cosmos)
- **Solana**: Anchor framework, solana-program-library
- **Substrate**: Polkadot SDK, parity-scale-codec
- **Near**: near-sdk-rs, near-primitives
- **Cosmos SDK**: tendermint-rs, cosmwasm
- **Инструменты**: cargo, rustup, cargo-clippy

### Cairo (Starknet)
- **Инструменты**: Starknet Foundry (starknet-foundry), Scarb, protostar
- **Библиотеки**: starknet-rs, cairo-lang, OpenZeppelin contracts
- **Тестирование**: starknet-foundry test, protostar test
- **L1 <> L2**: Messaging bridge, ethereum Starknet bridge

### Move (Aptos, Sui)
- **Aptos**: move-cli, aptos-framework, sui-framework
- **Синтаксис**: ресурсы, capabilities, publish modules
- **Тестирование**: move test, sui move test

### Go (Cosmos, backend, nodes)
- **Cosmos SDK**: chain开发区, modules, keeper pattern
- **Tendermint**: consensus, ABCI, p2p
- **gRPC**: cosmos-sdk-proto, cosmwasm-go
- **Node ops**: Cosmos nodes, relayers (Hermes, IBC relayer)

### TypeScript / JavaScript
- **Web3.js**: ethers.js, viem, web3.js, wagmi
- **Front-end**: React + ethers, Ethers.js + Vite
- **Back-end**: Node.js + ethers, Express + web3
- **Тестирование**: Jest + ethers, Mocha + web3

### Vyper (EVM, security-oriented)
- **Особенности**: python-подобный синтаксис, безопасность
- **Фреймворки**: Brownie, Ape Framework
- **Интеграция**: Solidity interop, ERC-20, ERC-721

### Circom / Noir (ZK-SNARK)
- **Circom**: R1CS generation, constraints, witness generation
- **Noir**: ACIR compilation, proof generation, verification
- **Библиотеки**: circomlib, snarkjs, noir-wasm
- **Проверка**: Solidity verifier contracts

### Plonky2 / Halo2 / Gnark (Advanced ZK)
- **Golang**: gnark (bn254, bls12-381 curves)
- **Rust**: plonky2, halo2
- **Применение**: recursive proofs, custom circuits

## Инструменты и фреймворки

### Hardhat
```javascript
// hardhat.config.ts
import { HardhatUserConfig } from "hardhat/config"
import "@nomicfoundation/hardhat-toolbox"

const config: HardhatUserConfig = {
  solidity: "0.8.24",
  networks: {
    sepolia: {
      url: process.env.SEPOLIA_RPC,
      accounts: [process.env.PRIVATE_KEY]
    }
  },
  etherscan: {
    apiKey: process.env.ETHERSCAN_API_KEY
  }
}
export default config
```

### Foundry (Forge)
```bash
# Установка
forge init my-project
cd my-project

# Смарт-контракт
forge create src/MyContract.sol:MyContract --rpc-url $RPC --private-key $KEY

# Тест
forge test -vvv

# Gas report
forge test --gas-report

# Cast (CLI tool)
cast send <contract> "mint()" --rpc-url $RPC --private-key $KEY
```

### Anchor (Solana)
```rust
// programs/my-program/src/lib.rs
use anchor_lang::prelude::*;

declare_id!("11111111111111111111111111111111");

#[program]
mod my_program {
    use super::*;

    pub fn initialize(ctx: Context<Initialize>) -> Result<()> {
        let my_account = &mut ctx.accounts.my_account;
        my_account.data = 0;
        Ok(())
    }
}

#[derive(Accounts)]
struct Initialize<'info> {
    #[account(init, payer = user, space = 8 + 8)]
    pub my_account: Account<'info, MyAccount>,
    #[account(mut)]
    pub user: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[account]
pub struct MyAccount {
    pub data: u64,
}
```

### Scarb / Starknet Foundry
```toml
# Scarb.toml
[package]
name = "my-starknet-contract"
version = "0.1.0"

[dependencies]
starknet = ">=2.0.0"
openzeppelin = "https://github.com/OpenZeppelin/cairo-contracts?tag=v0.12.0"

[[target.starknet-contract]]
sierra = true
```

```cairo
// src/lib.cairo
#[starknet::interface]
pub trait IMyContract<T> {
    fn get_value(self: @T) -> u256;
    fn set_value(ref self: T, value: u256);
}

#[starknet::contract]
mod MyContract {
    #[storage]
    struct Storage {
        value: u256
    }

    #[external(v0)]
    impl IMyContractImpl of super::IMyContract<ContractState> {
        fn get_value(self: @ContractState) -> u256 {
            self.value.read()
        }

        fn set_value(ref self: ContractState, value: u256) {
            self.value.write(value);
        }
    }
}
```

### ethers.js / viem / web3.js
```typescript
// ethers.js v6
import { ethers } from "ethers";

const provider = new ethers.JsonRpcProvider("https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY");
const wallet = new ethers.Wallet(process.env.PRIVATE_KEY, provider);

const contract = new ethers.Contract(ADDRESS, ABI, wallet);
const tx = await contract.mint(amount);
await tx.wait();

// viem (более lightweight)
import { createPublicClient, http } from 'viem'
import { mainnet } from 'viem/chains'

const client = createPublicClient({
  chain: mainnet,
  transport: http()
})
const blockNumber = await client.getBlockNumber()
```

### ethers-rs / web3-rs
```rust
use ethers_providers::{Provider, Http};
use ethers_signers::{Wallet, LocalWallet};
use ethers_contract::{Contract, abi};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let provider = Provider::try_from("https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY")?;
    let wallet: LocalWallet = "0x...".parse()?;
    let client = provider.with_signer(wallet);
    
    let contract = Contract::new(ADDRESS, abi::..., client);
    let tx = contract.method::<_, ()>("mint", ())?.send().await?;
    let receipt = tx.await?;
    Ok(())
}
```

### LangChain / LangGraph (agent orchestration)
```python
# LangGraph autonomous agent
from langgraph.graph import StateGraph, END

def should_continue(state):
    if state["done"]:
        return END
    return "continue"

def execute_tool(state):
    # Execute next tool based on reasoning
    pass

def reason(state):
    # ReAct reasoning
    pass

workflow = StateGraph(State)
workflow.add_node("reason", reason)
workflow.add_node("execute", execute_tool)
workflow.add_conditional_edges("reason", should_continue)
workflow.add_edge("execute", "reason")
workflow.set_entry_point("reason")

app = workflow.compile()
```

### AutoGen / CrewAI (multi-agent)
```python
# AutoGen
from autogen import AssistantAgent, UserProxyAgent, GroupChat

config_list = [...]

assistant = AssistantAgent("assistant", llm_config={"config_list": config_list})
user_proxy = UserProxyAgent("user_proxy", code_execution_config={"work_dir": "coding"})

# CrewAI
from crewai import Agent, Task, Crew

researcher = Agent(role="Researcher", goal="Research DeFi protocols", backstory="...")
developer = Agent(role="Developer", goal="Write smart contracts", backstory="...")

task1 = Task(description="Research Uniswap V4", agent=researcher)
task2 = Task(description="Implement contract", agent=developer)

crew = Crew(agents=[researcher, developer], tasks=[task1, task2])
result = crew.kickoff()
```

### web3.py / brownie / ape
```python
# web3.py
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY"))
contract = w3.eth.contract(address=ADDRESS, abi=ABI)
tx = contract.functions.swap(amountIn).transact({"from": wallet.address})
receipt = w3.eth.wait_for_transaction_receipt(tx)

# brownie
from brownie import interface, accounts

account = accounts.load("mainnet")
token = interface.IERC20("0x...")
tx = token.transfer(to, amount, {"from": account})

# ape
import ape
from ape import project

contract = project.MyContract.deploy(sender=account)
```

## Автономный режим (Agent Loop)

### ReAct Pattern
```
Thought → Action → Observation → Thought → ...
```

```python
async def react_agent(prompt: str, tools: List[Tool], max_iterations: int = 10):
    context = prompt
    for _ in range(max_iterations):
        thought = await llm(f"Thought about: {context}")
        action = await llm(f"Choose action based on: {thought}")
        
        if action.name == "done":
            return action.result
        
        observation = await execute_tool(action)
        context += f"\nThought: {thought}\nAction: {action}\nObservation: {observation}"
```

### Plan-and-Execute
```python
async def plan_and_execute(task: str, tools: List[Tool]):
    # Plan phase
    plan = await llm(f"Create plan for: {task}")
    steps = parse_plan(plan)
    
    # Execute phase
    results = []
    for step in steps:
        result = await execute_step(step, tools)
        results.append(result)
    
    return results
```

### OODA Loop
```python
async def ooda_loop(agent_state: AgentState):
    observe_result = await observe(agent_state)
    orient_result = await orient(observe_result, agent_state.memory)
    decide_result = await decide(orient_result, agent_state.goals)
    act_result = await act(decide_result)
    return act_result
```

### LangGraph Stateful Workflows
```python
from langgraph.graph import StateGraph
from typing import TypedDict

class AgentState(TypedDict):
    messages: List[BaseMessage]
    context: Dict
    goals: List[str]
    memory: Memory

def build_agent_graph() -> StateGraph:
    graph = StateGraph(AgentState)
    graph.add_node("reason", reason_node)
    graph.add_node("execute", execute_node)
    graph.add_node("remember", remember_node)
    
    graph.add_edge("reason", "execute")
    graph.add_edge("execute", "remember")
    graph.add_conditional_edges("remember", should_continue)
    
    return graph.compile()
```

### Memory Systems

#### Vector DB (long-term)
```python
from langchain.vectorstores import Chroma, FAISS
from langchain.embeddings import OpenAIEmbeddings

vectorstore = FAISS.from_documents(docs, embeddings)

# Retrieve similar documents
results = vectorstore.similarity_search(query, k=5)
```

#### Short-term memory
```python
class ShortTermMemory:
    def __init__(self, max_tokens: int = 8000):
        self.buffer = []
        self.max_tokens = max_tokens
    
    def add(self, item: str):
        self.buffer.append(item)
        if self.token_count() > self.max_tokens:
            self.buffer.pop(0)
    
    def get_context(self) -> str:
        return "\n".join(self.buffer)
```

#### Long-term memory
```python
class LongTermMemory:
    def __init__(self, vectorstore):
        self.vectorstore = vectorstore
    
    async def remember(self, key: str) -> List[Document]:
        return self.vectorstore.similarity_search(key, k=10)
    
    async def forget(self, key: str):
        # Remove old/unnecessary memories
        pass
```

### Tool Calling
```python
from langchain.tools import tool

@tool
def deploy_contract(language: str, code: str, network: str) -> str:
    """Deploy smart contract to network"""
    # Implementation
    return f"Deployed at {address}"

@tool
def analyze_security(code: str) -> dict:
    """Analyze smart contract for security vulnerabilities"""
    # Slither, Mythril, etc.
    return report

@tool
def query_blockchain(network: str, query: str) -> dict:
    """Query blockchain data"""
    # eth_call, eth_getLogs, etc.
    return result

tools = [deploy_contract, analyze_security, query_blockchain]
```

## Cron / Scheduling

### Встроенный cron (AO / AgenticOS)
```javascript
// AO (Arweave) cron
import { cron } from "@ao-sdk/core"

cron("*/15 * * * *", async () => {
  const data = await fetchMarketData()
  await arweave.transactions.post({
    data: JSON.stringify(data)
  })
})
```

### On-chain Cron (Gelato, Chainlink)
```solidity
// Gelato Automate
function checker() external view returns (bool canExec, bytes memory execPayload) {
    if (block.timestamp - lastExecution > 1 days) {
        return (true, abi.encodeWithSelector(this.dailyTask.selector));
    }
    return (false, "");
}
```

```solidity
// Chainlink Automation
function checkUpkeep(
    bytes calldata checkData
) external view returns (bool upkeepNeeded, bytes memory performData) {
    upkeepNeeded = block.timestamp - lastTimeStamp > INTERVAL;
    performData = checkData;
}

function performUpkeep(bytes calldata performData) external {
    // Execute scheduled task
}
```

### Cloud Cron + Webhooks
```python
# Vercel Cron
# vercel.json
{
  "crons": [
    {
      "path": "/api/cron/price-update",
      "schedule": "*/5 * * * *"
    }
  ]
}
```

```python
# Cloud Scheduler + Webhook
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('interval', minutes=15)
async def price_update():
    await fetch_and_post_price()

scheduler.start()
```

### Hybrid Approach
```python
async def hybrid_scheduler():
    """Combine on-chain and off-chain scheduling"""
    
    # Off-chain: frequent checks
    asyncio.create_task(offchain_polling(interval=60))
    
    # On-chain: final settlement
    await gelato_execute_ifNeeded()
    
    # Fallback: cloud cron backup
    if on_chain_failed:
        await cloud_webhook_trigger()
```

## Кросс-платформенная разработка (WLS)

### Rust Toolchain
```bash
# Linux
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup default stable
cargo --version

# Windows (WSL2)
wsl --install -d Ubuntu
wsl
# Then run rustup install above
```

### Substrate / Polkadot SDK
```bash
# Установка
rustup default nightly
rustup target add wasm32-unknown-unknown
cargo install substrate-contract-cli

# Создание проекта
substrate-contract new my-pallet
cd my-pallet
cargo contract build
```

### Docker / WSL2
```bash
# Docker в WSL2
# 1. Установить Docker Desktop for Windows
# 2. WSL2 интеграция включена

# Запуск контейнера
docker run -it --rm rust:1.75 bash

# docker-compose для блокчейн стека
version: '3.8'
services:
  hardhat-node:
    image: node:20
    command: npx hardhat node
    ports:
      - "8545:8545"
  
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: blockchain
```

### Git + CI/CD (GitHub Actions)
```yaml
# .github/workflows/ci.yml
name: Smart Contract CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install Foundry
        run: |
          forge install
      
      - name: Run tests
        run: |
          forge test
      
      - name: Security audit
        run: |
          slither . --solc-remaps='node_modules=node_modules'
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to Sepolia
        run: |
          forge script script/Deploy.s.sol:Deploy --rpc-url $SEPOLIA_RPC --broadcast --verify
        env:
          SEPOLIA_RPC: ${{ secrets.SEPOLIA_RPC }}
          PRIVATE_KEY: ${{ secrets.PRIVATE_KEY }}
```

## Примеры использования

### DeFi протокол
```
User: "Создай AMM DEX на Solidity с Concentrated Liquidity"
Agent:
  1. Plan: [Design architecture, Implement core, Add tests, Deploy]
  2. Execute: Создает uniswap-v3-like contract
  3. Test: Forge tests для full range
  4. Deploy: Sepolia + verify
```

### ZK-приложение
```
User: "Создай ZK rollup contract для voting"
Agent:
  1. Research: circom circuits for voting
  2. Implement: Vote circuit + Solidity verifier
  3. Test: Proof generation/verification
  4. Deploy: Goerli testnet
```

### Кросс-чейн мост
```
User: "Создай мост Ethereum → Solana"
Agent:
  1. Design: Two-way bridge architecture
  2. Implement: 
     - Ethereum side: Lock/unlock contracts
     - Solana side: Mint/burn program
  3. Test: Integration tests
  4. Security: Audit with Slither + Securify
```

### Автономный Trading Agent
```
User: "Создай агента для арбитража между DEX"
Agent:
  1. Setup: LangGraph + memory + tools
  2. Tools: price monitoring, order execution
  3. Memory: vector DB для patterns
  4. Deploy: Cloud cron + monitoring
```

## Troubleshooting

### Solidity
| Проблема | Решение |
|----------|---------|
| Out of gas | Оптимизатор + меньше storage ops |
| Reentrancy | Checks-Effects-Interactions pattern |
| Stack too deep | Разбить на несколько функций |

### Rust / Solana
| Проблема | Решение |
|----------|---------|
| Account size | PDA + zero-copy |
| Compute units | Снизить логгинг + inline |
| CPI depth | Limit cross-program calls |

### Cairo / Starknet
| Проблема | Решение |
|----------|---------|
| Gas consumption | Использовать less storage writes |
| Array bounds | Проверять length перед access |
| Felt vs u256 | Преобразовывать правильно |

## Best Practices

1. **Security first**: Всегда audit, Slither, Mythril
2. **Testing**: 100% coverage + fuzz testing
3. **Documentation**: NatSpec comments + README
4. **Gas optimization**: Batch operations + storage packing
5. **Upgradeability**: Proxy patterns + timelock
6. **Monitoring**: Events + alerting
7. **Key management**: Multi-sig + hardware wallets

---

## Implemented Contracts

### Privacy-Preserving Voting Contract (Starknet)

**Location:** `contracts/privacy_voting/`

**Purpose:** Privacy-preserving governance voting with MEV protection for DAOs.

**Features:**
- Encrypted vote commitments using Poseidon hashing
- Two-phase voting: commit → reveal
- MEV protection through vote encryption
- Slashing mechanism for double-voting prevention
- Time-locked reveal mechanism

**Contract Structure:**
```
contracts/privacy_voting/
├── src/
│   ├── lib.cairo          # Module entry point
│   └── voting.cairo       # Main contract
├── Scarb.toml             # Project config
└── tests/
    └── test_voting.cairo  # Unit tests
```

**Key Functions:**
- `submit_vote_commitment()`: Submit encrypted vote hash
- `reveal_vote()`: Reveal actual vote after commit period
- `finalize_voting()`: Finalize results after reveal period
- `slash_double_voter()`: Penalize double-voting attempts

**Usage:**
```bash
# Initialize project
cd contracts/privacy_voting

# Build contract
scarb build

# Run tests
scarb test

# Deploy to testnet
starknet deploy --network testnet --contract target/dev/privacy_voting_PrivacyVoting.contract_class.json
```

**Integration Example:**
```cairo
use privacy_voting::voting::{PrivacyVoting, IPrivacyVoting};

// Initialize
let contract = PrivacyVoting::constructor(
    contract_address_const::<0>(),
    admin,
    proposal_hash,
    100,  // voting duration
    50    // reveal duration
);

// Submit encrypted vote
let commitment = compute_vote_hash(option_id, secret_nonce);
contract.submit_vote_commitment(commitment);

// Reveal after voting period
contract.reveal_vote(option_id, secret_nonce);
```

**Research Context:**
This contract addresses the gap in DAO governance privacy identified in crypto_research.md:
- MEV protection for voting decisions
- Privacy from front-running vote manipulation
- Transparent yet secret voting mechanism
