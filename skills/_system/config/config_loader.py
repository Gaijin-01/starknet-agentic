#!/usr/bin/env python3
"""
config_loader.py - Universal config access for all skills

Usage:
    from config_loader import Config
    
    cfg = Config()
    print(cfg.persona.name)
    print(cfg.apis.search.provider)
    print(cfg.get_template('gm'))
"""

import os
import yaml
import random
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# ============================================
# CONFIG PATH RESOLUTION
# ============================================

def find_config() -> Path:
    """Find config.yaml in standard locations"""
    search_paths = [
        Path(__file__).parent.parent / "config" / "config.yaml",
        Path.home() / "clawd" / "config.yaml",
        Path.home() / "clawdbot" / "config.yaml",
        Path("/home/claude/universal-skills/config/config.yaml"),
        Path("config.yaml"),
    ]
    
    for p in search_paths:
        if p.exists():
            return p
    
    raise FileNotFoundError(f"config.yaml not found in: {search_paths}")


# ============================================
# NESTED DICT ACCESS
# ============================================

class DotDict(dict):
    """Dict with dot notation access"""
    
    def __getattr__(self, key):
        try:
            value = self[key]
            if isinstance(value, dict):
                return DotDict(value)
            return value
        except KeyError:
            raise AttributeError(f"No attribute '{key}'")
    
    def __setattr__(self, key, value):
        self[key] = value
    
    def get_nested(self, path: str, default=None):
        """Get nested value: 'apis.search.provider'"""
        keys = path.split('.')
        value = self
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value


# ============================================
# MAIN CONFIG CLASS
# ============================================

class Config:
    """Universal config manager"""
    
    _instance = None
    _config: DotDict = None
    
    def __new__(cls, config_path: Optional[Path] = None):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load(config_path)
        return cls._instance
    
    def _load(self, config_path: Optional[Path] = None):
        """Load config from YAML"""
        path = config_path or find_config()
        
        with open(path) as f:
            raw = yaml.safe_load(f)
        
        self._config = DotDict(raw)
        self._expand_paths()
    
    def _expand_paths(self):
        """Expand ~ in paths"""
        if 'queue' in self._config:
            bd = self._config['queue'].get('base_dir', '')
            self._config['queue']['base_dir'] = os.path.expanduser(bd)
        
        if 'memory' in self._config:
            bd = self._config['memory'].get('base_dir', '')
            self._config['memory']['base_dir'] = os.path.expanduser(bd)
    
    def reload(self, config_path: Optional[Path] = None):
        """Force reload config"""
        self._load(config_path)
    
    # ============================================
    # PROPERTY ACCESS
    # ============================================
    
    @property
    def bot(self) -> DotDict:
        return DotDict(self._config.get('bot', {}))
    
    @property
    def persona(self) -> DotDict:
        return DotDict(self._config.get('persona', {}))
    
    @property
    def topics(self) -> DotDict:
        return DotDict(self._config.get('topics', {}))
    
    @property
    def templates(self) -> DotDict:
        return DotDict(self._config.get('templates', {}))
    
    @property
    def apis(self) -> DotDict:
        return DotDict(self._config.get('apis', {}))
    
    @property
    def assets(self) -> DotDict:
        return DotDict(self._config.get('assets', {}))
    
    @property
    def queue(self) -> DotDict:
        return DotDict(self._config.get('queue', {}))
    
    @property
    def memory(self) -> DotDict:
        return DotDict(self._config.get('memory', {}))
    
    @property
    def schedule(self) -> DotDict:
        return DotDict(self._config.get('schedule', {}))
    
    @property
    def engagement(self) -> DotDict:
        return DotDict(self._config.get('engagement', {}))
    
    @property
    def rate_limits(self) -> DotDict:
        return DotDict(self._config.get('rate_limits', {}))
    
    # ============================================
    # HELPER METHODS
    # ============================================
    
    def get(self, path: str, default=None):
        """Get nested value by path: config.get('apis.search.provider')"""
        return self._config.get_nested(path, default)
    
    def get_template(self, template_type: str) -> str:
        """Get random template of given type"""
        templates = self._config.get('templates', {}).get(template_type, [])
        if not templates:
            return "{content}"
        return random.choice(templates)
    
    def get_asset(self, symbol: str) -> Optional[Dict]:
        """Get asset config by symbol"""
        assets = self._config.get('assets', {})
        
        # Check all asset types
        for asset_type, items in assets.items():
            if isinstance(items, list):
                for item in items:
                    if item.get('symbol', '').upper() == symbol.upper():
                        return item
                    if item.get('id', '').lower() == symbol.lower():
                        return item
        return None
    
    def get_api_key(self, api_name: str) -> Optional[str]:
        """Get API key from environment"""
        api_cfg = self._config.get('apis', {}).get(api_name, {})
        env_key = api_cfg.get('env_key')
        
        if env_key:
            return os.environ.get(env_key)
        return None
    
    def get_random_topic(self, primary_only: bool = False) -> str:
        """Get random topic"""
        topics = self._config.get('topics', {})
        pool = topics.get('primary', [])
        
        if not primary_only:
            pool = pool + topics.get('secondary', [])
        
        return random.choice(pool) if pool else "general"
    
    def get_random_emoji(self) -> str:
        """Get random emoji based on persona"""
        # Default emojis if not specified
        default = ["🔥", "💀", "⚡", "🚀", "👀", "🫡", "💪", "🐺"]
        
        # Could be extended to read from persona config
        return random.choice(default)
    
    def is_active_hour(self) -> bool:
        """Check if current time is within active hours"""
        from datetime import datetime
        import pytz
        
        schedule = self._config.get('schedule', {})
        tz_name = schedule.get('timezone', 'UTC')
        active = schedule.get('active_hours', {})
        
        if not active:
            return True
        
        try:
            tz = pytz.timezone(tz_name)
            now = datetime.now(tz)
            current_time = now.strftime('%H:%M')
            
            start = active.get('start', '00:00')
            end = active.get('end', '23:59')
            
            return start <= current_time <= end
        except:
            return True
    
    def to_dict(self) -> Dict:
        """Export config as dict"""
        return dict(self._config)


# ============================================
# CLI
# ============================================

if __name__ == "__main__":
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Config loader utility")
    parser.add_argument("--get", help="Get config value by path (e.g., apis.search.provider)")
    parser.add_argument("--dump", action="store_true", help="Dump full config as JSON")
    parser.add_argument("--template", help="Get random template by type")
    parser.add_argument("--asset", help="Get asset config by symbol")
    
    args = parser.parse_args()
    cfg = Config()
    
    if args.get:
        value = cfg.get(args.get)
        print(value)
    
    elif args.dump:
        print(json.dumps(cfg.to_dict(), indent=2))
    
    elif args.template:
        print(cfg.get_template(args.template))
    
    elif args.asset:
        asset = cfg.get_asset(args.asset)
        print(json.dumps(asset, indent=2) if asset else "Not found")
    
    else:
        # Demo
        print(f"Bot: {cfg.bot.name}")
        print(f"Persona: {cfg.persona.name}")
        print(f"Voice: {cfg.persona.voice}")
        print(f"Search API: {cfg.apis.search.provider}")
        print(f"Price API: {cfg.apis.prices.provider}")
        print(f"\nRandom GM template:")
        print(cfg.get_template('gm'))
