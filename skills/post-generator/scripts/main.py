#!/usr/bin/env python3
"""
Post Generator Skill - CLI Interface.

Generates social media posts using style profiles.
"""

import sys
import os
import argparse
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from post_generator import PostGenerator


def main():
    parser = argparse.ArgumentParser(
        description="Post Generator - Create social media posts",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Generate post
    gen_parser = subparsers.add_parser("generate", help="Generate a post")
    gen_parser.add_argument("--topic", "-t", required=True, help="Post topic")
    gen_parser.add_argument("--style", "-s", default="default", help="Style profile")
    gen_parser.add_argument("--format", "-f", default="tweet", 
                           choices=["tweet", "thread", "longpost"],
                           help="Post format")
    gen_parser.add_argument("--platform", "-p", default="twitter",
                           choices=["twitter", "thread", "longpost"],
                           help="Target platform")
    
    # Auto-generate
    subparsers.add_parser("auto", help="Auto-generate from trending")
    
    args = parser.parse_args()
    
    if args.command == "generate":
        generator = PostGenerator()
        post = generator.generate(args.topic, style=args.style, format=args.format)
        print(json.dumps({"post": post}, indent=2))
        
    elif args.command == "auto":
        print(json.dumps({"status": "auto mode not implemented"}))
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
