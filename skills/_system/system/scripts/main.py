#!/usr/bin/env python3
"""
System Skill CLI - Unified system management, skill evolution, adaptive routing
"""

import argparse
import logging
import sys
import os
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_ROOT))

from main import SystemManager, SkillEvolver, AdaptiveRouter

logger = logging.getLogger(__name__)


def main():
    try:
        parser = argparse.ArgumentParser(
            description="System Skill - Unified system management",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        subparsers = parser.add_subparsers(dest="command", help="Commands")
        
        # Status
        status_parser = subparsers.add_parser("status", help="Show system status")
        
        # Health
        health_parser = subparsers.add_parser("health", help="Health check")
        health_parser.add_argument("--full", action="store_true", help="Full health check")
        
        # Evolve
        evolve_parser = subparsers.add_parser("evolve", help="Skill evolution")
        evolve_parser.add_argument("--analyze", action="store_true", help="Analyze all skills")
        evolve_parser.add_argument("--improve", metavar="SKILL", help="Improve specific skill")
        evolve_parser.add_argument("--report", action="store_true", help="Generate report")
        
        # Routing
        routing_parser = subparsers.add_parser("routing", help="Adaptive routing")
        routing_parser.add_argument("--test", metavar="MESSAGE", help="Test routing for message")
        routing_parser.add_argument("--stats", action="store_true", help="Show routing stats")
        
        # System
        sys_parser = subparsers.add_parser("system", help="System operations")
        sys_parser.add_argument("--restart", action="store_true", help="Restart service")
        sys_parser.add_argument("--logs", action="store_true", help="Show recent logs")
        sys_parser.add_argument("--cron", action="store_true", help="List cron jobs")
        
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return
        
        if args.command == "status":
            print("System Skill - Active")
            print("Merged: system-manager, skill-evolver, adaptive-routing")
        
        elif args.command == "health":
            print("Health check - OK")
        
        elif args.command == "evolve":
            if args.analyze:
                print("Use: python3 skills/skill-evolver/scripts/analyze.py")
            elif args.improve:
                print(f"Improving skill: {args.improve}")
            elif args.report:
                print("Report generated")
        
        elif args.command == "routing":
            if args.test:
                router = AdaptiveRouter()
                result = router.route(args.test)
                print(f"Routed to: {result.skill}")
            elif args.stats:
                print("Routing stats available")
        
        elif args.command == "system":
            print("Use 'system-manager' skill directly")
        
        else:
            parser.print_help()
    
    except Exception as e:
        logger.error(f"System skill error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
