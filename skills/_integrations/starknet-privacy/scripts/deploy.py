#!/usr/bin/env python3
"""
Deploy ShieldedPool contract to Starknet testnet.
Requires: starknet-py + Python 3.10-3.12

Usage:
    export STARKNET_PRIVATE_KEY=...
    export STARKNET_ACCOUNT_ADDRESS=...
    python3 scripts/deploy.py
"""

import os
import json
from pathlib import Path

# Path to compiled artifacts
CONTRACT_DIR = Path(__file__).parent.parent / "contracts" / "starknet_shielded_pool_forge"
SIERRA_FILE = CONTRACT_DIR / "target/dev/starknet_shielded_pool_ShieldedPoolMinimal.contract_class.json"

# RPC for testnet
TESTNET_RPC = os.getenv("STARKNET_RPC_URL", "https://rpc.starknet.testnet.lava.build")


def load_contract():
    """Load compiled contract artifacts."""
    with open(SIERRA_FILE) as f:
        return json.load(f)


async def deploy():
    """Deploy contract to testnet."""
    try:
        # New starknet-py v0.12+ imports
        from starknet_py.net.account.account import Account
        from starknet_py.net.full_node_client import FullNodeClient
        from starknet_py.net.signer.key_pair import KeyPair
        from starknet_py.contract import Contract
    except ImportError as e:
        print(f"❌ starknet-py not installed: {e}")
        print("   Requires: Python 3.10-3.12")
        print("   Install: pip install starknet-py")
        return
    
    # Load contract
    contract = load_contract()
    sierra = contract["sierra_program"]
    abi = contract["abi"]
    
    print(f"📦 Contract loaded: {len(sierra)} bytecode instructions")
    print(f"📋 ABI: {len(abi)} functions")
    
    # Account setup (from env or error)
    private_key = os.getenv("STARKNET_PRIVATE_KEY")
    account_address = os.getenv("STARKNET_ACCOUNT_ADDRESS")
    
    if not private_key or not account_address:
        print("❌ Missing env vars:")
        print("   STARKNET_PRIVATE_KEY")
        print("   STARKNET_ACCOUNT_ADDRESS")
        return
    
    # Connect to testnet
    client = FullNodeClient(node_url=TESTNET_RPC)
    key_pair = KeyPair.from_private_key(private_key)
    account = Account(
        address=int(account_address, 16),
        client=client,
        key_pair=key_pair,
    )
    
    # Declare contract
    print("🔨 Declaring contract...")
    declared = await Contract.declare(
        account,
        compile_hint=lambda: None,  # Sierra already compiled
        constructor_calldata=[account_address],
    )
    print(f"✅ Declared: class_hash={declared.class_hash}")
    
    # Deploy
    print("🚀 Deploying...")
    deployed = await declared.deploy(
        constructor_calldata=[account_address]
    )
    print(f"✅ Deployed: address={deployed.contract_address}")
    
    # Save deployment info
    deployment_info = {
        "class_hash": str(declared.class_hash),
        "address": str(deployed.contract_address),
        "network": "testnet",
        "rpc": TESTNET_RPC,
    }
    
    with open(CONTRACT_DIR / "deployment.json", "w") as f:
        json.dump(deployment_info, f, indent=2)
    
    print(f"💾 Saved to deployment.json")


if __name__ == "__main__":
    import asyncio
    
    print("=" * 50)
    print("🚀 ShieldedPool Deployment")
    print("=" * 50)
    print(f"Contract: {SIERRA_FILE}")
    print(f"Network: Testnet")
    print()
    
    asyncio.run(deploy())
