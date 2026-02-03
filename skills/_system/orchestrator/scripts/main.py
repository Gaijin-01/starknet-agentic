#!/usr/bin/env python3
"""
Skill Orchestrator for Claude-Proxy Bot

Routes incoming messages to appropriate skills based on intent detection,
keyword patterns, and confidence scoring.
"""

import re
import json
import sys
import os
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum

# Add skill scripts path for imports
SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class SkillType(Enum):
    """Enumeration of available skills."""
    PRICES = "prices"
    RESEARCH = "research"
    POST_GENERATOR = "post-generator"
    STYLE_LEARNER = "style-learner"
    CAMSNAP = "camsnap"
    SONGSEE = "songsee"
    MCPORTER = "mcporter"
    QUEUE_MANAGER = "queue-manager"
    TWITTER_API = "twitter-api"
    CRYPTO_TRADING = "crypto-trading"
    CT_INTELLIGENCE = "ct-intelligence"
    CLAUDE_PROXY = "claude-proxy"
    ADAPTIVE_ROUTING = "adaptive-routing"


@dataclass
class RoutingResult:
    """Result of routing decision."""
    skill: SkillType
    confidence: float
    params: Dict[str, Any]
    fallback: Optional[SkillType] = None


class AdaptiveRouter:
    """
    Intent-based skill router.
    
    Uses keyword patterns + context for skill selection.
    Calculates confidence scores based on pattern matches.
    """
    
    # Keyword patterns for each skill
    PATTERNS = {
        SkillType.PRICES: [
            r'\b(price|цена|курс|btc|eth|sol|token|coin)\b',
            r'\b(market|рынок|pump|dump|moon)\b',
            r'\$([\w]+)',  # $BTC, $ETH format
        ],
        SkillType.RESEARCH: [
            r'\b(research|исследуй|find|search|новости|news)\b',
            r'\b(what is|что такое|explain|объясни)\b',
            r'\b(анализ|analysis|report|отчет)\b',
        ],
        SkillType.POST_GENERATOR: [
            r'\b(post|пост|tweet|твит|write|напиши)\b',
            r'\b(thread|тред|content|контент)\b',
            r'\b(generate|generate|create-создай)\b',
        ],
        SkillType.STYLE_LEARNER: [
            r'\b(style|стиль|tone|тон|voice)\b',
            r'\b(learn|учись|mimic|копируй)\b',
            r'\b(persona|персона|character)\b',
        ],
        SkillType.CAMSNAP: [
            r'\b(camera|камера|photo|фото|snap|screenshot)\b',
            r'\b(capture захват|image|изображение)\b',
        ],
        SkillType.SONGSEE: [
            r'\b(song|песня|music|музыка|track|трек)\b',
            r'\b(playing|играет|shazam|identify)\b',
            r'\b(lyrics|текст|artist|исполнитель)\b',
        ],
        SkillType.MCPORTER: [
            r'\b(mcp|server|сервер|connect|подключи)\b',
            r'\b(tool|инструмент|integration|интеграция)\b',
        ],
        SkillType.QUEUE_MANAGER: [
            r'\b(queue|очередь|task|задача|job|работа)\b',
            r'\b(schedule|расписание|pending|ожидает)\b',
        ],
        SkillType.TWITTER_API: [
            r'\b(twitter|tweet|retweet|quote)\b',
            r'\b(follow|mention|dm|dm)\b',
        ],
        SkillType.CRYPTO_TRADING: [
            r'\b(whale|whales|whale\s+activity|whale\s+tracking)\b',
            r'\b(arbitrage|arb)\b',
            r'\b(on-chain|chain|token\s+metrics|token\s+analytics)\b',
            r'\b(tvl|liquidity|volume|fees)\b',
            r'\b(dex|decentralized\s+exchange|uniswap|sushi)\b',
        ],
        SkillType.CT_INTELLIGENCE: [
            r'\b(competitor|trend|trending|viral)\b',
            r'\b(analysis|intelligence|monitor)\b',
        ],
        SkillType.ADAPTIVE_ROUTING: [
            r'\b(route|роут|routing)\b',
            r'\b(tier|уровень|fast|standard|deep)\b',
        ],
    }
    
    def __init__(self):
        """Compile regex patterns for efficient matching."""
        self.compiled_patterns = {
            skill: [re.compile(p, re.IGNORECASE) for p in patterns]
            for skill, patterns in self.PATTERNS.items()
        }
    
    def route(
        self,
        message: str,
        context: Optional[Dict] = None
    ) -> RoutingResult:
        """
        Route message to appropriate skill.
        
        Args:
            message: User input text
            context: Optional context (chat history, user prefs, etc.)
            
        Returns:
            RoutingResult with skill, confidence, and extracted params
        """
        scores: Dict[SkillType, float] = {}
        
        for skill, patterns in self.compiled_patterns.items():
            score = 0.0
            for pattern in patterns:
                matches = pattern.findall(message)
                score += len(matches) * 0.3
            scores[skill] = min(score, 1.0)
        
        # Sort by score descending
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        if ranked[0][1] < 0.1:
            # No clear match → default to claude-proxy (general chat)
            return RoutingResult(
                skill=SkillType.CLAUDE_PROXY,
                confidence=0.5,
                params={"message": message},
                fallback=None
            )
        
        best_skill, best_score = ranked[0]
        fallback = ranked[1][0] if len(ranked) > 1 and ranked[1][1] > 0.1 else None
        
        # Extract params based on skill type
        params = self._extract_params(best_skill, message)
        
        return RoutingResult(
            skill=best_skill,
            confidence=best_score,
            params=params,
            fallback=fallback
        )
    
    def _extract_params(self, skill: SkillType, message: str) -> Dict[str, Any]:
        """Extract skill-specific parameters from message."""
        params = {"raw_message": message}
        
        if skill == SkillType.PRICES:
            # Extract token symbols
            tokens = re.findall(r'\$([A-Za-z]+)', message)
            tokens += re.findall(r'\b(btc|eth|sol|strk|avax|matic)\b', message.lower())
            params["tokens"] = list(set(tokens))
            
        elif skill == SkillType.RESEARCH:
            # Extract search query
            params["query"] = message
            
        elif skill == SkillType.POST_GENERATOR:
            # Extract topic
            params["topic"] = message
            params["format"] = "tweet" if "tweet" in message.lower() else "post"
            
        elif skill == SkillType.CRYPTO_TRADING:
            # Extract trading parameters
            tokens = re.findall(r'\$([A-Za-z]+)', message)
            params["tokens"] = list(set(tokens))
            params["action"] = "analyze"
            if "whale" in message.lower():
                params["action"] = "whale"
            elif "arbitrage" in message.lower():
                params["action"] = "arbitrage"
                
        elif skill == SkillType.CT_INTELLIGENCE:
            params["query"] = message
            if "competitor" in message.lower():
                params["mode"] = "competitor"
            elif "trend" in message.lower() or "viral" in message.lower():
                params["mode"] = "trend"
            else:
                params["mode"] = "analyze"
        
        return params


class SkillExecutor:
    """
    Executes skills and manages result flow.
    
    Handles skill loading, execution, and fallback logic.
    """
    
    def __init__(self, skills_path: str = "/home/wner/clawd/skills"):
        self.skills_path = skills_path
        self.router = AdaptiveRouter()
    
    def execute(
        self,
        message: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Route and execute appropriate skill.
        
        Args:
            message: User input
            context: Optional context
            
        Returns:
            Execution result dict
        """
        route = self.router.route(message, context)
        
        result = {
            "skill": route.skill.value,
            "confidence": route.confidence,
            "params": route.params,
            "status": "pending",
            "output": None,
            "error": None
        }
        
        try:
            # Import and execute skill
            skill_module = self._load_skill(route.skill)
            if skill_module and hasattr(skill_module, 'execute'):
                output = skill_module.execute(route.params)
                result["status"] = "success"
                result["output"] = output
            elif skill_module:
                # Module loaded but no execute function
                result["status"] = "success"
                result["output"] = f"Skill {route.skill.value} loaded successfully"
            else:
                result["status"] = "skipped"
                result["error"] = f"Skill {route.skill.value} not yet implemented"
                
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            
            # Try fallback
            if route.fallback:
                result["fallback_attempted"] = route.fallback.value
        
        return result
    
    def _load_skill(self, skill: SkillType):
        """Dynamically load skill module."""
        import importlib.util
        
        skill_path = os.path.join(
            self.skills_path, 
            skill.value, 
            "scripts", 
            "main.py"
        )
        
        if not os.path.exists(skill_path):
            return None
            
        spec = importlib.util.spec_from_file_location(skill.value, skill_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


# Cron job configurations for automated tasks
CRON_JOBS = {
    "price-check": {
        "schedule": "*/15 * * * *",
        "skill": SkillType.PRICES,
        "params": {"mode": "alert", "threshold": 5.0},
        "description": "Check prices every 15 min, alert on 5% change"
    },
    "research-digest": {
        "schedule": "0 8,20 * * *",
        "skill": SkillType.RESEARCH,
        "params": {"mode": "daily", "topics": ["crypto", "starknet", "defi"]},
        "description": "Morning/evening research digest"
    },
    "style-update": {
        "schedule": "0 3 * * 0",
        "skill": SkillType.STYLE_LEARNER,
        "params": {"mode": "retrain"},
        "description": "Weekly style model retrain"
    },
    "queue-cleanup": {
        "schedule": "0 */6 * * *",
        "skill": SkillType.QUEUE_MANAGER,
        "params": {"mode": "gc", "max_age_hours": 24},
        "description": "Clean stale queue items every 6h"
    },
    "auto-post": {
        "schedule": "0 9,13,18,22 * * *",
        "skill": SkillType.POST_GENERATOR,
        "params": {"mode": "auto", "persona": "sefirotwatch"},
        "description": "Automated posts 4x daily"
    },
    "crypto-watch": {
        "schedule": "*/30 * * * *",
        "skill": SkillType.CRYPTO_TRADING,
        "params": {"mode": "whale", "min_value": 100000},
        "description": "Watch for whale transactions every 30 min"
    },
    "trend-scan": {
        "schedule": "0 */4 * * *",
        "skill": SkillType.CT_INTELLIGENCE,
        "params": {"mode": "trend"},
        "description": "Scan for trending topics every 4 hours"
    }
}


def generate_crontab() -> str:
    """Generate crontab entries for all jobs."""
    lines = [
        "# Claude-Proxy Bot Cron Jobs",
        "# Generated by adaptive-routing skill",
        "# Run: crontab <(python skills/orchestrator/scripts/main.py --generate-cron)",
        "",
    ]
    
    for job_name, config in CRON_JOBS.items():
        cmd = f"cd {SKILL_ROOT} && python skills/orchestrator/scripts/main.py --job {job_name}"
        lines.append(f"# {config['description']}")
        lines.append(f"{config['schedule']} {cmd}")
        lines.append("")
    
    return "\n".join(lines)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Adaptive Routing Skill - Intent-based skill router",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--job",
        help="Run specific cron job by name"
    )
    parser.add_argument(
        "--message", "-m",
        help="Process a message through the router"
    )
    parser.add_argument(
        "--generate-cron",
        action="store_true",
        help="Generate crontab entries for all cron jobs"
    )
    parser.add_argument(
        "--test-route", "-t",
        help="Test routing for a message without execution"
    )
    parser.add_argument(
        "--list-jobs",
        action="store_true",
        help="List all configured cron jobs"
    )
    parser.add_argument(
        "--skills-path",
        default="/home/wner/clawd/skills",
        help="Path to skills directory"
    )
    
    args = parser.parse_args()
    
    if args.generate_cron:
        print(generate_crontab())
        
    elif args.list_jobs:
        for name, config in CRON_JOBS.items():
            print(f"{name}:")
            print(f"  Schedule: {config['schedule']}")
            print(f"  Skill: {config['skill'].value}")
            print(f"  Description: {config['description']}")
            print()
        
    elif args.test_route:
        router = AdaptiveRouter()
        result = router.route(args.test_route)
        print(json.dumps({
            "skill": result.skill.value,
            "confidence": round(result.confidence, 3),
            "params": result.params,
            "fallback": result.fallback.value if result.fallback else None
        }, indent=2, ensure_ascii=False))
        
    elif args.job:
        if args.job in CRON_JOBS:
            config = CRON_JOBS[args.job]
            executor = SkillExecutor(args.skills_path)
            print(f"Executing job: {args.job}")
            print(f"Skill: {config['skill'].value}")
            print(f"Params: {json.dumps(config['params'], indent=2)}")
            
            # Attempt to execute
            result = executor.execute(
                f"Execute {args.job}",
                context=config["params"]
            )
            print(f"\nResult: {json.dumps(result, indent=2, default=str)}")
        else:
            print(f"Unknown job: {args.job}")
            print(f"Available jobs: {', '.join(CRON_JOBS.keys())}")
            
    elif args.message:
        executor = SkillExecutor(args.skills_path)
        result = executor.execute(args.message)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    else:
        parser.print_help()


if __name__ == "__main__":
    import argparse
    main()
