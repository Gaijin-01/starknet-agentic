#!/usr/bin/env python3
"""
mcporter skill - MCP server management tool.

Wraps the mcporter CLI for Clawdbot integration.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_mcporter(args: list, config: str = None) -> dict:
    """Execute mcporter command and return structured output."""
    cmd = ["mcporter"]
    if config:
        cmd.extend(["--config", config])
    cmd.extend(args)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout.strip(),
            "error": result.stderr.strip() if result.stderr else None,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out", "returncode": -1}
    except FileNotFoundError:
        return {"success": False, "error": "mcporter not found", "returncode": -1}


def cmd_list(server: str = None, schema: bool = False) -> str:
    """List available MCP servers or tools."""
    args = ["list"]
    if server:
        args.append(server)
        if schema:
            args.append("--schema")
    result = run_mcporter(args)
    if result["success"]:
        return result["output"]
    return f"Error: {result['error']}"


def cmd_call(tool: str, args_str: str = None, json_args: str = None, output: str = "json") -> str:
    """Call an MCP tool."""
    call_args = ["call", tool]
    
    if args_str:
        call_args.append(args_str)
    if json_args:
        call_args.extend(["--args", json_args])
    call_args.extend(["--output", output])
    
    result = run_mcporter(call_args)
    if result["success"]:
        try:
            return json.dumps(json.loads(result["output"]), indent=2)
        except json.JSONDecodeError:
            return result["output"]
    return f"Error: {result['error']}"


def cmd_auth(server: str, reset: bool = False) -> str:
    """Authenticate with an MCP server."""
    args = ["auth", server]
    if reset:
        args.append("--reset")
    result = run_mcporter(args)
    if result["success"]:
        return "Authentication successful"
    return f"Error: {result['error']}"


def cmd_config(action: str, key: str = None, value: str = None) -> str:
    """Manage mcporter configuration."""
    args = ["config", action]
    if key:
        args.append(key)
    if value:
        args.append(value)
    result = run_mcporter(args)
    if result["success"]:
        return result["output"]
    return f"Error: {result['error']}"


def cmd_daemon(action: str) -> str:
    """Control the mcporter daemon."""
    result = run_mcporter(["daemon", action])
    if result["success"]:
        return f"Daemon {action}: OK"
    return f"Error: {result['error']}"


def cmd_generate_cli(server: str = None, command: str = None, output: str = None) -> str:
    """Generate CLI for an MCP server."""
    args = ["generate-cli"]
    if server:
        args.extend(["--server", server])
    if command:
        args.extend(["--command", command])
    if output:
        args.extend(["--output", output])
    
    result = run_mcporter(args)
    if result["success"]:
        return f"CLI generated: {result['output']}"
    return f"Error: {result['error']}"


def cmd_emit_ts(server: str, mode: str = "types") -> str:
    """Emit TypeScript types for an MCP server."""
    args = ["emit-ts", server, "--mode", mode]
    result = run_mcporter(args)
    if result["success"]:
        return result["output"]
    return f"Error: {result['error']}"


def main():
    """Main entry point for mcporter skill."""
    parser = argparse.ArgumentParser(
        description="MCP server management for Clawdbot"
    )
    parser.add_argument(
        "--config",
        help="Path to mcporter config file"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # list
    p_list = subparsers.add_parser("list", help="List MCP servers or tools")
    p_list.add_argument("server", nargs="?", help="Server name (optional)")
    p_list.add_argument("--schema", action="store_true", help="Show tool schema")

    # call
    p_call = subparsers.add_parser("call", help="Call an MCP tool")
    p_call.add_argument("tool", help="Tool selector (server.tool)")
    p_call.add_argument("--args", help="JSON arguments")
    p_call.add_argument("--output", default="json", help="Output format")

    # auth
    p_auth = subparsers.add_parser("auth", help="Authenticate with server")
    p_auth.add_argument("server", help="Server name or URL")
    p_auth.add_argument("--reset", action="store_true", help="Reset authentication")

    # config
    p_config = subparsers.add_parser("config", help="Manage configuration")
    p_config.add_argument("action", choices=["list", "get", "add", "remove", "import"])
    p_config.add_argument("key", nargs="?", help="Config key")
    p_config.add_argument("value", nargs="?", help="Config value")

    # daemon
    p_daemon = subparsers.add_parser("daemon", help="Control daemon")
    p_daemon.add_argument("action", choices=["start", "status", "stop", "restart"])

    # generate-cli
    p_gen = subparsers.add_parser("generate-cli", help="Generate CLI for server")
    p_gen.add_argument("--server", help="Server name")
    p_gen.add_argument("--command", help="Server command URL")
    p_gen.add_argument("--output", help="Output file path")

    # emit-ts
    p_ts = subparsers.add_parser("emit-ts", help="Emit TypeScript types")
    p_ts.add_argument("server", help="Server name")
    p_ts.add_argument("--mode", default="types", choices=["client", "types"])

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    config = getattr(args, "config", None)

    if args.command == "list":
        output = cmd_list(args.server, args.schema)
    elif args.command == "call":
        output = cmd_call(args.tool, args.args, getattr(args, "args", None), args.output)
    elif args.command == "auth":
        output = cmd_auth(args.server, args.reset)
    elif args.command == "config":
        output = cmd_config(args.action, args.key, args.value)
    elif args.command == "daemon":
        output = cmd_daemon(args.action)
    elif args.command == "generate-cli":
        output = cmd_generate_cli(args.server, args.command, args.output)
    elif args.command == "emit-ts":
        output = cmd_emit_ts(args.server, args.mode)
    else:
        output = f"Unknown command: {args.command}"

    print(output)


if __name__ == "__main__":
    main()
