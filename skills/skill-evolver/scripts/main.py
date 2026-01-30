#!/usr/bin/env python3
"""
Skill Evolver - CLI Interface.

Analyzes and improves skills.
"""

import sys
import os
import argparse
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyze import SkillAnalyzer
from evolve import SkillEvolver


def main():
    parser = argparse.ArgumentParser(
        description="Skill Evolver - Analyze and improve skills",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a skill")
    analyze_parser.add_argument("--skill", "-s", required=True, help="Skill name")
    analyze_parser.add_argument("--output", "-o", default="report", 
                               choices=["report", "json", "metrics"],
                               help="Output format")
    
    # Evolve
    evolve_parser = subparsers.add_parser("evolve", help="Improve a skill")
    evolve_parser.add_argument("--skill", "-s", required=True)
    evolve_parser.add_argument("--fix", action="store_true", 
                              help="Apply fixes automatically")
    
    # List
    subparsers.add_parser("list", help="List all skills")
    
    args = parser.parse_args()
    
    if args.command == "analyze":
        analyzer = SkillAnalyzer()
        results = analyzer.analyze_skill(args.skill)
        if args.output == "json":
            print(json.dumps(results, indent=2, default=str))
        else:
            print(f"Analysis for {args.skill}:")
            print(results)
            
    elif args.command == "evolve":
        evolver = SkillEvolver()
        result = evolver.evolve_skill(args.skill, auto_fix=args.fix)
        print(json.dumps(result, indent=2, default=str))
        
    elif args.command == "list":
        skills = SkillAnalyzer().list_skills()
        print(json.dumps(skills, indent=2))
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
