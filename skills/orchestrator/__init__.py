"""
Adaptive Routing Skill - Intent-based skill router for claude-proxy bot.

Routes incoming messages to appropriate skills based on keyword patterns,
context awareness, and confidence scoring.
"""

__version__ = "1.0.0"
__author__ = "Evolver"

from .scripts.main import (
    SkillType,
    RoutingResult,
    AdaptiveRouter,
    SkillExecutor,
    CRON_JOBS,
    generate_crontab
)

__all__ = [
    "SkillType",
    "RoutingResult", 
    "AdaptiveRouter",
    "SkillExecutor",
    "CRON_JOBS",
    "generate_crontab"
]
