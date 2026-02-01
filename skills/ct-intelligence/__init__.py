"""
CT Intelligence Skill - Competitor tracking, viral analysis, and trend detection.
"""

import logging

__version__ = "1.0.0"
__author__ = "Evolver"

logger = logging.getLogger(__name__)

try:
    from scripts.viral import ViralAnalyzer
    from scripts.competitor import CompetitorTracker
    from scripts.trends import TrendDetector
    __all__ = ["ViralAnalyzer", "CompetitorTracker", "TrendDetector"]
except ImportError as e:
    logger.warning(f"CT Intelligence imports failed: {e}")
    __all__ = []
