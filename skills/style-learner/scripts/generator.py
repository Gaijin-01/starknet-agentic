#!/usr/bin/env python3
"""
style-learner/generator.py - Content Generator

Generates content matching user's learned style.
"""

import json
import random
from typing import Dict, List, Optional


class ContentGenerator:
    """Generate content in user's style"""
    
    def __init__(self):
        self.default_templates = {
            "gm": [
                "gm {emoji} zk summer loading. execution > narratives. higher 🐺",
                "gm. {topic} vibes today. lfg",
                "gm 🌅 another day of building",
                "gm ser 🐺",
            ],
            "price": [
                "{symbol} ${price} {direction}. {emoji}",
                "{symbol} at ${price}. {sentiment}. patience.",
                "{emoji} {symbol} {price} {direction}",
            ],
            "news": [
                "{headline}. bullish if true. 🔥",
                "just in: {headline}. thoughts?",
                "{headline}\n\n{emoji} {take}",
            ],
            "insight": [
                "hot take: {insight} {emoji}",
                "people sleep on {topic}.\n\n{insight}",
                "unpopular opinion: {insight}",
            ],
            "reply": [
                "this. {emoji}",
                "based {emoji}",
                "ser 🐺",
                "higher",
                "{content} {emoji}",
            ],
            "thread": [
                "🧵 {title}\n\n1/",
                "continuing... {content}\n\n2/",
                "final point: {content}\n\n{emoji} /end",
            ]
        }
    
    def _get_templates(self, content_type: str, profile: Dict) -> List[str]:
        """Get templates from profile or defaults"""
        try:
            templates = profile.get("templates", {}).get(content_type, [])
            if templates:
                return templates
        except:
            pass
        return self.default_templates.get(content_type, ["{content}"])
    
    def _apply_style(self, text: str, profile: Dict) -> str:
        """Apply user's style to generated text"""
        # Add signature emoji if sparse style
        emoji_style = profile.get("persona", {}).get("emoji_style", "sparse")
        
        if emoji_style == "sparse" and "🐺" not in text:
            text = text.rstrip() + " 🐺"
        
        return text
    
    def generate(self, content_type: str, profile: Dict, context: str = "") -> str:
        """Generate content of given type"""
        templates = self._get_templates(content_type, profile)
        template = random.choice(templates)
        
        # Parse context
        topic = context or self._get_random_topic(profile)
        
        # Build template variables
        variables = {
            "emoji": self._get_emoji(profile),
            "topic": topic,
            "content": context,
            "headline": context[:100] if context else "new development",
            "take": "interesting development" if context else "worth watching",
            "insight": context or "the market sleeps",
            "symbol": "STRK",
            "price": "0.07",
            "direction": "down",
            "sentiment": "bearish",
        }
        
        # Generate
        content = template
        for key, value in variables.items():
            content = content.replace(f"{{{key}}}", str(value))
        
        # Apply style
        content = self._apply_style(content, profile)
        
        return content
    
    def _get_emoji(self, profile: Dict) -> str:
        """Get emoji based on user's preferences"""
        emoji_usage = profile.get("vocabulary", {}).get("emoji_usage", {})
        
        if emoji_usage:
            top_emoji = random.choice(list(emoji_usage.keys())[:3])
            return top_emoji
        
        return random.choice(["🔥", "💀", "🐺", "⚡", "👀"])
    
    def _get_random_topic(self, profile: Dict) -> str:
        """Get random topic from profile"""
        topics = profile.get("engagement", {}).get("liked_topics", [])
        
        if not topics:
            topics = ["starknet", "zk", "defi", "l2"]
        
        return random.choice(topics)
    
    def generate_reply(self, original_tweet: str, profile: Dict) -> str:
        """Generate a reply matching user's style"""
        templates = self._get_templates("reply", profile)
        template = random.choice(templates)
        
        # Analyze original for context
        original_lower = original_tweet.lower()
        
        if "gm" in original_lower or "good morning" in original_lower:
            response = "gm ser 🐺"
        elif "?" in original_tweet:
            response = "patience. higher. 🐺"
        elif len(original_tweet) < 50:
            response = "based 🔥"
        else:
            response = template.format(content=original_tweet[:50], emoji=self._get_emoji(profile))
        
        return self._apply_style(response, profile)
    
    def generate_thread(self, title: str, points: List[str], profile: Dict) -> List[str]:
        """Generate a thread from points"""
        thread = []
        
        # Opening tweet
        opening = self.generate("thread", profile, title).format(title=title)
        thread.append(opening)
        
        # Point tweets
        for i, point in enumerate(points, 1):
            tweet = f"{i}/ {point}"
            if i == len(points):
                tweet += f"\n\n🐺 /end"
            thread.append(tweet)
        
        return thread
    
    def optimize_for_algorithm(self, content: str, profile: Dict) -> Dict:
        """Optimize content using x-algorithm scoring"""
        # Simple heuristics based on algorithm knowledge
        optimized = {
            "original": content,
            "suggestions": []
        }
        
        # Length check
        word_count = len(content.split())
        if word_count > 280:
            optimized["suggestions"].append("Content too long - may be truncated")
        
        # Engagement check
        if "?" not in content and content_type != "gm":
            optimized["suggestions"].append("Consider adding a question for engagement")
        
        # Emoji check
        emoji_count = content.count("🐺") + content.count("🔥") + content.count("💀")
        if emoji_count == 0:
            optimized["suggestions"].append("Add an emoji for better engagement")
        
        # Hashtag check
        if "#" in content:
            optimized["suggestions"].append("Consider removing hashtags for cleaner look")
        
        return optimized


if __name__ == "__main__":
    generator = ContentGenerator()
    
    # Test with default profile
    profile = {
        "persona": {"emoji_style": "sparse"},
        "vocabulary": {"emoji_usage": {"🐺": 5, "🔥": 3}},
        "engagement": {"liked_topics": ["starknet", "defi"]}
    }
    
    print("GM:", generator.generate("gm", profile))
    print("News:", generator.generate("news", profile, "Starknet v0.14 released"))
    print("Reply:", generator.generate_reply("gm everyone!", profile))
