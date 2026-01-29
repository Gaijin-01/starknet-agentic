#!/usr/bin/env python3
"""
post_generator.py - Universal post generation skill

Uses config-based templates and persona for any domain
"""

import os
import sys
import json
import logging
import argparse
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Add parent to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "config"))
from config_loader import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================
# VOICE MODIFIERS
# ============================================

VOICE_STYLES = {
    'degen': {
        'caps_words': ['LFG', 'WAGMI', 'NGMI', 'NFA', 'DYOR'],
        'slang': {'good': 'bullish', 'bad': 'bearish', 'increase': 'pump', 'decrease': 'dump'},
        'endings': ['🔥', '💀', 'lfg', 'higher 🐺', 'ser'],
        'case': 'lower'
    },
    'professional': {
        'caps_words': [],
        'slang': {},
        'endings': ['.', ''],
        'case': 'sentence'
    },
    'casual': {
        'caps_words': [],
        'slang': {},
        'endings': ['!', '😊', '👍', ''],
        'case': 'sentence'
    },
    'sarcastic': {
        'caps_words': ['OBVIOUSLY', 'SHOCKING', 'WHO KNEW'],
        'slang': {},
        'endings': ['🙄', '...', ''],
        'case': 'sentence'
    },
    'formal': {
        'caps_words': [],
        'slang': {},
        'endings': ['.'],
        'case': 'title'
    }
}


# ============================================
# POST GENERATOR
# ============================================

class PostGenerator:
    """Universal post generator"""
    
    MAX_LENGTH = 280  # Twitter limit
    
    def __init__(self, cfg: Config = None):
        self.cfg = cfg or Config()
        self.voice = self.cfg.get('persona.voice', 'casual')
        self.style = VOICE_STYLES.get(self.voice, VOICE_STYLES['casual'])
    
    def _apply_case(self, text: str) -> str:
        """Apply case style"""
        case = self.style.get('case', 'sentence')
        
        if case == 'lower':
            # Keep caps words, lowercase rest
            caps = self.style.get('caps_words', [])
            words = text.split()
            result = []
            for w in words:
                if w.upper() in caps:
                    result.append(w.upper())
                else:
                    result.append(w.lower())
            return ' '.join(result)
        
        elif case == 'title':
            return text.title()
        
        else:  # sentence
            return text
    
    def _apply_slang(self, text: str) -> str:
        """Apply slang replacements"""
        slang = self.style.get('slang', {})
        for word, replacement in slang.items():
            text = text.replace(word, replacement)
        return text
    
    def _add_ending(self, text: str) -> str:
        """Add voice-appropriate ending"""
        endings = self.style.get('endings', [''])
        ending = random.choice(endings)
        
        if not text.endswith(('.', '!', '?', '🔥', '💀', '🐺', '👀')):
            text = text.rstrip() + ' ' + ending
        
        return text.strip()
    
    def _truncate(self, text: str) -> str:
        """Truncate to max length"""
        if len(text) <= self.MAX_LENGTH:
            return text
        return text[:self.MAX_LENGTH - 3].rstrip() + '...'
    
    def generate(
        self,
        post_type: str,
        **kwargs
    ) -> str:
        """
        Generate post of given type
        
        Args:
            post_type: gm, price, news, insight, engagement
            **kwargs: Template variables
        
        Returns:
            Generated post text
        """
        # Get template
        template = self.cfg.get_template(post_type)
        
        # Add default variables
        defaults = {
            'emoji': self.cfg.get_random_emoji(),
            'topic': self.cfg.get_random_topic(),
            'action': random.choice(['building', 'buying', 'researching', 'testing']),
            'adjective': random.choice(['huge', 'massive', 'interesting', 'wild', 'bullish'])
        }
        defaults.update(kwargs)
        
        # Format template
        try:
            post = template.format(**defaults)
        except KeyError as e:
            logger.warning(f"Missing template variable: {e}")
            post = template
        
        # Apply voice modifications
        post = self._apply_slang(post)
        post = self._apply_case(post)
        post = self._add_ending(post)
        post = self._truncate(post)
        
        return post
    
    def generate_gm(self) -> str:
        """Generate GM post"""
        return self.generate('gm')
    
    def generate_price(
        self,
        asset: str,
        price: float,
        change: float = 0
    ) -> str:
        """Generate price post"""
        direction = '📈' if change > 0 else '📉'
        sentiment = 'accumulation zone' if change < 0 else 'momentum building'
        
        # Format price
        if price < 0.01:
            price_str = f"{price:.6f}"
        elif price < 1:
            price_str = f"{price:.4f}"
        elif price < 100:
            price_str = f"{price:.2f}"
        else:
            price_str = f"{price:,.0f}"
        
        return self.generate(
            'price',
            coin=asset,
            symbol=asset,
            price=price_str,
            direction=direction,
            sentiment=sentiment,
            change=f"{change:+.1f}%"
        )
    
    def generate_news(
        self,
        headline: str,
        take: Optional[str] = None
    ) -> str:
        """Generate news post"""
        return self.generate(
            'news',
            headline=headline,
            take=take or 'thoughts?'
        )
    
    def generate_insight(
        self,
        insight: str,
        topic: Optional[str] = None
    ) -> str:
        """Generate insight/opinion post"""
        return self.generate(
            'insight',
            insight=insight,
            topic=topic or self.cfg.get_random_topic()
        )
    
    def generate_custom(self, text: str) -> str:
        """Apply voice to custom text"""
        post = self._apply_slang(text)
        post = self._apply_case(post)
        post = self._truncate(post)
        return post


# ============================================
# QUEUE MANAGEMENT
# ============================================

def save_to_queue(post: str, cfg: Config) -> Path:
    """Save post to queue directory"""
    queue_dir = Path(cfg.get('queue.base_dir', '~/clawd/post_queue'))
    ready_dir = queue_dir / cfg.get('queue.subdirs.ready', 'ready')
    ready_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"post_{timestamp}.txt"
    filepath = ready_dir / filename
    
    with open(filepath, 'w') as f:
        f.write(post)
    
    logger.info(f"Saved to queue: {filepath}")
    return filepath


# ============================================
# CLI
# ============================================

def main():
    parser = argparse.ArgumentParser(description="Universal post generator")
    parser.add_argument("--type", "-t", choices=['gm', 'price', 'news', 'insight', 'engagement'],
                        help="Post type")
    parser.add_argument("--custom", "-c", help="Custom text to process")
    parser.add_argument("--headline", help="News headline (for news type)")
    parser.add_argument("--take", help="Your take on news")
    parser.add_argument("--insight", help="Insight text (for insight type)")
    parser.add_argument("--asset", help="Asset symbol (for price type)")
    parser.add_argument("--price", type=float, help="Price value")
    parser.add_argument("--change", type=float, default=0, help="24h change %")
    parser.add_argument("--save", "-s", action="store_true", help="Save to queue")
    parser.add_argument("--count", "-n", type=int, default=1, help="Number of posts to generate")
    
    args = parser.parse_args()
    
    if not args.type and not args.custom:
        parser.error("Either --type or --custom required")
    
    cfg = Config()
    gen = PostGenerator(cfg)
    
    posts = []
    
    for _ in range(args.count):
        if args.custom:
            post = gen.generate_custom(args.custom)
        
        elif args.type == 'gm':
            post = gen.generate_gm()
        
        elif args.type == 'price':
            if not args.asset:
                parser.error("--asset required for price type")
            post = gen.generate_price(
                asset=args.asset,
                price=args.price or 0,
                change=args.change
            )
        
        elif args.type == 'news':
            if not args.headline:
                parser.error("--headline required for news type")
            post = gen.generate_news(
                headline=args.headline,
                take=args.take
            )
        
        elif args.type == 'insight':
            if not args.insight:
                parser.error("--insight required for insight type")
            post = gen.generate_insight(insight=args.insight)
        
        elif args.type == 'engagement':
            post = gen.generate('engagement')
        
        else:
            post = gen.generate(args.type)
        
        posts.append(post)
        
        if args.save:
            save_to_queue(post, cfg)
    
    # Output
    for post in posts:
        print(post)
        print(f"[{len(post)} chars]")
        print()


if __name__ == "__main__":
    main()
