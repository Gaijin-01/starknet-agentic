"""
Viral Analysis Module.

Analyzes content virality patterns, detects viral content,
and provides recommendations for maximizing reach.
"""

import os
import json
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ViralMetrics:
    """Metrics for viral potential."""
    virality_score: float  # 0-100
    engagement_score: float  # 0-100
    reach_score: float  # 0-100
    overall_score: float  # 0-100
    factors: Dict[str, float]
    recommendations: List[str]


@dataclass
class ViralContent:
    """Detected viral content."""
    id: str
    platform: str
    content_type: str
    text: str
    engagement: Dict[str, int]
    virality_score: float
    detected_at: datetime
    url: str
    hashtags: List[str] = None
    mentions: List[str] = None


class ViralAnalyzer:
    """Analyzes content for viral potential."""
    
    # Viral content patterns
    VIRAL_TRIGGERS = {
        "emotional": ["amazing", "incredible", "shocking", "unbelievable", "must see"],
        "urgent": ["now", "limited", "hurry", "last chance", "expires"],
        "curiosity": ["you won't believe", "secret", "revealed", "what if", "guess"],
        "social": ["tag", "share", "retweet", "follow", "comment"],
        "controversial": ["vs", "versus", "wrong", "right", "debate"],
    }
    
    # Optimal content characteristics
    OPTIMAL_LENGTH = {
        "tweet": (70, 100),  # Characters
        "linkedin_post": (150, 300),
        "instagram_caption": (150, 250),
    }
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize viral analyzer.
        
        Args:
            data_dir: Directory for storing analysis data
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Viral content history
        self._viral_history: List[ViralContent] = []
        self._load_viral_history()
    
    # ============ Viral Scoring ============
    
    def analyze_virality(self, text: str, context: Optional[Dict] = None) -> ViralMetrics:
        """
        Analyze text for viral potential.
        
        Args:
            text: Content to analyze
            context: Additional context (hashtags, mentions, etc.)
            
        Returns:
            ViralMetrics with scores and recommendations
        """
        context = context or {}
        factors = {}
        recommendations = []
        
        # Length analysis
        length = len(text)
        optimal = self.OPTIMAL_LENGTH.get("tweet", (70, 100))
        
        if optimal[0] <= length <= optimal[1]:
            factors["length"] = 100
        elif length < optimal[0]:
            factors["length"] = max(0, 100 - (optimal[0] - length) * 2)
            recommendations.append("Consider adding more detail (target: 70-100 chars)")
        else:
            factors["length"] = max(0, 100 - (length - optimal[1]) * 1.5)
            recommendations.append("Consider shortening (target: 70-100 chars)")
        
        # Hashtag analysis
        hashtags = context.get("hashtags", self._extract_hashtags(text))
        if len(hashtags) in [2, 3, 4]:
            factors["hashtags"] = 100
        elif len(hashtags) < 2:
            factors["hashtags"] = 50
            recommendations.append("Add 2-4 relevant hashtags")
        else:
            factors["hashtags"] = max(0, 100 - (len(hashtags) - 4) * 10)
            recommendations.append("Limit to 2-4 hashtags")
        
        # Viral triggers
        trigger_score = self._analyze_triggers(text)
        factors["triggers"] = trigger_score
        
        if trigger_score < 30:
            recommendations.append("Add emotional or curiosity-triggering words")
        
        # Sentiment analysis (simple)
        sentiment_score = self._analyze_sentiment(text)
        factors["sentiment"] = sentiment_score
        
        # URL/media presence
        has_url = bool(context.get("has_url") or self._extract_urls(text))
        has_media = context.get("has_media", False)
        
        if has_url or has_media:
            factors["media"] = 100
        else:
            factors["media"] = 70
            recommendations.append("Add media or links for higher engagement")
        
        # Engagement prediction
        engagement_score = self._predict_engagement(text, factors)
        factors["predicted_engagement"] = engagement_score
        
        # Calculate overall score
        weights = {
            "length": 0.15,
            "hashtags": 0.15,
            "triggers": 0.25,
            "sentiment": 0.15,
            "media": 0.15,
            "predicted_engagement": 0.15
        }
        
        overall = sum(factors.get(k, 0) * v for k, v in weights.items())
        
        virality_score = self._calculate_virality_score(factors, overall)
        reach_score = self._calculate_reach_score(text, context)
        
        return ViralMetrics(
            virality_score=virality_score,
            engagement_score=engagement_score,
            reach_score=reach_score,
            overall_score=overall,
            factors=factors,
            recommendations=recommendations
        )
    
    def analyze_thread(
        self,
        tweets: List[str],
        context: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Analyze a thread for viral potential.
        
        Args:
            tweets: List of tweet texts
            context: Optional list of tweet contexts
            
        Returns:
            Thread analysis
        """
        context = context or [{}] * len(tweets)
        
        analyses = []
        total_score = 0
        
        for i, (tweet, ctx) in enumerate(zip(tweets, context)):
            analysis = self.analyze_virality(tweet, ctx)
            analyses.append({
                "position": i + 1,
                "text": tweet[:50] + "...",
                "score": analysis.overall_score,
                "factors": analysis.factors,
                "recommendations": analysis.recommendations
            })
            total_score += analysis.overall_score
        
        avg_score = total_score / len(tweets) if tweets else 0
        
        # Thread-specific analysis
        hook_strength = analyses[0]["score"] if analyses else 0
        conclusion_strength = analyses[-1]["score"] if analyses else 0
        
        return {
            "total_tweets": len(tweets),
            "average_score": avg_score,
            "hook_strength": hook_strength,
            "conclusion_strength": conclusion_strength,
            "tweet_analyses": analyses,
            "thread_recommendations": self._analyze_thread_structure(analyses)
        }
    
    # ============ Content Optimization ============
    
    def optimize_for_virality(
        self,
        text: str,
        target_platform: str = "twitter",
        max_length: int = 280
    ) -> Dict[str, Any]:
        """
        Generate optimized versions of content.
        
        Args:
            text: Original content
            target_platform: Target platform
            max_length: Max character length
            
        Returns:
            Optimization results
        """
        base_analysis = self.analyze_virality(text)
        
        optimizations = []
        
        # Version with hashtags
        hashtags = self._extract_hashtags(text)
        if len(hashtags) < 2:
            optimized = text + " #trending #viral"
            if len(optimized) <= max_length:
                analysis = self.analyze_virality(optimized)
                optimizations.append({
                    "type": "with_hashtags",
                    "text": optimized,
                    "score": analysis.overall_score,
                    "improvement": analysis.overall_score - base_analysis.overall_score
                })
        
        # Version with hook
        hooks = [
            "You won't believe this: ",
            "Here's the truth: ",
            "Just discovered: ",
            "This is huge: ",
        ]
        
        for hook in hooks:
            optimized = hook + text
            if len(optimized) <= max_length:
                analysis = self.analyze_virality(optimized)
                optimizations.append({
                    "type": "with_hook",
                    "text": optimized,
                    "score": analysis.overall_score,
                    "improvement": analysis.overall_score - base_analysis.overall_score
                })
        
        # Short version
        if len(text) > 100:
            short_version = text[:97] + "..."
            analysis = self.analyze_virality(short_version)
            optimizations.append({
                "type": "shortened",
                "text": short_version,
                "score": analysis.overall_score,
                "improvement": analysis.overall_score - base_analysis.overall_score
            })
        
        # Sort by improvement
        optimizations.sort(key=lambda x: x["improvement"], reverse=True)
        
        return {
            "original": {
                "text": text,
                "score": base_analysis.overall_score
            },
            "optimizations": optimizations,
            "best_option": optimizations[0] if optimizations else None
        }
    
    def generate_viral_hook(
        self,
        topic: str,
        style: str = "curiosity"
    ) -> str:
        """
        Generate viral-style hooks for a topic.
        
        Args:
            topic: Content topic
            style: Hook style (curiosity, urgency, emotion, controversy)
            
        Returns:
            Generated hook
        """
        hooks = {
            "curiosity": [
                f"You've been thinking about {topic} wrong. Here's why...",
                f"The secret about {topic} nobody tells you.",
                f"What if everything you know about {topic} is wrong?",
                f"I spent 100 hours studying {topic}. Here's what I found.",
            ],
            "urgency": [
                f"This {topic} strategy expires soon. Don't miss out.",
                f"Limited time: The ultimate {topic} guide.",
                f"Only 1% know this {topic} hack. Will you?",
                f"Last chance to learn this {topic} technique.",
            ],
            "emotion": [
                f"This {topic} story gave me chills.",
                f"The most inspiring {topic} journey I've ever seen.",
                f"If you're struggling with {topic}, read this.",
                f"After 10 years in {topic}, I'm finally sharing this.",
            ],
            "controversy": [
                f"Hot take: Most {topic} advice is garbage.",
                f"Unpopular opinion: {topic} is overrated.",
                f"Why {topic} proponents are wrong.",
                f"The {topic} debate nobody asked for.",
            ]
        }
        
        style_hooks = hooks.get(style, hooks["curiosity"])
        return style_hooks[hash(topic) % len(style_hooks)]
    
    # ============ Viral Detection ============
    
    def detect_viral_content(
        self,
        content_list: List[Dict[str, Any]],
        threshold: float = 70.0
    ) -> List[ViralContent]:
        """
        Detect viral content from a list.
        
        Args:
            content_list: List of content dicts
            threshold: Virality threshold (0-100)
            
        Returns:
            List of ViralContent
        """
        viral = []
        
        for item in content_list:
            text = item.get("text", "")
            analysis = self.analyze_virality(text, item)
            
            if analysis.overall_score >= threshold:
                viral_content = ViralContent(
                    id=item.get("id", ""),
                    platform=item.get("platform", "twitter"),
                    content_type=item.get("type", "post"),
                    text=text,
                    engagement=item.get("engagement", {}),
                    virality_score=analysis.overall_score,
                    detected_at=datetime.now(),
                    url=item.get("url", ""),
                    hashtags=self._extract_hashtags(text),
                    mentions=self._extract_mentions(text)
                )
                viral.append(viral_content)
        
        # Sort by virality score
        viral.sort(key=lambda x: x.virality_score, reverse=True)
        
        return viral
    
    def learn_from_viral_content(self, viral_content: ViralContent):
        """
        Learn from detected viral content.
        
        Args:
            viral_content: Viral content to learn from
        """
        self._viral_history.append(viral_content)
        self._save_viral_history()
        
        logger.info(f"Learned from viral content: {viral_content.id}")
    
    def get_viral_patterns(self) -> Dict[str, Any]:
        """
        Get learned viral patterns.
        
        Returns:
            Pattern analysis
        """
        if not self._viral_history:
            return {"error": "No viral content analyzed yet"}
        
        # Analyze common patterns
        avg_score = sum(v.virality_score for v in self._viral_history) / len(self._viral_history)
        
        # Common hashtags
        all_hashtags = []
        for v in self._viral_history:
            all_hashtags.extend(v.hashtags or [])
        
        from collections import Counter
        hashtag_counts = Counter(all_hashtags)
        
        # Average engagement
        total_engagement = defaultdict(int)
        for v in self._viral_history:
            for metric, value in v.engagement.items():
                total_engagement[metric] += value
        
        avg_engagement = {
            k: v / len(self._viral_history)
            for k, v in total_engagement.items()
        }
        
        return {
            "total_analyzed": len(self._viral_history),
            "average_virality_score": avg_score,
            "common_hashtags": dict(hashtag_counts.most_common(10)),
            "average_engagement": avg_engagement,
            "platform_breakdown": self._get_platform_breakdown()
        }
    
    # ============ Helper Methods ============
    
    def _analyze_triggers(self, text: str) -> float:
        """Analyze viral triggers in text."""
        text_lower = text.lower()
        score = 50  # Base score
        
        for category, triggers in self.VIRAL_TRIGGERS.items():
            for trigger in triggers:
                if trigger in text_lower:
                    score += 5
        
        return min(100, score)
    
    def _analyze_sentiment(self, text: str) -> float:
        """Simple sentiment analysis (returns 0-100 positive score)."""
        positive = ["great", "amazing", "love", "best", "excited", "happy", "awesome"]
        negative = ["bad", "terrible", "hate", "worst", "sad", "angry", "awful"]
        
        text_lower = text.lower()
        
        pos_count = sum(1 for w in positive if w in text_lower)
        neg_count = sum(1 for w in negative if w in text_lower)
        
        if pos_count + neg_count == 0:
            return 50  # Neutral
        
        ratio = pos_count / (pos_count + neg_count)
        return 50 + (ratio - 0.5) * 50
    
    def _predict_engagement(self, text: str, factors: Dict[str, float]) -> float:
        """Predict engagement rate."""
        # Base engagement
        base = 50
        
        # Adjust for factors
        if factors.get("length", 0) > 80:
            base += 10
        if factors.get("triggers", 0) > 60:
            base += 15
        if factors.get("sentiment", 50) > 60:
            base += 10
        
        return min(100, base)
    
    def _calculate_virality_score(
        self,
        factors: Dict[str, float],
        overall: float
    ) -> float:
        """Calculate virality score (0-100)."""
        # Weight the factors differently for virality
        virality_weights = {
            "triggers": 0.35,
            "sentiment": 0.25,
            "media": 0.20,
            "length": 0.10,
            "hashtags": 0.10
        }
        
        return sum(factors.get(k, 0) * v for k, v in virality_weights.items())
    
    def _calculate_reach_score(self, text: str, context: Dict[str, Any]) -> float:
        """Calculate potential reach score."""
        # Base reach
        reach = 30
        
        # Adjust for factors
        if context.get("has_media", False):
            reach += 20
        
        hashtags = context.get("hashtags", self._extract_hashtags(text))
        if len(hashtags) > 0:
            reach += len(hashtags) * 5
        
        # Check for share triggers
        if "share" in text.lower() or "retweet" in text.lower():
            reach += 15
        
        return min(100, reach)
    
    def _analyze_thread_structure(self, analyses: List[Dict]) -> List[str]:
        """Analyze thread structure and give recommendations."""
        recommendations = []
        
        if not analyses:
            return ["Thread is empty"]
        
        # Check hook
        if analyses[0]["score"] < 60:
            recommendations.append("First tweet needs a stronger hook")
        
        # Check conclusion
        if analyses[-1]["score"] < 50:
            recommendations.append("Final tweet needs a stronger call-to-action")
        
        # Check pacing
        if len(analyses) > 5:
            avg_middle = sum(a["score"] for a in analyses[1:-1]) / max(1, len(analyses) - 2)
            if avg_middle < 50:
                recommendations.append("Middle tweets need more engagement hooks")
        
        return recommendations
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text."""
        return re.findall(r"#(\w+)", text)
    
    def _extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from text."""
        return re.findall(r"@(\w+)", text)
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text."""
        return re.findall(r"https?://\S+", text)
    
    def _get_platform_breakdown(self) -> Dict[str, int]:
        """Get breakdown by platform."""
        from collections import Counter
        platforms = [v.platform for v in self._viral_history]
        return dict(Counter(platforms))
    
    # ============ Data Persistence ============
    
    def _load_viral_history(self):
        """Load viral history from file."""
        path = os.path.join(self.data_dir, "viral_history.json")
        if os.path.exists(path):
            try:
                with open(path) as f:
                    data = json.load(f)
                    for item in data:
                        self._viral_history.append(ViralContent(
                            id=item["id"],
                            platform=item["platform"],
                            content_type=item["content_type"],
                            text=item["text"],
                            engagement=item["engagement"],
                            virality_score=item["virality_score"],
                            detected_at=datetime.fromisoformat(item["detected_at"]),
                            url=item["url"],
                            hashtags=item.get("hashtags"),
                            mentions=item.get("mentions")
                        ))
            except Exception as e:
                logger.error(f"Failed to load viral history: {e}")
    
    def _save_viral_history(self):
        """Save viral history to file."""
        path = os.path.join(self.data_dir, "viral_history.json")
        
        data = []
        for v in self._viral_history[-1000:]:  # Keep last 1000
            data.append({
                "id": v.id,
                "platform": v.platform,
                "content_type": v.content_type,
                "text": v.text,
                "engagement": v.engagement,
                "virality_score": v.virality_score,
                "detected_at": v.detected_at.isoformat(),
                "url": v.url,
                "hashtags": v.hashtags,
                "mentions": v.mentions
            })
        
        with open(path, "w") as f:
            json.dump(data, f)
