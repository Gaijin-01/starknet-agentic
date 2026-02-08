#!/usr/bin/env python3
"""
Session Logs Analyzer
Search and analyze session logs using jq.
"""

import argparse
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DEFAULT_LOG_DIR = Path.home() / ".openclaw" / "agents" / "main" / "sessions"


def search_logs(pattern: str, log_dir: str = None, limit: int = 100):
    """Search session logs for pattern"""
    log_path = Path(log_dir) if log_dir else DEFAULT_LOG_DIR
    
    if not log_path.exists():
        logger.error(f"Log directory not found: {log_path}")
        return
    
    try:
        import glob
        files = sorted(log_path.glob("*.jsonl"), reverse=True)[:limit]
        
        matches = []
        for f in files:
            try:
                with open(f) as fp:
                    content = fp.read()
                    if pattern in content:
                        matches.append((f.name, content))
            except IOError as e:
                logger.warning(f"Failed to read {f.name}: {e}")
                continue
        
        logger.info(f"Found {len(matches)} matches for '{pattern}'")
        return matches
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return []


def list_sessions(log_dir: str = None, limit: int = 20):
    """List recent session files"""
    log_path = Path(log_dir) if log_dir else DEFAULT_LOG_DIR
    
    if not log_path.exists():
        logger.error(f"Log directory not found: {log_path}")
        return
    
    try:
        files = sorted(log_path.glob("*.jsonl"), reverse=True)[:limit]
        logger.info(f"Sessions in {log_path}:")
        for f in files:
            size = f.stat().st_size
            logger.info(f"  {f.name} ({size} bytes)")
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")


def main():
    parser = argparse.ArgumentParser(description='📋 Session Logs Analyzer')
    parser.add_argument('--dir', '-d', help='Log directory')
    parser.add_argument('--limit', '-l', type=int, default=20, help='Limit results')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search logs')
    search_parser.add_argument('pattern', help='Search pattern')
    
    # List command
    subparsers.add_parser('list', help='List recent sessions')
    
    args = parser.parse_args()
    
    try:
        if args.command == 'search':
            search_logs(args.pattern, args.dir, args.limit)
        elif args.command == 'list':
            list_sessions(args.dir, args.limit)
        else:
            parser.print_help()
    except Exception as e:
        logger.error(f"Command failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
