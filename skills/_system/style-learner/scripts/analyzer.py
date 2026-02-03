#!/usr/bin/env python3
"""
style-learner/analyzer.py - Style Profile Builder

Analyzes tweets and engagement to build user style profile.
"""

import json
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class StyleAnalyzer:
    """Build style profile from collected data"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
    
    def load_observations(self, days: int = 30) -> List[Dict]:
        """Load all observation files"""
        observations = []
        obs_dir = self.data_dir / "observations"
        
        if not obs_dir.exists():
            return observations
        
        for f in sorted(obs_dir.glob("*.jsonl"), reverse=True)[:days]:
            with open(f) as file:
                for line in file:
                    if line.strip():
                        observations.append(json.loads(line))
        
        return observations
    
    def extract_words(self, text: str) -> List[str]:
        """Extract meaningful words from text"""
        # Remove URLs, mentions, clean text
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#(\w+)', r'\1', text)
        
        # Split and filter
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter common words
        stopwords = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 
                     'can', 'had', 'her', 'was', 'one', 'our', 'out', 'has',
                     'have', 'been', 'this', 'that', 'with', 'they', 'from',
                     'will', 'would', 'there', 'their', 'what', 'about'}
        
        return [w for w in words if w not in stopwords]
    
    def analyze_vocabulary(self, texts: List[str]) -> Dict:
        """Analyze vocabulary from texts"""
        all_words = []
        for text in texts:
            all_words.extend(self.extract_words(str(text)))
        
        word_counts = Counter(all_words)
        
        # Signature phrases (2-4 word combinations)
        signatures = []
        for text in texts[:50]:  # Limit for performance
            text_lower = str(text).lower()
            # Common patterns
            if "higher" in text_lower:
                signatures.append("higher")
            if "execution" in text_lower:
                signatures.append("execution > narratives")
            if "patience" in text_lower:
                signatures.append("patience")
            if "lfg" in text_lower:
                signatures.append("lfg")
        
        # Extract emojis
        all_emojis = []
        for text in texts:
            emojis = self.emoji_pattern.findall(str(text))
            all_emojis.extend([e for em in emojis for e in em])
        
        emoji_counts = Counter(all_emojis)
        
        # Avg text length
        lengths = [len(str(t).split()) for t in texts if t]
        avg_length = sum(lengths) / len(lengths) if lengths else 0
        
        return {
            "frequent": dict(word_counts.most_common(50)),
            "signature_phrases": list(set(signatures)),
            "emoji_usage": dict(emoji_counts.most_common(20)),
            "avg_word_count": round(avg_length, 1),
            "total_words_analyzed": len(all_words)
        }
    
    def analyze_timing(self, tweets: List[Dict]) -> Dict:
        """Analyze posting patterns"""
        if not tweets:
            return {"active_hours": [], "avg_posts_per_day": 0}
        
        hours = []
        for tweet in tweets:
            # Try to extract timestamp
            ts = tweet.get("created_at") or tweet.get("timestamp")
            if ts:
                try:
                    if isinstance(ts, str):
                        hour = int(ts.split(":")[0]) if ":" in ts else 12
                    else:
                        hour = 12
                    hours.append(hour)
                except:
                    pass
        
        # Calculate peak hours
        hour_counts = Counter(hours)
        peak_hours = [h for h, _ in hour_counts.most_common(3)]
        
        # Estimate posts per day (rough)
        unique_days = len(set(t.get("date", "") for t in tweets))
        posts_per_day = len(tweets) / max(unique_days, 1)
        
        return {
            "peak_hours": sorted(peak_hours) if peak_hours else [8, 9, 13, 21],
            "avg_posts_per_day": round(posts_per_day, 1),
            "active_hours": list(range(5, 23))  # Default range
        }
    
    def analyze_engagement(self, likes: List[Dict], mentions: List[Dict]) -> Dict:
        """Analyze engagement patterns"""
        # Who they mention
        mentioned_users = []
        for tweet in mentions:
            text = str(tweet.get("text", ""))
            mentioned_users.extend(re.findall(r'@(\w+)', text))
        
        user_counts = Counter(mentioned_users)
        
        # Topics from likes
        liked_topics = []
        for like in likes[:50]:
            text = str(like.get("text", ""))
            if "starknet" in text.lower() or "zk" in text.lower():
                liked_topics.append("starknet")
            if "defi" in text.lower():
                liked_topics.append("defi")
            if "eth" in text.lower():
                liked_topics.append("ethereum")
        
        return {
            "frequently_mentioned": list(user_counts.most_common(10)),
            "liked_topics": list(set(liked_topics)),
            "priority_accounts": ["StarkWareLtd", "Starknet", "VitalikButerin"]
        }
    
    def detect_tone(self, texts: List[str]) -> List[str]:
        """Detect tone from text analysis"""
        tones = []
        
        text_combined = " ".join(texts).lower()
        
        # Minimal/Cryptic indicators
        if len(texts) > 0:
            avg_length = sum(len(t.split()) for t in texts) / len(texts)
            if avg_length < 10:
                tones.append("minimal")
            if avg_length < 20:
                tones.append("cryptic")
        
        # Edgy indicators
        edgy_words = ["lfg", "ser", "gm", "based", "bullish"]
        if any(w in text_combined for w in edgy_words):
            tones.append("edgy")
        
        # Technical indicators
        tech_words = ["zk", "rollup", "cairo", "execution", "protocol"]
        if any(w in text_combined for w in tech_words):
            tones.append("technical")
        
        # Confident indicators
        confident_words = ["higher", "knows", "patience"]
        if any(w in text_combined for w in confident_words):
            tones.append("confident")
        
        # Default
        if not tones:
            tones = ["minimal", "confident"]
        
        return list(set(tones))
    
    def build_profile(self, days: int = 30) -> Dict:
        """Build complete style profile"""
        observations = self.load_observations(days)
        
        # Collect all texts
        all_texts = []
        for obs in observations:
            all_texts.extend(obs.get("tweets", []))
        
        likes = []
        for obs in observations:
            likes.extend(obs.get("likes", []))
        
        mentions = []
        for obs in observations:
            mentions.extend(obs.get("mentions", []))
        
        if not all_texts:
            # Default profile if no data
            return self._default_profile()
        
        # Analyze each component
        vocabulary = self.analyze_vocabulary(all_texts)
        timing = self.analyze_timing(all_texts)
        engagement = self.analyze_engagement(likes, mentions)
        tone = self.detect_tone(all_texts)
        
        # Emoji style
        emoji_count = sum(vocabulary.get("emoji_usage", {}).values())
        if emoji_count == 0:
            emoji_style = "sparse"
        elif emoji_count < len(all_texts) * 0.3:
            emoji_style = "sparse"
        elif emoji_count < len(all_texts) * 0.7:
            emoji_style = "moderate"
        else:
            emoji_style = "heavy"
        
        profile = {
            "persona": {
                "name": "SefirotWatch",
                "tone": tone,
                "emoji_style": emoji_style,
                "caps_usage": "rare"
            },
            "vocabulary": vocabulary,
            "timing": timing,
            "engagement": engagement,
            "generated_at": datetime.now().isoformat(),
            "observations_count": len(observations)
        }
        
        return profile
    
    def _default_profile(self) -> Dict:
        """Return default profile for new users"""
        return {
            "persona": {
                "name": "SefirotWatch",
                "tone": ["minimal", "cryptic", "confident"],
                "emoji_style": "sparse",
                "caps_usage": "rare"
            },
            "vocabulary": {
                "frequent": {"higher": 5, "execution": 3, "patience": 2},
                "signature_phrases": [],
                "emoji_usage": {"🐺": 3, "🔥": 2},
                "avg_word_count": 10
            },
            "timing": {
                "peak_hours": [8, 9, 13, 21],
                "avg_posts_per_day": 5,
                "active_hours": list(range(5, 23))
            },
            "engagement": {
                "frequently_mentioned": [],
                "liked_topics": ["starknet", "defi"],
                "priority_accounts": ["StarkWareLtd", "Starknet"]
            },
            "generated_at": datetime.now().isoformat(),
            "observations_count": 0
        }


if __name__ == "__main__":
    analyzer = StyleAnalyzer()
    profile = analyzer.build_profile()
    print(json.dumps(profile, indent=2))
