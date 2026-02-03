#!/usr/bin/env python3
"""
Adaptive Router — Core routing logic for skill selection.
"""

import re
import json
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime


class SkillType(Enum):
    """Supported skill types for routing."""
    PRICES = "prices"
    RESEARCH = "research"
    POST_GENERATOR = "post-generator"
    STYLE_LEARNER = "style-learner"
    CAMSNAP = "camsnap"
    SONGSEE = "songsee"
    MCPORTER = "mcporter"
    QUEUE_MANAGER = "queue-manager"
    CLAUDE_PROXY = "claude-proxy"
    EDITOR = "editor"
    # System & Orchestration (added 2026-01-30)
    SKILL_EVOLVER = "skill-evolver"
    SYSTEM_MANAGER = "system-manager"
    WORKFLOW = "workflow"
    ORCHESTRATOR = "orchestrator"


@dataclass
class RoutingResult:
    """Result of routing decision."""
    skill: SkillType
    confidence: float
    params: Dict[str, Any] = field(default_factory=dict)
    fallback: Optional[SkillType] = None
    reasoning: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return {
            "skill": self.skill.value,
            "confidence": self.confidence,
            "params": self.params,
            "fallback": self.fallback.value if self.fallback else None,
            "reasoning": self.reasoning,
            "timestamp": self.timestamp
        }


@dataclass
class SkillConfig:
    """Configuration for a skill."""
    name: str
    keywords: List[str]
    patterns: List[str]
    priority: int = 0  # Higher = more specific, checked first


# Skill configurations with keywords and regex patterns
SKILL_CONFIGS: Dict[SkillType, SkillConfig] = {
    SkillType.PRICES: SkillConfig(
        name="prices",
        keywords=["price", "цена", "курс", "btc", "eth", "sol", "token", "coin", "market", "pump", "dump", "moon"],
        patterns=[r'\$([A-Za-z]+)', r'\b(btc|eth|sol|strk|avax|matic)\b'],
        priority=10
    ),
    SkillType.RESEARCH: SkillConfig(
        name="research",
        keywords=["research", "исследуй", "find", "search", "news", "анализ", "analysis", "отчет", "what is", "что такое"],
        patterns=[r'\b(what is|что такое)\b.*', r'\b(news|news)\b'],
        priority=8
    ),
    SkillType.POST_GENERATOR: SkillConfig(
        name="post-generator",
        keywords=["post", "пост", "tweet", "твит", "write", "напиши", "thread", "тред", "content", "контент", "generate"],
        patterns=[r'(post|tweet|thread|content)', r'(write|generate|create)'],
        priority=8
    ),
    SkillType.STYLE_LEARNER: SkillConfig(
        name="style-learner",
        keywords=["style", "стиль", "tone", "тон", "voice", "learn", "учись", "mimic", "persona"],
        patterns=[r'(style|tone|voice)', r'(learn|mimic)'],
        priority=5
    ),
    SkillType.CAMSNAP: SkillConfig(
        name="camsnap",
        keywords=["camera", "камера", "photo", "фото", "snap", "screenshot", "capture", "захват"],
        patterns=[r'(camera|photo|snap|screenshot|capture)'],
        priority=5
    ),
    SkillType.SONGSEE: SkillConfig(
        name="songsee",
        keywords=["song", "песня", "music", "музыка", "track", "трек", "playing", "играет", "shazam", "lyrics"],
        patterns=[r'(song|music|track|playing|shazam|lyrics)'],
        priority=5
    ),
    SkillType.MCPORTER: SkillConfig(
        name="mcporter",
        keywords=["mcp", "server", "сервер", "connect", "подключи", "tool", "инструмент", "integration"],
        patterns=[r'(mcp|server|connect|tool)'],
        priority=5
    ),
    SkillType.QUEUE_MANAGER: SkillConfig(
        name="queue-manager",
        keywords=["queue", "очередь", "task", "задача", "job", "schedule", "расписание", "pending"],
        patterns=[r'(queue|task|job|schedule|pending)'],
        priority=5
    ),
    SkillType.EDITOR: SkillConfig(
        name="editor",
        keywords=["edit", "редактируй", "rewrite", "перепиши", "style", "стиль", "transform", "transform"],
        patterns=[r'(edit|rewrite|transform)'],
        priority=7
    ),
    # System & Orchestration (added 2026-01-30)
    SkillType.SKILL_EVOLVER: SkillConfig(
        name="skill-evolver",
        keywords=["evolve", "improve", "optimize", "analyze", "audit", "fix", "refactor", "рефактор", "улучши"],
        patterns=[r'(evolve|improve|optimize|analyze|audit|fix|refactor)'],
        priority=8
    ),
    SkillType.SYSTEM_MANAGER: SkillConfig(
        name="system-manager",
        keywords=["system", "status", "health", "process", "cron", "gateway", "service", "restart"],
        patterns=[r'(system|status|health|process|cron|gateway|service|restart)'],
        priority=7
    ),
    SkillType.WORKFLOW: SkillConfig(
        name="workflow",
        keywords=["workflow", "pipeline", "step", "stage", "automation", "automate", "flow"],
        patterns=[r'(workflow|pipeline|step|stage|automation|automate)'],
        priority=6
    ),
    SkillType.ORCHESTRATOR: SkillConfig(
        name="orchestrator",
        keywords=["orchestrate", "coordinate", "route", "route", "dispatch", "delegate", "route"],
        patterns=[r'(orchestrate|coordinate|route|dispatch|delegate)'],
        priority=6
    ),
}


class AdaptiveRouter:
    """
    Intent-based skill router with keyword and regex pattern matching.
    
    Features:
    - Keyword-based scoring
    - Regex pattern matching
    - Confidence scoring (0.0-1.0)
    - Fallback to claude-proxy on low confidence
    - Multi-skill detection (returns top 3)
    """
    
    def __init__(self, config: Dict[SkillType, SkillConfig] = None):
        """
        Initialize router with optional custom config.
        
        Args:
            config: Optional skill configuration dict
        """
        self.config = config or SKILL_CONFIGS
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for each skill."""
        self.compiled_patterns: Dict[SkillType, List[re.Pattern]] = {}
        for skill_type, skill_config in self.config.items():
            patterns = []
            for pattern_str in skill_config.patterns:
                try:
                    patterns.append(re.compile(pattern_str, re.IGNORECASE))
                except re.error:
                    # Skip invalid patterns
                    continue
            self.compiled_patterns[skill_type] = patterns
    
    def route(self, message: str, context: Optional[Dict] = None) -> RoutingResult:
        """
        Route message to appropriate skill.
        
        Args:
            message: User input text
            context: Optional context (chat history, user prefs)
            
        Returns:
            RoutingResult with skill, confidence, params, and reasoning
        """
        if not message or not isinstance(message, str):
            return self._default_result("Empty or invalid message")
        
        message_lower = message.lower().strip()
        
        # Score each skill
        scores = self._score_all(message, message_lower)
        
        if not scores:
            return self._default_result("No matching skills found")
        
        # Sort by score
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        best_skill, best_score = ranked[0]
        fallback = None
        
        # Get fallback from 2nd place if score > 0.1
        if len(ranked) > 1 and ranked[1][1] > 0.1:
            fallback = ranked[1][0]
        
        # Confidence threshold check
        if best_score < 0.1:
            return RoutingResult(
                skill=SkillType.CLAUDE_PROXY,
                confidence=0.5,
                params={"message": message},
                fallback=None,
                reasoning=f"Low score ({best_score:.2f}), routing to general chat"
            )
        
        # Build reasoning
        reasoning = self._build_reasoning(best_skill, ranked)
        
        # Extract params
        params = self._extract_params(best_skill, message)
        
        return RoutingResult(
            skill=best_skill,
            confidence=min(best_score, 1.0),
            params=params,
            fallback=fallback,
            reasoning=reasoning
        )
    
    def _score_all(self, message: str, message_lower: str) -> Dict[SkillType, float]:
        """Score all skills against message."""
        scores: Dict[SkillType, float] = {}
        
        for skill_type, skill_config in self.config.items():
            score = 0.0
            
            # Keyword matching (weighted)
            for keyword in skill_config.keywords:
                if keyword in message_lower:
                    score += 0.1
                    # Exact word match bonus
                    if re.search(r'\b' + re.escape(keyword) + r'\b', message_lower):
                        score += 0.05
            
            # Pattern matching
            for pattern in self.compiled_patterns.get(skill_type, []):
                matches = pattern.findall(message)
                score += len(matches) * 0.2
            
            # Priority bonus (specific skills win)
            score += skill_config.priority * 0.01
            
            scores[skill_type] = score
        
        return scores
    
    def _extract_params(self, skill: SkillType, message: str) -> Dict[str, Any]:
        """Extract skill-specific parameters from message."""
        params = {"raw_message": message}
        
        if skill == SkillType.PRICES:
            # Extract token symbols
            tokens = re.findall(r'\$([A-Za-z]+)', message)
            tokens += re.findall(r'\b(btc|eth|sol|strk|avax|matic|ldo|crv|aave)\b', message.lower())
            params["tokens"] = list(set(tokens))
            params["action"] = "check"
            
        elif skill == SkillType.RESEARCH:
            # Extract search query
            query = re.sub(r'\b(what is|что такое|research|search)\b', '', message, flags=re.IGNORECASE)
            params["query"] = query.strip()
            params["action"] = "search"
            
        elif skill == SkillType.POST_GENERATOR:
            # Extract topic
            params["topic"] = message
            params["format"] = "tweet" if "tweet" in message.lower() else "post"
            params["action"] = "generate"
            
        elif skill == SkillType.EDITOR:
            # Extract text to edit
            params["text"] = message
            params["action"] = "edit"
            
        return params
    
    def _build_reasoning(self, best_skill: SkillType, ranked: List) -> str:
        """Build human-readable reasoning for routing decision."""
        config = self.config[best_skill]
        reasons = []
        
        for keyword in config.keywords[:3]:  # Top 3 keywords
            reasons.append(f"keyword:{keyword}")
        
        return f"Matched {best_skill.value} (conf: {ranked[0][1]:.2f}) — {', '.join(reasons)}"
    
    def _default_result(self, reason: str) -> RoutingResult:
        """Return default result when no match found."""
        return RoutingResult(
            skill=SkillType.CLAUDE_PROXY,
            confidence=0.5,
            params={},
            fallback=None,
            reasoning=reason
        )
    
    def route_batch(self, messages: List[str], context: Optional[Dict] = None) -> List[RoutingResult]:
        """
        Route multiple messages.
        
        Args:
            messages: List of messages
            context: Optional shared context
            
        Returns:
            List of RoutingResult for each message
        """
        return [self.route(msg, context) for msg in messages]


# Convenience function
def route(message: str, context: Optional[Dict] = None) -> RoutingResult:
    """Quick route function for simple usage."""
    router = AdaptiveRouter()
    return router.route(message, context)


if __name__ == "__main__":
    # CLI test
    import sys
    
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
    else:
        message = input("Enter message to route: ")
    
    router = AdaptiveRouter()
    result = router.route(message)
    
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
