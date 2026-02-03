#!/usr/bin/env python3
"""
X Algorithm Optimizer - Timing and engagement optimization

Based on x-algorithm-optimizer skill.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime, timedelta


@dataclass
class ScoreResult:
    """Content scoring result."""
    score: float
    factors: Dict[str, float]
    recommendation: str


class AlgorithmOptimizer:
    """
    Optimizes content for X algorithm.
    
    Factors:
    - Timing (peak hours bonus)
    - Content length (optimal 50-100 chars)
    - Engagement signals (questions, calls to action)
    - Emoji usage (optimal 1-2)
    - Hashtags (minimal, relevant)
    """
    
    # Optimal posting hours (UTC, based on CT engagement)
    PEAK_HOURS = [8, 9, 13, 21]
    
    # Hours to avoid
    AVOID_HOURS = [2, 3, 4, 5]
    
    def __init__(self):
        self.history = []
    
    def score_content(self, content: str, post_time: datetime = None) -> ScoreResult:
        """
        Score content for algorithm optimization.
        
        Returns score 0-100 and recommendations.
        """
        factors = {}
        
        # Length scoring (optimal: 50-100 chars)
        length = len(content)
        if 50 <= length <= 100:
            factors["length"] = 1.0
        elif length < 50:
            factors["length"] = 0.5 + (length / 100)
        else:
            factors["length"] = max(0.3, 1.0 - (length - 100) / 200)
        
        # Emoji scoring (optimal: 1-2)
        emoji_count = sum(1 for c in content if c in "🔥🐺💀🧠🚀🌙⭐💎🤖")
        if 1 <= emoji_count <= 2:
            factors["emoji"] = 1.0
        elif emoji_count == 0:
            factors["emoji"] = 0.7
        else:
            factors["emoji"] = max(0.5, 1.0 - (emoji_count - 2) * 0.1)
        
        # Engagement signals
        engagement = 0.5
        if "?" in content:
            engagement += 0.2  # Questions boost
        if any(w in content.lower() for w in ["gm", "lfg", "fr", "的观点"]):
            engagement += 0.15  # Community signals
        if any(w in content.lower() for w in ["follow", "retweet", "share"]):
            engagement += 0.1  # CTAs
        factors["engagement"] = min(1.0, engagement)
        
        # Timing score
        time_score = 0.5
        if post_time:
            hour = post_time.hour
            if hour in self.PEAK_HOURS:
                time_score = 1.0
            elif hour in self.AVOID_HOURS:
                time_score = 0.2
            else:
                time_score = 0.6
        factors["timing"] = time_score
        
        # Hashtag penalty
        hashtag_count = content.count("#")
        if hashtag_count == 0:
            factors["hashtags"] = 1.0
        elif hashtag_count <= 2:
            factors["hashtags"] = 0.9
        else:
            factors["hashtags"] = max(0.3, 1.0 - hashtag_count * 0.15)
        
        # Calculate weighted score
        weights = {
            "length": 0.2,
            "emoji": 0.15,
            "engagement": 0.3,
            "timing": 0.25,
            "hashtags": 0.1
        }
        
        total_score = sum(
            factors.get(k, 0.5) * v 
            for k, v in weights.items()
        ) * 100
        
        # Generate recommendation
        recommendation = self._generate_recommendation(factors, content)
        
        return ScoreResult(
            score=round(total_score, 1),
            factors=factors,
            recommendation=recommendation
        )
    
    def _generate_recommendation(self, factors: Dict, content: str) -> str:
        """Generate improvement recommendations."""
        recommendations = []
        
        if factors.get("length", 0.5) < 0.7:
            recommendations.append("Shorten or expand content (aim for 50-100 chars)")
        if factors.get("emoji", 0.5) < 0.8:
            recommendations.append("Add 1-2 community emojis")
        if factors.get("engagement", 0.5) < 0.7:
            recommendations.append("Add question or community signal (gm, lfg)")
        if factors.get("timing", 0.5) < 0.7:
            recommendations.append("Consider posting during peak hours (8, 9, 13, 21 UTC)")
        if factors.get("hashtags", 0.5) < 0.8:
            recommendations.append("Reduce or remove hashtags")
        
        if not recommendations:
            return "Content is well-optimized for algorithm! 🎯"
        
        return "Improve: " + "; ".join(recommendations)
    
    def get_best_hours(self) -> List[int]:
        """Get optimal posting hours."""
        return self.PEAK_HOURS.copy()
    
    def get_worst_hours(self) -> List[int]:
        """Get hours to avoid."""
        return self.AVOID_HOURS.copy()
    
    def suggest_improvements(self, content: str) -> Dict:
        """Get suggestions for improving content."""
        score = self.score_content(content)
        
        suggestions = {
            "current_score": score.score,
            "factors": score.factors,
            "recommendation": score.recommendation
        }
        
        # Generate improved version
        improved = content
        
        # Add emoji if missing
        if not any(c in improved for c in "🔥🐺💀🧠🚀🌙⭐💎🤖"):
            improved = f"{improved} 🐺"
        
        # Trim if too long
        if len(improved) > 100:
            improved = improved[:97] + "..."
        
        suggestions["improved_version"] = improved
        
        return suggestions
    
    def optimal_timing(self, content: str) -> Dict:
        """Get optimal timing for content."""
        now = datetime.utcnow()
        
        best_time = None
        best_score = 0
        
        for hour in self.PEAK_HOURS:
            candidate = now.replace(hour=hour, minute=0, second=0)
            if candidate > now:
                score = self.score_content(content, candidate)
                if score.score > best_score:
                    best_score = score.score
                    best_time = candidate
        
        if not best_time:
            # Next day
            best_time = now.replace(hour=self.PEAK_HOURS[0], minute=0, second=0) + timedelta(days=1)
        
        return {
            "best_time": best_time.isoformat(),
            "expected_score": best_score,
            "peak_hours": self.PEAK_HOURS
        }


# Convenience function
def score(content: str, post_time: datetime = None) -> ScoreResult:
    """Quick content scoring."""
    optimizer = AlgorithmOptimizer()
    return optimizer.score_content(content, post_time)
