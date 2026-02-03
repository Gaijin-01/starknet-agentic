#!/usr/bin/env python3
"""
CLI Interface for Adaptive Routing Skill.
Provides command-line tools for routing testing and management.
"""

#!/usr/bin/env python3
"""Adaptive routing skill CLI interface."""

import sys
import json
import argparse
from typing import Optional

# Handle both relative and absolute imports
try:
    from .router import AdaptiveRouter, SkillType, RoutingResult
except ImportError:
    from router import AdaptiveRouter, SkillType, RoutingResult


def print_result(result: RoutingResult):
    """Print routing result in human-readable format."""
    print("\n" + "=" * 60)
    print("ROUTING RESULT")
    print("=" * 60)
    print(f"Skill:       {result.skill.value}")
    print(f"Confidence:  {result.confidence:.2%}")
    print(f"Params:      {json.dumps(result.params, indent=4, ensure_ascii=False)}")
    print(f"Fallback:    {result.fallback.value if result.fallback else 'None'}")
    print(f"Reasoning:   {result.reasoning}")
    print(f"Timestamp:   {result.timestamp}")
    print("=" * 60)


def cmd_route(args):
    """Route a single message."""
    router = AdaptiveRouter()
    result = router.route(args.message)
    print_result(result)


def cmd_batch(args):
    """Route multiple messages from file or stdin."""
    router = AdaptiveRouter()
    messages = []
    
    if args.file:
        with open(args.file, 'r') as f:
            messages = [line.strip() for line in f if line.strip()]
    else:
        # Read from stdin
        for line in sys.stdin:
            line = line.strip()
            if line:
                messages.append(line)
    
    if not messages:
        print("No messages to route")
        return
    
    print(f"\nRouting {len(messages)} messages...\n")
    
    results = router.route_batch(messages)
    
    for i, (msg, result) in enumerate(zip(messages, results), 1):
        print(f"[{i}] Message: {msg[:50]}...")
        print(f"    → {result.skill.value} (conf: {result.confidence:.2%})")
        print()


def cmd_list_skills(args):
    """List all available skills."""
    skills = list(SkillType)
    
    print("\nAVAILABLE SKILLS")
    print("=" * 40)
    for skill in skills:
        print(f"  • {skill.value}")
    print("=" * 40)


def cmd_config(args):
    """Show router configuration."""
    router = AdaptiveRouter()
    
    print("\nROUTER CONFIG")
    print("=" * 40)
    print(f"Skills configured: {len(router.config)}")
    print(f"Priority range:    0-10")
    print("=" * 40)


def cmd_interactive(args):
    """Interactive routing mode."""
    router = AdaptiveRouter()
    
    print("\nADAPTIVE ROUTING — INTERACTIVE MODE")
    print("Type 'quit' or 'exit' to stop.\n")
    
    while True:
        try:
            message = input("Message: ").strip()
            if message.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            if not message:
                continue
            
            result = router.route(message)
            print_result(result)
            print()
            
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Adaptive Routing Skill CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Route a single message
  python scripts/cli.py route "what's the price of $BTC"
  
  # Batch route from file
  python scripts/cli.py batch --file messages.txt
  
  # Interactive mode
  python scripts/cli.py interactive
  
  # List all skills
  python scripts/cli.py skills
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Route command
    route_parser = subparsers.add_parser("route", help="Route a single message")
    route_parser.add_argument("message", help="Message to route")
    
    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Route multiple messages")
    batch_parser.add_argument("-f", "--file", help="File with messages (one per line)")
    
    # List skills
    subparsers.add_parser("skills", help="List all available skills")
    
    # Config
    subparsers.add_parser("config", help="Show router configuration")
    
    # Interactive
    subparsers.add_parser("interactive", help="Interactive routing mode")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    commands = {
        "route": cmd_route,
        "batch": cmd_batch,
        "skills": cmd_list_skills,
        "config": cmd_config,
        "interactive": cmd_interactive,
    }
    
    commands[args.command](args)


if __name__ == "__main__":
    main()
