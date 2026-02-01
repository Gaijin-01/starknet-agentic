#!/usr/bin/env python3.12
"""
Starknet.py CLI - Command-line interface for Starknet operations.

Usage:
    python3.12 scripts/cli.py balance <address>
    python3.12 scripts/cli.py balance-usdc <address>
    python3.12 scripts/cli.py account-info <address>
    python3.12 scripts/cli.py --rpc <custom-rpc> balance <address>
"""

import argparse
import sys
import os

try:
    from starknet_py.net.full_node_client import FullNodeClient
    from starknet_py.net.client_models import Call
except ImportError as e:
    print(f"Error: {e}")
    print("Run: pip install starknet-py --break-system-packages")
    sys.exit(1)

# RPC endpoints - Lava.build (provided by user)
NETWORKS = {
    "mainnet": "https://rpc.starknet.lava.build:443",
    "sepolia": "https://starknet-sepolia.public.blastapi.io/rpc/v0_6"
}

# Token addresses (mainnet)
ETH_TOKEN = "0x049d36570d4e46f48e99674bd3e8462bc8bdf9d19c5f7b8e8f3d5e4c1f5a3e8d"
USDC_TOKEN = "0x053c91253bc9682c04929ca02ed00b3e423f6714d2ea42d73d1b8f3f8d400005"


def get_client(rpc_url):
    """Create a FullNodeClient."""
    return FullNodeClient(node_url=rpc_url)


def cmd_balance(args):
    """Get ETH balance for an address."""
    client = get_client(args.rpc)
    
    try:
        call = Call(
            to_addr=int(ETH_TOKEN, 16),
            selector=0x2e426dad724c5c1a4d1640d5881d0750f5381923d4d37b8e2c5c3e3f16c5f1c,  # balanceOf
            calldata=[int(args.address, 16)]
        )
        result = client.call_contract_sync(call=call)
        balance_wei = result[0]
        balance_eth = balance_wei / 1e18
        print(f"Address: {args.address}")
        print(f"ETH Balance: {balance_eth:.6f} ETH")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_balance_usdc(args):
    """Get USDC balance for an address."""
    client = get_client(args.rpc)
    
    try:
        call = Call(
            to_addr=int(USDC_TOKEN, 16),
            selector=0x2e426dad724c5c1a4d1640d5881d0750f5381923d4d37b8e2c5c3e3f16c5f1c,  # balanceOf
            calldata=[int(args.address, 16)]
        )
        result = client.call_contract_sync(call=call)
        balance_raw = result[0]
        balance_usdc = balance_raw / 1e6
        print(f"Address: {args.address}")
        print(f"USDC Balance: {balance_usdc:.6f} USDC")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_account_info(args):
    """Show account information."""
    client = get_client(args.rpc)
    
    try:
        # Get nonce
        nonce = client.get_nonce_sync(args.address)
        chain_id = client.get_chain_id_sync()
        
        print(f"Address: {args.address}")
        print(f"Nonce: {nonce}")
        print(f"Chain ID: {chain_id}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_deploy(args):
    """Deploy a contract."""
    print(f"Deploying contract with ABI: {args.abi}")
    print("Note: Full deploy requires private key setup.")
    print("Use starknet.py directly with Account class.")
    print(f"RPC: {args.rpc}")


def cmd_call(args):
    """Call a read-only contract function."""
    print(f"Contract: {args.address}")
    print(f"Function: {args.function}")
    print(f"Args: {args.args}")
    print("Note: Full call requires ABI and function selector.")
    print("Use starknet.py directly.")
    print(f"RPC: {args.rpc}")


def cmd_invoke(args):
    """Invoke a contract function."""
    print(f"Invoking contract function: {args.function}")
    print("Note: Full invoke requires private key and Account.")
    print("Use starknet.py directly.")
    print(f"RPC: {args.rpc}")


def main():
    parser = argparse.ArgumentParser(
        description="Starknet.py CLI - Python SDK for Starknet",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3.12 scripts/cli.py balance 0x123...
  python3.12 scripts/cli.py balance-usdc 0x123...
  python3.12 scripts/cli.py account-info 0x123...
  python3.12 scripts/cli.py --network sepolia balance 0x123...
        """
    )
    
    parser.add_argument("--network", "-n", default="mainnet",
                       choices=["mainnet", "sepolia"],
                       help="Network (default: mainnet)")
    parser.add_argument("--rpc", "-r", help="Custom RPC URL")
    
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Balance
    bal_parser = subparsers.add_parser("balance", help="Check ETH balance")
    bal_parser.add_argument("address", help="Account address (0x...)")
    
    # USDC balance
    usdc_parser = subparsers.add_parser("balance-usdc", help="Check USDC balance")
    usdc_parser.add_argument("address", help="Account address (0x...)")
    
    # Account info
    acc_parser = subparsers.add_parser("account-info", help="Account info")
    acc_parser.add_argument("address", help="Account address (0x...)")
    
    # Deploy
    deploy_parser = subparsers.add_parser("deploy", help="Deploy contract")
    deploy_parser.add_argument("--abi", required=True, help="ABI file path")
    
    # Call
    call_parser = subparsers.add_parser("call", help="Call function")
    call_parser.add_argument("address", help="Contract address")
    call_parser.add_argument("function", help="Function name")
    call_parser.add_argument("args", nargs="*", help="Arguments")
    
    # Invoke
    invoke_parser = subparsers.add_parser("invoke", help="Invoke function")
    invoke_parser.add_argument("address", help="Contract address")
    invoke_parser.add_argument("function", help="Function name")
    invoke_parser.add_argument("args", nargs="*", help="Arguments")
    
    args = parser.parse_args()
    
    # Set RPC URL
    if args.rpc:
        rpc_url = args.rpc
    else:
        rpc_url = NETWORKS.get(args.network, NETWORKS["mainnet"])
    
    # Store RPC in args for subcommands
    args.rpc = rpc_url
    
    # Route command
    if args.command == "balance":
        cmd_balance(args)
    elif args.command == "balance-usdc":
        cmd_balance_usdc(args)
    elif args.command == "account-info":
        cmd_account_info(args)
    elif args.command == "deploy":
        cmd_deploy(args)
    elif args.command == "call":
        cmd_call(args)
    elif args.command == "invoke":
        cmd_invoke(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
