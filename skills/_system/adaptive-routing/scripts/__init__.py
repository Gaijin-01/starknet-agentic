#!/usr/bin/env python3
"""
Adaptive Routing Skill for Clawdbot
Intent-based skill router with confidence scoring.
"""

from .router import AdaptiveRouter, RoutingResult, SkillType

__version__ = "1.0.0"
__all__ = ["AdaptiveRouter", "RoutingResult", "SkillType"]
