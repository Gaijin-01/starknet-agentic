#!/usr/bin/env python3
"""
queue_manager.py - Universal file queue manager

100% domain-agnostic. Manages files in queue directories.
"""

import os
import sys
import json
import shutil
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Add parent to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "config"))
from config_loader import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================
# QUEUE MANAGER
# ============================================

class QueueManager:
    """Universal queue manager"""
    
    STATES = ['ready', 'posted', 'failed', 'drafts']
    
    def __init__(self, cfg: Config = None):
        self.cfg = cfg or Config()
        self.base_dir = Path(self.cfg.get('queue.base_dir', '~/clawd/post_queue')).expanduser()
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        """Create queue directories if missing"""
        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.error(f"Failed to create base dir {self.base_dir}: {e}")
            raise
        
        for state in self.STATES:
            try:
                subdir = self.cfg.get(f'queue.subdirs.{state}', state)
                (self.base_dir / subdir).mkdir(parents=True, exist_ok=True)
            except OSError as e:
                logger.error(f"Failed to create state dir {state}: {e}")
    
    def _get_dir(self, state: str) -> Path:
        """Get directory for state"""
        subdir = self.cfg.get(f'queue.subdirs.{state}', state)
        return self.base_dir / subdir
    
    def _get_file_info(self, filepath: Path) -> Dict:
        """Get file metadata"""
        try:
            stat = filepath.stat()
            content = filepath.read_text()[:100] if filepath.suffix == '.txt' else ''
            
            return {
                'name': filepath.name,
                'path': str(filepath),
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'preview': content.strip()[:50] + '...' if len(content) > 50 else content.strip()
            }
        except OSError as e:
            logger.error(f"Failed to get info for {filepath}: {e}")
            return {
                'name': filepath.name,
                'path': str(filepath),
                'size': 0,
                'error': str(e)
            }
    
    # ============================================
    # OPERATIONS
    # ============================================
    
    def list(self, state: str = 'ready', all_states: bool = False) -> Dict[str, List[Dict]]:
        """List queue contents"""
        result = {}
        
        states = self.STATES if all_states else [state]
        
        for s in states:
            dir_path = self._get_dir(s)
            files = []
            
            try:
                if dir_path.exists():
                    for f in sorted(dir_path.iterdir()):
                        if f.is_file() and not f.name.startswith('.'):
                            files.append(self._get_file_info(f))
            except OSError as e:
                logger.error(f"Error reading {s}: {e}")
            
            result[s] = files
        
        return result
    
    def add(self, content: str, filename: Optional[str] = None) -> Path:
        """Add content to ready queue"""
        ready_dir = self._get_dir('ready')
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"post_{timestamp}.txt"
        
        filepath = ready_dir / filename
        
        try:
            filepath.write_text(content)
            logger.info(f"Added to queue: {filepath}")
            return filepath
        except OSError as e:
            logger.error(f"Failed to write {filepath}: {e}")
            raise
    
    def move(self, filename: str, to_state: str, from_state: str = 'ready') -> bool:
        """Move file between states"""
        if to_state not in self.STATES:
            logger.error(f"Invalid state: {to_state}")
            return False
        
        # Find file
        src = None
        if from_state:
            src = self._get_dir(from_state) / filename
            if not src.exists():
                src = None
        
        # Search all states if not found
        if not src:
            for s in self.STATES:
                candidate = self._get_dir(s) / filename
                if candidate.exists():
                    src = candidate
                    break
        
        if not src or not src.exists():
            logger.error(f"File not found: {filename}")
            return False
        
        try:
            dst = self._get_dir(to_state) / filename
            shutil.move(str(src), str(dst))
            logger.info(f"Moved {filename}: {src.parent.name} → {to_state}")
            return True
        except OSError as e:
            logger.error(f"Failed to move {filename}: {e}")
            return False
    
    def clear(self, state: str = 'posted', older_than_days: int = 7) -> int:
        """Clear old files from state"""
        dir_path = self._get_dir(state)
        cutoff = datetime.now() - timedelta(days=older_than_days)
        cleared = 0
        
        try:
            for f in dir_path.iterdir():
                if f.is_file():
                    try:
                        mtime = datetime.fromtimestamp(f.stat().st_mtime)
                        if mtime < cutoff:
                            f.unlink()
                            cleared += 1
                    except OSError:
                        continue
        except OSError as e:
            logger.error(f"Error clearing {state}: {e}")
        
        logger.info(f"Cleared {cleared} files from {state} (older than {older_than_days} days)")
        return cleared
    
    def stats(self) -> Dict:
        """Get queue statistics"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'base_dir': str(self.base_dir),
            'states': {}
        }
        
        total_size = 0
        
        for state in self.STATES:
            dir_path = self._get_dir(state)
            files = list(dir_path.glob('*')) if dir_path.exists() else []
            files = [f for f in files if f.is_file() and not f.name.startswith('.')]
            
            state_size = sum(f.stat().st_size for f in files)
            total_size += state_size
            
            oldest = None
            newest = None
            if files:
                sorted_files = sorted(files, key=lambda x: x.stat().st_mtime)
                oldest = datetime.fromtimestamp(sorted_files[0].stat().st_mtime).isoformat()
                newest = datetime.fromtimestamp(sorted_files[-1].stat().st_mtime).isoformat()
            
            result['states'][state] = {
                'count': len(files),
                'size_bytes': state_size,
                'oldest': oldest,
                'newest': newest
            }
        
        result['total_files'] = sum(s['count'] for s in result['states'].values())
        result['total_size_bytes'] = total_size
        
        return result
    
    def get_next(self, state: str = 'ready') -> Optional[Dict]:
        """Get oldest file from state (FIFO)"""
        dir_path = self._get_dir(state)
        
        files = list(dir_path.glob('*'))
        files = [f for f in files if f.is_file() and not f.name.startswith('.')]
        
        if not files:
            return None
        
        oldest = min(files, key=lambda x: x.stat().st_mtime)
        
        info = self._get_file_info(oldest)
        info['content'] = oldest.read_text() if oldest.suffix == '.txt' else None
        
        return info
    
    def peek(self, state: str = 'ready', count: int = 5) -> List[Dict]:
        """Peek at top N files from state"""
        dir_path = self._get_dir(state)
        
        files = list(dir_path.glob('*'))
        files = [f for f in files if f.is_file() and not f.name.startswith('.')]
        files = sorted(files, key=lambda x: x.stat().st_mtime)[:count]
        
        result = []
        for f in files:
            info = self._get_file_info(f)
            info['content'] = f.read_text() if f.suffix == '.txt' else None
            result.append(info)
        
        return result


# ============================================
# CLI
# ============================================

def main():
    parser = argparse.ArgumentParser(description="Universal queue manager")
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # List
    list_p = subparsers.add_parser('list', help='List queue contents')
    list_p.add_argument('--state', '-s', default='ready', choices=QueueManager.STATES)
    list_p.add_argument('--all', '-a', action='store_true', help='List all states')
    
    # Add
    add_p = subparsers.add_parser('add', help='Add content to queue')
    add_p.add_argument('--content', '-c', required=True, help='Content to add')
    add_p.add_argument('--filename', '-f', help='Optional filename')
    
    # Move
    move_p = subparsers.add_parser('move', help='Move file between states')
    move_p.add_argument('--file', '-f', required=True, help='Filename to move')
    move_p.add_argument('--to', '-t', required=True, choices=QueueManager.STATES)
    move_p.add_argument('--from', dest='from_state', default='ready')
    
    # Clear
    clear_p = subparsers.add_parser('clear', help='Clear old files')
    clear_p.add_argument('--state', '-s', default='posted', choices=QueueManager.STATES)
    clear_p.add_argument('--older-than', '-d', type=int, default=7, help='Days')
    
    # Stats
    subparsers.add_parser('stats', help='Queue statistics')
    
    # Next
    next_p = subparsers.add_parser('next', help='Get next item (FIFO)')
    next_p.add_argument('--state', '-s', default='ready', choices=QueueManager.STATES)
    
    # Peek
    peek_p = subparsers.add_parser('peek', help='Peek at queue')
    peek_p.add_argument('--state', '-s', default='ready', choices=QueueManager.STATES)
    peek_p.add_argument('--count', '-n', type=int, default=5)
    
    args = parser.parse_args()
    
    cfg = Config()
    qm = QueueManager(cfg)
    
    if args.command == 'list':
        result = qm.list(state=args.state, all_states=args.all)
        
        for state, files in result.items():
            print(f"\n📁 {state.upper()} ({len(files)} files)")
            print("-" * 40)
            for f in files:
                print(f"  {f['name']}")
                if f['preview']:
                    print(f"    └─ {f['preview']}")
    
    elif args.command == 'add':
        path = qm.add(args.content, args.filename)
        print(f"✅ Added: {path}")
    
    elif args.command == 'move':
        success = qm.move(args.file, args.to, args.from_state)
        if success:
            print(f"✅ Moved {args.file} → {args.to}")
        else:
            print(f"❌ Failed to move {args.file}")
            sys.exit(1)
    
    elif args.command == 'clear':
        count = qm.clear(args.state, args.older_than)
        print(f"🗑️  Cleared {count} files from {args.state}")
    
    elif args.command == 'stats':
        stats = qm.stats()
        print(f"\n📊 QUEUE STATS")
        print(f"Base: {stats['base_dir']}")
        print(f"Total: {stats['total_files']} files ({stats['total_size_bytes']} bytes)")
        print()
        for state, info in stats['states'].items():
            print(f"  {state}: {info['count']} files")
    
    elif args.command == 'next':
        item = qm.get_next(args.state)
        if item:
            print(f"📄 {item['name']}")
            if item.get('content'):
                print(f"\n{item['content']}")
        else:
            print(f"Queue '{args.state}' is empty")
    
    elif args.command == 'peek':
        items = qm.peek(args.state, args.count)
        print(f"\n👀 Top {len(items)} in {args.state}:")
        for i, item in enumerate(items, 1):
            print(f"\n{i}. {item['name']}")
            if item.get('content'):
                print(f"   {item['content'][:100]}...")


if __name__ == "__main__":
    main()
