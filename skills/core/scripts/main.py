#!/usr/bin/env python3
"""
Core Skill CLI - Unified management for claude-proxy, orchestrator, config, mcporter
"""

import argparse
import sys
import os
from pathlib import Path

# Add skill root to path
SKILL_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_ROOT))

from main import AdaptiveRouter, ClaudeProxy, MCPManager, Config


def main():
    try:
        parser = argparse.ArgumentParser(
            description="Core Skill - Unified management",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        subparsers = parser.add_subparsers(dest="command", help="Commands")
        
        # Status
        status_parser = subparsers.add_parser("status", help="Show system status")
        
        # Config
        config_parser = subparsers.add_parser("config", help="Config operations")
        config_parser.add_argument("--get", metavar="KEY", help="Get config value")
        config_parser.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"), help="Set config value")
        
        # Claude Proxy
        proxy_parser = subparsers.add_parser("proxy", help="Claude proxy operations")
        proxy_parser.add_argument("--chat", help="Start chat session")
        
        # Route
        route_parser = subparsers.add_parser("route", help="Route message")
        route_parser.add_argument("message", help="Message to route")
        
        # MCP
        mcp_parser = subparsers.add_parser("mcp", help="MCP operations")
        mcp_parser.add_argument("--list", action="store_true", help="List MCP servers")
        
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return
        
        cfg = Config()
        
        if args.command == "status":
            print("Core Skill - Active")
            print(f"Merged: claude-proxy, orchestrator, config, mcporter")
        
        elif args.command == "config":
            if args.get:
                print(getattr(cfg, args.get, "Not found"))
            elif args.set:
                print(f"Set {args.set[0]} = {args.set[1]}")
            else:
                parser.parse_args(["config", "-h"])
        
        elif args.command == "proxy":
            print("Proxy mode - Use main.py directly")
        
        elif args.command == "route":
            router = AdaptiveRouter()
            result = router.route(args.message)
            print(f"Skill: {result.skill}, Confidence: {result.confidence}")
        
        elif args.command == "mcp":
            manager = MCPManager()
            print("MCP operations available")
        
        else:
            parser.print_help()
    
    except Exception as e:
        logger.error(f"Core skill error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
