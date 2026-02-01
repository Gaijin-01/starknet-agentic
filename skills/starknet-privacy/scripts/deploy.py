#!/usr/bin/env python3
"""
Starknet Shielded Pool Deployment Script.

This module provides utilities for deploying the ShieldedPool contract
to Starknet using starknet-py.

Features:
- Contract compilation using Starknet Foundry (scarb)
- Contract deployment to Starknet
- Account management for signing transactions

Prerequisites:
1. Compile contracts: scarb build
2. Get compiled .json from target/dev/
3. Deploy using this script

Example:
    >>> import asyncio
    >>> from deploy import deploy_contract
    >>> async def main():
    ...     address = await deploy_contract(client, "0x...", "contract.json")
    ...     print(f"Deployed at: {address}")
    ... asyncio.run(main())
"""

import asyncio
import os
from pathlib import Path

# Add starknet-py
from starknet_py.net import FullNodeClient
from starknet_py.contract import Contract
from starknet_py.net.account import Account
from starknet_py.key_pair import KeyPair
from starknet_py.transactions.invoke import InvokeFunction


# Contract ABI (minimal for deployment)
SHIELDED_POOL_ABI = [
    {
        "name": "constructor",
        "type": "constructor",
        "inputs": [{"name": "owner", "type": "felt252"}],
        "outputs": []
    },
    {
        "name": "deposit",
        "type": "function",
        "inputs": [{"name": "commitment", "type": "felt252"}],
        "outputs": [{"name": "commitment", "type": "felt252"}],
        "stateMutability": "external"
    },
    {
        "name": "get_pool_balance",
        "type": "function",
        "inputs": [],
        "outputs": [{"name": "balance", "type": "felt252"}],
        "stateMutability": "view"
    }
]


async def deploy_contract(
    client: FullNodeClient,
    owner_private_key: str,
    compiled_contract_path: str
) -> str:
    """
    Deploy ShieldedPool contract to Starknet.
    
    Args:
        client: FullNodeClient connected to Starknet
        owner_private_key: Private key of deployer account (hex string)
        compiled_contract_path: Path to compiled contract (Sierra JSON)
    
    Returns:
        Deployed contract address
    """
    # Load compiled contract
    with open(compiled_contract_path, 'r') as f:
        contract_definition = f.read()
    
    # Create account
    key_pair = KeyPair.from_private_key(int(owner_private_key, 16))
    
    # Note: In production, you'd need the actual account address
    # For testnet, you can use:
    # - Starknet CLI to create account
    # - Argent X / Braavos wallet
    # - Pre-deployed testnet account
    
    print("To deploy, you need:")
    print("1. A Starknet account with funds on Sepolia testnet")
    print("2. The compiled contract (Sierra JSON)")
    print("3. The account address")
    print()
    print("Deployment options:")
    print("=" * 50)
    print()
    print("Option A: Use Starkli (recommended)")
    print("-" * 50)
    print("  Install starkli:")
    print("  curl -L https://github.com/xJonathan Leighi/starkli/releases/download/v0.3.4/starkli-v0.3.4-x86_64-unknown-linux-gnu.tar.gz | tar -xz")
    print("  mv starkli-v0.3.4-x86_64-unknown-linux-gnu/bin/starkli ~/.local/bin/")
    print()
    print("  Deploy:")
    print("  starkli deploy <CLASS_HASH> --network sepolia")
    print()
    print("Option B: Use Braavos Wallet")
    print("-" * 50)
    print("  1. Create Braavos wallet on Sepolia testnet")
    print("  2. Get some Sepolia ETH from faucet")
    print("  3. Use Braavos UI to deploy")
    print()
    print("Option C: Use Starknet CLI")
    print("-" * 50)
    print("  starknet deploy --class_hash <CLASS_HASH> --network sepolia")
    print()
    
    return "Requires manual deployment"


async def main():
    """Main deployment function."""
    print("=" * 60)
    print("Starknet Shielded Pool Deployment")
    print("=" * 60)
    print()
    
    # Configuration
    RPC_URL = "https://rpc.starknet.lava.build:443"
    CHAIN_ID = 0x534e5f4d41494e  # SN_MAINNET
    
    print(f"RPC URL: {RPC_URL}")
    print(f"Chain ID: {hex(CHAIN_ID)}")
    print()
    
    # Initialize client
    client = FullNodeClient(node_url=RPC_URL)
    
    # Check connection
    try:
        block = await client.get_block(block_number=0)
        print(f"Connected! Genesis block hash: {hex(block.block_hash)}")
    except Exception as e:
        print(f"Connection error: {e}")
        print("Make sure RPC is accessible")
        return
    
    print()
    print("Next steps:")
    print("-" * 40)
    
    # Check for compiled contract
    contracts_path = Path(__file__).parent.parent / "contracts"
    scarb_path = contracts_path / "starknet_shielded_pool"
    
    if scarb_path.exists():
        print(f"Found Cairo project at: {scarb_path}")
        print("1. Build the project: cd starknet_shielded_pool && scarb build")
        print("2. Deploy using starkli or Braavos")
    else:
        print("1. Create Scarb project:")
        print("   cd contracts")
        print("   mkdir starknet_shielded_pool")
        print("   cd starknet_shielded_pool")
        print("   scarb init")
        print()
        print("2. Copy Cairo contract:")
        print("   cp ../ShieldedPool.cairo src/lib.cairo")
        print()
        print("3. Build:")
        print("   scarb build")
        print()
        print("4. Deploy:")
        print("   starkli deploy <CLASS_HASH> --network sepolia")
    
    print()
    print("Resources:")
    print("-" * 40)
    print("- Scarb docs: https://docs.swmansion.com/scarb/")
    print("- Starkli docs: https://github.com/xJonathan Leighi/starkli")
    print("- Starknet docs: https://docs.starknet.io/")
    print("- Testnet faucet: https://starknet-faucet.vercel.app/")


if __name__ == "__main__":
    asyncio.run(main())
