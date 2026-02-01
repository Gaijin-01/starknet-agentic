#!/usr/bin/env python3.12
"""
Starknet.py CLI - Main entry point for Starknet operations.
"""

import argparse
import sys
import os

# Ensure python3.12 is available for starknet-py
PYTHON_BIN = "/usr/bin/python3.12"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    parser = argparse.ArgumentParser(
        description="Starknet.py - Python SDK for Starknet",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--network", "-n", default="mainnet",
                       choices=["mainnet", "sepolia"],
                       help="Starknet network (default: mainnet)")
    parser.add_argument("--rpc", "-r", help="Custom RPC URL")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Balance command
    subparsers.add_parser("balance", help="Check account balance")
    subparsers.add_parser("balance-usdc", help="Check USDC balance")
    
    # Account commands
    subparsers.add_parser("account-info", help="Show account details")
    
    # Contract commands
    deploy_parser = subparsers.add_parser("deploy", help="Deploy contract")
    deploy_parser.add_argument("--abi", required=True, help="ABI file path")
    deploy_parser.add_argument("--constructor", default="", help="Constructor args")
    
    call_parser = subparsers.add_parser("call", help="Call contract function")
    call_parser.add_argument("--address", required=True, help="Contract address")
    call_parser.add_argument("--function", required=True, help="Function name")
    call_parser.add_argument("--args", default="", help="Function arguments (comma-separated)")
    
    invoke_parser = subparsers.add_parser("invoke", help="Invoke contract function")
    invoke_parser.add_argument("--address", required=True, help="Contract address")
    invoke_parser.add_argument("--function", required=True, help="Function name")
    invoke_parser.add_argument("--args", default="", help="Function arguments (comma-separated)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Build command
    cmd = [PYTHON_BIN, f"{SCRIPT_DIR}/cli.py", "--network", args.network]
    if args.rpc:
        cmd.extend(["--rpc", args.rpc])
    cmd.append(args.command)
    
    if hasattr(args, "abi"):
        cmd.extend(["--abi", args.abi])
    if hasattr(args, "address"):
        cmd.extend(["--address", args.address])
    if hasattr(args, "function"):
        cmd.extend(["--function", args.function])
    if hasattr(args, "args") and args.args:
        cmd.extend(["--args", args.args])
    
    os.execv(PYTHON_BIN, cmd)


if __name__ == "__main__":
    main()
