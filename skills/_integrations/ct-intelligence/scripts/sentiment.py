#!/usr/bin/env python3
"""
Sentiment Analysis for CT Intelligence.

Error Handling:
- All public methods wrap operations in try/except
- Errors logged and propagated for caller handling
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from collections import Counter
import logging

logger = logging.getLogger(__name__)


@dataclass
class SentimentResult:
    """Sentiment analysis result."""
    text: str
    sentiment: str  # positive, negative, neutral
    score: float  # -1.0 to 1.0
    keywords: List[str]
    confidence: float


class SentimentAnalyzer:
    """Analyze sentiment of tweets and accounts."""
    
    # Keywords for sentiment detection
    POSITIVE = [
        "moon", "lambo", "profit", "win", "gain", "up", "bullish",
        "great", "amazing", "love", "best", "awesome", "excited",
        "high", "突破", "上涨", "收益", "盈利"
    ]
    
    NEGATIVE = [
        "dump", "rug", "scam", "loss", "fail", "down", "bearish",
        "bad", "terrible", "hate", "worst", "sad", "worried",
        "low", "暴跌", "下跌", "亏损", "归零"
    ]
    
    def __init__(self, config: Dict = None):
        """Initialize analyzer."""
        self.config = config or {}
        logger.info("Sentiment Analyzer initialized")
    
    def analyze_text(self, text: str) -> SentimentResult:
        """
        Analyze sentiment of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            SentimentResult with analysis
        """
        try:
            text_lower = text.lower()
            
            # Count keywords
            pos_count = sum(1 for w in self.POSITIVE if w in text_lower)
            neg_count = sum(1 for w in self.NEGATIVE if w in text_lower)
            
            # Calculate score
            total = pos_count + neg_count
            if total == 0:
                score = 0.0
                sentiment = "neutral"
            else:
                score = (pos_count - neg_count) / total
                if score > 0.2:
                    sentiment = "positive"
                elif score < -0.2:
                    sentiment = "negative"
                else:
                    sentiment = "neutral"
            
            # Extract keywords
            keywords = [w for w in self.POSITIVE + self.NEGATIVE if w in text_lower]
            
            # Confidence based on keyword count
            confidence = min(total / 5, 1.0)
            
            return SentimentResult(
                text=text,
                sentiment=sentiment,
                score=score,
                keywords=keywords,
                confidence=confidence
            )
        except Exception as e:
            logger.error(f"Failed to analyze text: {e}")
            raise
    
    def analyze_tweets(self, tweets: List[Dict]) -> Dict:
        """
        Analyze sentiment of multiple tweets.
        
        Args:
            tweets: List of tweet dicts
            
        Returns:
            Aggregated sentiment analysis
        """
        try:
            if not tweets:
                return {"sentiment": "neutral", "score": 0.0, "count": 0}
            
            results = [self.analyze_text(t.get("text", "")) for t in tweets]
            
            # Aggregate
            avg_score = sum(r.score for r in results) / len(results)
            
            sentiment_counts = Counter(r.sentiment for r in results)
            dominant = sentiment_counts.most_common(1)[0][0]
            
            return {
                "sentiment": dominant,
                "score": round(avg_score, 3),
                "count": len(results),
                "breakdown": dict(sentiment_counts),
                "keywords": self._top_keywords(results)
            }
        except Exception as e:
            logger.error(f"Failed to analyze tweets: {e}")
            raise
    
    def _top_keywords(self, results: List[SentimentResult]) -> List[str]:
        """Get top mentioned keywords."""
        try:
            all_keywords = []
            for r in results:
                all_keywords.extend(r.keywords)
            return [k for k, _ in Counter(all_keywords).most_common(10)]
        except Exception as e:
            logger.error(f"Failed to get top keywords: {e}")
            return []
    
    def get_account_sentiment(self, username: str, tweets: List[Dict]) -> Dict:
        """
        Get overall sentiment for account.
        
        Args:
            username: Account username
            tweets: List of tweet dicts
            
        Returns:
            Account sentiment profile
        """
        try:
            analysis = self.analyze_tweets(tweets)
            
            return {
                "username": username,
                "sentiment": analysis["sentiment"],
                "score": analysis["score"],
                "tweet_count": analysis["count"],
                "breakdown": analysis.get("breakdown", {}),
                "top_keywords": analysis.get("keywords", [])
            }
        except Exception as e:
            logger.error(f"Failed to get account sentiment for {username}: {e}")
            raise


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sentiment Analysis")
    parser.add_argument("--text", help="Text to analyze")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    analyzer = SentimentAnalyzer()
    
    if args.text:
        result = analyzer.analyze_text(args.text)
        if args.json:
            import json
            print(json.dumps({
                "sentiment": result.sentiment,
                "score": result.score,
                "keywords": result.keywords,
                "confidence": result.confidence
            }, indent=2))
        else:
            print(f"Sentiment: {result.sentiment} ({result.score:+.2f})")
            print(f"Keywords: {', '.join(result.keywords)}")
            print(f"Confidence: {result.confidence:.2%}")


if __name__ == "__main__":
    main()
