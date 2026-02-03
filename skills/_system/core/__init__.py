"""
Core Skill - Unified orchestrator, config, and agent management.

Combines: claude-proxy, orchestrator, config, mcporter
"""

__version__ = "1.0.0"
__author__ = "Clawd"

# Import key components
from .main import Config, AdaptiveRouter, ClaudeProxy
from .tools import TOOL_DEFINITIONS
from .executor import ToolExecutor

__all__ = ["Config", "AdaptiveRouter", "ClaudeProxy", "TOOL_DEFINITIONS", "ToolExecutor"]
