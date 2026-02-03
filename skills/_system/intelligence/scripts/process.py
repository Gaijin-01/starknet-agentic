#!/usr/bin/env python3
"""
process.py - Filter, rank, and summarize intelligence signals.

Features:
- Relevance filtering
- Deduplication
- Multi-factor ranking
- Sentiment analysis
- Summary generation
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import re

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import load_config
from gather import IntelligenceSignal, Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ProcessedSignal:
    """Processed and ranked intelligence signal."""
    original: Dict
    relevance_score: float
    rank: int
    cluster_id: Optional[str]
    summary: str
    key_points: List[str]
    sentiment: str
    sentiment_score: float
    
    def to_dict(self) -> Dict:
        return asdict(self)


# ============================================
# RELEVANCE FILTERING
# ============================================

def filter_relevance(
    signals: List[IntelligenceSignal],
    min_score: float = 0.5,
    keywords: List[str] = None
) -> List[IntelligenceSignal]:
    """
    Filter signals by relevance score.
    
    Args:
        signals: List of IntelligenceSignal objects
        min_score: Minimum relevance score to include
        keywords: Keywords to boost relevance for
        
    Returns:
        Filtered list of signals
    """
    keywords = keywords or []
    
    filtered = []
    for signal in signals:
        score = _calculate_relevance(signal, keywords)
        signal.relevance_score = score
        
        if score >= min_score:
            filtered.append(signal)
    
    logger.info(f"Relevance filter: {len(signals)} -> {len(filtered)} signals (min_score={min_score})")
    
    return filtered


def _calculate_relevance(signal: IntelligenceSignal, keywords: List[str]) -> float:
    """Calculate relevance score for a signal."""
    score = 0.5  # Base score
    
    title_lower = signal.title.lower()
    content_lower = signal.content.lower()
    
    # Keyword matching
    for kw in keywords:
        kw_lower = kw.lower()
        if kw_lower in title_lower:
            score += 0.15
        if kw_lower in content_lower:
            score += 0.05
    
    # Engagement boost
    engagement = signal.engagement
    total_engagement = sum(engagement.values()) if engagement else 0
    
    if total_engagement > 1000:
        score += 0.2
    elif total_engagement > 500:
        score += 0.15
    elif total_engagement > 100:
        score += 0.1
    elif total_engagement > 10:
        score += 0.05
    
    # Source quality adjustment
    source_quality = {
        "hacker_news": 0.9,
        "whale_tracker": 0.85,
        "twitter": 0.8,
        "reddit": 0.75,
        "dexscreener": 0.7
    }
    score *= source_quality.get(signal.source, 0.7)
    
    # Recency boost
    try:
        signal_time = datetime.fromisoformat(signal.timestamp.replace('Z', '+00:00'))
        hours_ago = (datetime.now() - signal_time).total_seconds() / 3600
        
        if hours_ago < 1:
            score += 0.1
        elif hours_ago < 6:
            score += 0.05
        elif hours_ago > 48:
            score -= 0.1
    except:
        pass
    
    return min(max(score, 0), 1)


# ============================================
# DEDUPLICATION
# ============================================

def deduplicate(
    signals: List[IntelligenceSignal],
    threshold: float = 0.85
) -> List[IntelligenceSignal]:
    """
    Remove duplicate or near-duplicate signals.
    
    Args:
        signals: List of signals
        threshold: Similarity threshold (0-1)
        
    Returns:
        Deduplicated list
    """
    if len(signals) <= 1:
        return signals
    
    # Create text fingerprints
    fingerprints = []
    for signal in signals:
        fp = _create_fingerprint(signal)
        fingerprints.append((signal, fp))
    
    # Cluster similar signals
    clusters = []
    for signal, fp in fingerprints:
        placed = False
        
        for cluster in clusters:
            cluster_fp = cluster['fingerprint']
            similarity = _calculate_similarity(fp, cluster_fp)
            
            if similarity >= threshold:
                # Add to existing cluster (keep the higher scoring one)
                if signal.relevance_score > cluster['representative'].relevance_score:
                    cluster['representative'] = signal
                cluster['signals'].append(signal)
                placed = True
                break
        
        if not placed:
            clusters.append({
                'fingerprint': fp,
                'representative': signal,
                'signals': [signal]
            })
    
    # Return representatives
    deduplicated = [c['representative'] for c in clusters]
    
    logger.info(f"Deduplication: {len(signals)} -> {len(deduplicated)} signals")
    
    return deduplicated


def _create_fingerprint(signal: IntelligenceSignal) -> str:
    """Create text fingerprint for deduplication."""
    text = (signal.title + " " + signal.content).lower()
    
    # Remove common words
    stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 
                  'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                  'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                  'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she',
                  'it', 'we', 'they', 'what', 'which', 'who', 'whom', 'from'}
    
    words = [w for w in re.findall(r'\b[a-z]+\b', text) if w not in stop_words]
    
    # Sort and join first 10 words
    return ' '.join(sorted(set(words))[:10])


def _calculate_similarity(fp1: str, fp2: str) -> float:
    """Calculate similarity between two fingerprints."""
    words1 = set(fp1.split())
    words2 = set(fp2.split())
    
    if not words1 or not words2:
        return 0
    
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    return intersection / union if union > 0 else 0


# ============================================
# RANKING
# ============================================

def rank_signals(
    signals: List[IntelligenceSignal],
    weights: Dict[str, float] = None
) -> List[IntelligenceSignal]:
    """
    Rank signals by multiple factors.
    
    Args:
        signals: List of signals
        weights: Custom weights for ranking factors
        
    Returns:
        Ranked list of signals
    """
    weights = weights or {
        "relevance": 0.4,
        "engagement": 0.25,
        "recency": 0.2,
        "source_quality": 0.15
    }
    
    # Calculate composite score for each signal
    scored = []
    for signal in signals:
        score = _calculate_composite_score(signal, weights)
        scored.append((signal, score))
    
    # Sort by composite score
    scored.sort(key=lambda x: x[1], reverse=True)
    
    # Assign ranks
    ranked = []
    for rank, (signal, score) in enumerate(scored, 1):
        signal.relevance_score = score
        ranked.append(signal)
    
    logger.info(f"Ranked {len(ranked)} signals")
    
    return ranked


def _calculate_composite_score(signal: IntelligenceSignal, weights: Dict) -> float:
    """Calculate composite ranking score."""
    score = 0
    
    # Relevance (already calculated)
    score += weights.get("relevance", 0.4) * signal.relevance_score
    
    # Engagement
    engagement = signal.engagement or {}
    total_engagement = sum(engagement.values())
    engagement_score = min(total_engagement / 1000, 1.0)
    score += weights.get("engagement", 0.25) * engagement_score
    
    # Recency
    try:
        signal_time = datetime.fromisoformat(signal.timestamp.replace('Z', '+00:00'))
        hours_ago = (datetime.now() - signal_time).total_seconds() / 3600
        recency_score = max(0, 1 - (hours_ago / 72))  # Decay over 72 hours
        score += weights.get("recency", 0.2) * recency_score
    except:
        pass
    
    # Source quality
    source_scores = {
        "hacker_news": 1.0,
        "whale_tracker": 0.9,
        "twitter": 0.8,
        "reddit": 0.75,
        "dexscreener": 0.7
    }
    source_score = source_scores.get(signal.source, 0.5)
    score += weights.get("source_quality", 0.15) * source_score
    
    return min(score, 1.0)


# ============================================
# SENTIMENT ANALYSIS
# ============================================

def analyze_sentiment(signals: List[IntelligenceSignal]) -> List[IntelligenceSignal]:
    """
    Analyze and assign sentiment to signals.
    
    Args:
        signals: List of signals
        
    Returns:
        Signals with sentiment scores
    """
    # Keywords for sentiment
    bullish_keywords = [
        'bullish', 'moon', 'lfg', 'up only', 'gm', 'green', 'pump',
        'growing', 'adoption', 'launch', 'partnership', 'breakthrough',
        'innovation', 'opportunity', 'profit', 'win', 'success'
    ]
    
    bearish_keywords = [
        'bearish', 'dump', 'rugged', 'scam', 'rekt', 'rug', 'death',
        'crash', 'loss', 'fail', 'hack', 'exploit', 'vulnerability',
        'concern', 'warning', 'risk', 'danger', 'problem'
    ]
    
    for signal in signals:
        text = (signal.title + " " + signal.content).lower()
        
        bullish_count = sum(1 for kw in bullish_keywords if kw in text)
        bearish_count = sum(1 for kw in bearish_keywords if kw in text)
        
        total = bullish_count + bearish_count
        
        if total == 0:
            signal.sentiment = "neutral"
            signal.sentiment_score = 0.5
        else:
            bullish_ratio = bullish_count / total
            
            if bullish_ratio > 0.6:
                signal.sentiment = "bullish"
                signal.sentiment_score = 0.5 + (bullish_ratio * 0.5)
            elif bullish_ratio < 0.4:
                signal.sentiment = "bearish"
                signal.sentiment_score = 0.5 - ((1 - bullish_ratio) * 0.5)
            else:
                signal.sentiment = "neutral"
                signal.sentiment_score = 0.5
    
    return signals


# ============================================
# SUMMARIZATION
# ============================================

def summarize(
    signals: List[IntelligenceSignal],
    max_items: int = 10
) -> Dict:
    """
    Generate summary from top signals.
    
    Args:
        signals: List of ranked signals
        max_items: Maximum items to include
        
    Returns:
        Summary dictionary
    """
    top_signals = signals[:max_items]
    
    # Extract key points
    key_points = []
    for signal in top_signals:
        points = _extract_key_points(signal)
        key_points.extend(points)
    
    # Count topics
    topic_counts = defaultdict(int)
    for signal in top_signals:
        for tag in signal.tags or []:
            topic_counts[tag] += 1
    
    # Calculate sentiment distribution
    sentiment_dist = {"bullish": 0, "neutral": 0, "bearish": 0}
    for signal in top_signals:
        sentiment_dist[signal.sentiment] = sentiment_dist.get(signal.sentiment, 0) + 1
    
    # Generate summary text
    summary_parts = []
    
    if top_signals:
        # Top signal
        top = top_signals[0]
        summary_parts.append(f"Top story: {top.title}")
        summary_parts.append(f"Source: {top.source} | Sentiment: {top.sentiment}")
    
    # Topics
    if topic_counts:
        top_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        topics_str = ", ".join([f"{t[0]} ({t[1]})" for t in top_topics])
        summary_parts.append(f"Hot topics: {topics_str}")
    
    # Sentiment
    total = sum(sentiment_dist.values())
    if total > 0:
        bullish_pct = sentiment_dist['bullish'] / total * 100
        bearish_pct = sentiment_dist['bearish'] / total * 100
        summary_parts.append(f"Sentiment: {bullish_pct:.0f}% bullish, {bearish_pct:.0f}% bearish")
    
    return {
        "summary": " | ".join(summary_parts),
        "key_points": key_points[:10],
        "top_topics": dict(topic_counts),
        "sentiment_distribution": sentiment_dist,
        "signal_count": len(top_signals),
        "generated_at": datetime.now().isoformat()
    }


def _extract_key_points(signal: IntelligenceSignal) -> List[str]:
    """Extract key points from a signal."""
    points = []
    
    # Extract sentences
    sentences = re.split(r'[.!?]', signal.content)
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 20:
            points.append(sentence[:100])
    
    return points[:3]


# ============================================
# FULL PIPELINE
# ============================================

def process(
    signals: List[IntelligenceSignal],
    config: Config = None,
    keywords: List[str] = None
) -> Dict:
    """
    Full processing pipeline: filter, deduplicate, rank, summarize.
    
    Args:
        signals: Raw intelligence signals
        config: Configuration object
        keywords: Keywords for relevance scoring
        
    Returns:
        Processed results dictionary
    """
    config = config or Config()
    keywords = keywords or config.get("sources.twitter.keywords", [])
    
    logger.info(f"Processing {len(signals)} signals...")
    
    # Step 1: Filter by relevance
    filtered = filter_relevance(signals, min_score=0.5, keywords=keywords)
    
    # Step 2: Deduplicate
    deduplicated = deduplicate(filtered, threshold=0.85)
    
    # Step 3: Analyze sentiment
    with_sentiment = analyze_sentiment(deduplicated)
    
    # Step 4: Rank
    ranked = rank_signals(with_sentiment)
    
    # Step 5: Summarize
    summary = summarize(ranked)
    
    # Save processed data
    processed_dir = Path(config.get("output.processed_dir", "data/processed"))
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = processed_dir / f"{timestamp}.json"
    
    result = {
        "timestamp": datetime.now().isoformat(),
        "input_count": len(signals),
        "output_count": len(ranked),
        "summary": summary,
        "signals": [s.to_dict() for s in ranked]
    }
    
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    logger.info(f"Processing complete: {output_file}")
    
    return result


# ============================================
# CLI
# ============================================

def main():
    """CLI entry point."""
    import argparse
    import asyncio
    
    parser = argparse.ArgumentParser(description="Process intelligence signals")
    parser.add_argument("--input", "-i", help="Input JSON file with raw signals")
    parser.add_argument("--rank", action="store_true", help="Rank signals")
    parser.add_argument("--summarize", action="store_true", help="Generate summary")
    parser.add_argument("--output", "-o", help="Output file path (JSON)")
    
    args = parser.parse_args()
    
    config = Config()
    
    # Load signals from file or gather fresh
    if args.input:
        with open(args.input, 'r') as f:
            data = json.load(f)
            signals = [IntelligenceSignal(**s) for s in data.get('signals', data)]
    else:
        # Gather fresh data
        async def gather_and_process():
            raw = await gather_all(config)
            return raw
        signals = asyncio.run(gather_and_process())
    
    # Process
    result = process(signals, config)
    
    # Output
    if args.rank:
        for i, s in enumerate(result['signals'][:10], 1):
            print(f"{i}. [{s['source']}] {s['title'][:50]}... (score: {s['relevance_score']:.2f})")
    
    if args.summarize:
        print(f"\n{result['summary']['summary']}")
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Saved to {args.output}")
    
    if not any([args.rank, args.summarize, args.output]):
        print(f"Processed {result['output_count']} signals")
        print(f"Summary: {result['summary']['summary']}")


if __name__ == "__main__":
    main()
