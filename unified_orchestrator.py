#!/usr/bin/env python3
"""
Unified Skill Orchestrator for Claude-Proxy Bot
Combines: Skill Routing + Model Tier Selection + Execution

Flow:
1. Message → AdaptiveRouter (skill selection)
2. Message → Classifier (model tier selection)
3. Execute skill with appropriate model tier
"""

import re
import json
import subprocess
import sys
import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Literal
from enum import Enum
from pathlib import Path


# ============================================================
# SKILL TYPES
# ============================================================

class SkillType(Enum):
    PRICES = "prices"
    RESEARCH = "research"
    POST_GENERATOR = "post-generator"
    STYLE_LEARNER = "style-learner"
    CAMSNAP = "camsnap"
    SONGSEE = "songsee"
    MCPORTER = "mcporter"
    QUEUE_MANAGER = "queue-manager"
    CLAUDE_PROXY = "claude-proxy"
    ADAPTIVE_ROUTING = "adaptive-routing"
    BIRD = "bird"  # X/Twitter CLI
    X_ALGORITHM_OPTIMIZER = "x-algorithm-optimizer"
    SYSTEM_MANAGER = "system-manager"
    # Consolidated skills (2026-01-30)
    CORE = "core"
    INTELLIGENCE = "intelligence"
    PUBLISHER = "publisher"
    SYSTEM = "system"
    # Additional skills
    BLOCKCHAIN_DEV = "blockchain-dev"
    CRYPTO_TRADING = "crypto-trading"
    CT_INTELLIGENCE = "ct-intelligence"
    EDITOR = "editor"
    MULTI_LAYER_STYLE = "multi-layer-style"
    ORCHESTRATOR = "orchestrator"
    SKILL_EVOLVER = "skill-evolver"
    STARKNET_PY = "starknet-py"
    STARKNET_PRIVACY = "starknet-privacy"
    TWITTER_API = "twitter-api"


# ============================================================
# MODEL TIER CLASSIFIER (from classifier.py)
# ============================================================

COMPLEXITY_INDICATORS = {
    # High complexity (70-100)
    "architectural": 30, "system design": 30, "distributed systems": 35,
    "scalability": 30, "microservices": 30, "comprehensive analysis": 30,
    "research": 25, "trade-offs": 25, "performance optimization": 30,
    "security audit": 30, "deep dive": 30, "root cause": 25,
    # Medium complexity (30-70)
    "function": 15, "class": 15, "api": 15, "debug": 15, "implement": 18,
    "create": 12, "analyze": 20, "optimize": 20, "generate": 12,
    # Simple (1-30)
    "what is": 5, "who is": 5, "define": 6, "hello": 2, "thanks": 2,
}

TIER_PROMPTS = {
    "fast": "Be concise. Answer in 1-2 sentences.",
    "standard": "Be thorough but efficient. Provide complete answers.",
    "deep": "Think step by step. Provide detailed analysis with reasoning.",
}


@dataclass
class TierResult:
    score: int
    tier: Literal["fast", "standard", "deep"]
    model: str
    system_prompt: str


def classify_tier(query: str) -> TierResult:
    """Classify query complexity for model tier selection."""
    if not query:
        return TierResult(10, "fast", "MiniMax-M2.1-Fast", TIER_PROMPTS["fast"])
    
    query_lower = query.lower()
    score = 10
    
    for indicator, points in COMPLEXITY_INDICATORS.items():
        if indicator in query_lower:
            score += points
    
    # Length adjustment
    word_count = len(query.split())
    if word_count < 5:
        score -= 5
    elif word_count > 50:
        score += 5
    
    score = max(1, min(100, score))
    
    if score < 30:
        return TierResult(score, "fast", "MiniMax-M2.1-Fast", TIER_PROMPTS["fast"])
    elif score <= 70:
        return TierResult(score, "standard", "MiniMax-M2.1", TIER_PROMPTS["standard"])
    else:
        return TierResult(score, "deep", "MiniMax-M2.1-Deep", TIER_PROMPTS["deep"])


# ============================================================
# SKILL ROUTER
# ============================================================

SKILL_PATTERNS = {
    SkillType.PRICES: [
        r'\b(price|цена|курс|btc|eth|sol|strk|token|coin)\b',
        r'\b(market|рынок|pump|dump|moon)\b',
        r'\\$([A-Za-z]+)',
    ],
    SkillType.RESEARCH: [
        r'\b(research|исследуй|find|search|новости|news)\b',
        r'\b(what is|что такое|explain|объясни)\b',
        r'\b(анализ|analysis|report|отчет)\b',
    ],
    SkillType.POST_GENERATOR: [
        r'\b(post|пост|tweet|твит|write-напиши)\b',
        r'\b(thread|тред|content|контент)\b',
        r'\b(generate-сгенерируй)\b',
    ],
    SkillType.STYLE_LEARNER: [
        r'\b(style|стиль|tone|тон|voice)\b',
        r'\b(learn|учись|mimic|копируй)\b',
        r'\b(persona|персона)\b',
    ],
    SkillType.CAMSNAP: [
        r'\b(camera|камера|photo|фото|snap|screenshot)\b',
        r'\b(capture|захват|image|изображение)\b',
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
    SkillType.BIRD: [
        r'\b(twitter|x\.com|tweet|твит)\b',
        r'\b(post|tweet|reply|quote|like)\b',
        r'\b(bird|bird CLI)\b',
    ],
    SkillType.X_ALGORITHM_OPTIMIZER: [
        r'\b(algorithm|алгоритм|optimize|оптимизировать)\b',
        r'\b(engagement|reach|охват)\b',
    ],
    SkillType.SYSTEM_MANAGER: [
        r'\b(включи|выключи|enable|disable)\b',
        r'\b(скилл|skill)\b',
        r'\b(забэкапь|backup|память|memory)\b',
        r'\b(статус|status|систем|system)\b',
        r'\b(перезагрузи|restart|reload)\b',
        r'\b(health|здоровье)\b',
    ],
}


@dataclass
class RoutingResult:
    skill: SkillType
    confidence: float
    params: Dict[str, Any]
    tier: TierResult
    fallback: Optional[SkillType] = None


class UnifiedRouter:
    """Combined skill + tier routing."""
    
    def __init__(self):
        self.compiled = {
            skill: [re.compile(p, re.IGNORECASE) for p in patterns]
            for skill, patterns in SKILL_PATTERNS.items()
        }
    
    def route(self, message: str, context: Optional[Dict] = None) -> RoutingResult:
        """Route message to skill + determine model tier."""
        # 1. Score skills
        scores: Dict[SkillType, float] = {}
        for skill, patterns in self.compiled.items():
            score = sum(len(p.findall(message)) * 0.3 for p in patterns)
            scores[skill] = min(score, 1.0)
        
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # 2. Select skill
        if ranked[0][1] < 0.1:
            best_skill = SkillType.CLAUDE_PROXY
            confidence = 0.5
        else:
            best_skill, confidence = ranked[0]
        
        fallback = ranked[1][0] if len(ranked) > 1 and ranked[1][1] > 0.1 else None
        
        # 3. Determine tier
        tier = classify_tier(message)
        
        # 4. Extract params
        params = self._extract_params(best_skill, message)
        
        return RoutingResult(
            skill=best_skill,
            confidence=confidence,
            params=params,
            tier=tier,
            fallback=fallback
        )
    
    def _extract_params(self, skill: SkillType, message: str) -> Dict[str, Any]:
        params = {"raw_message": message}
        
        if skill == SkillType.PRICES:
            tokens = re.findall(r'\\$([A-Za-z]+)', message)
            tokens += re.findall(r'\b(btc|eth|sol|strk|avax|matic)\b', message.lower())
            params["tokens"] = list(set(t.upper() for t in tokens))
            
        elif skill == SkillType.RESEARCH:
            params["query"] = message
            
        elif skill == SkillType.POST_GENERATOR:
            params["topic"] = message
            params["format"] = "tweet" if "tweet" in message.lower() else "post"
            
        elif skill == SkillType.CAMSNAP:
            params["command"] = "snap"
            params["camera"] = "default"
            
        elif skill == SkillType.MCPORTER:
            params["command"] = "list"
            
        elif skill == SkillType.SONGSEE:
            params["command"] = "identify"
            
        elif skill == SkillType.BIRD:
            # Detect Twitter/X links
            twitter_match = re.search(r'(twitter\.com|x\.com)/[a-zA-Z0-9_]+/status/(\d+)', message)
            if twitter_match:
                params["action"] = "respond_to_tweet"
                params["tweet_id"] = twitter_match.group(2)
                params["link"] = message
            else:
                params["action"] = "post"
                params["content"] = message
                
        elif skill == SkillType.X_ALGORITHM_OPTIMIZER:
            params["task"] = "optimize_engagement"
            
        elif skill == SkillType.SYSTEM_MANAGER:
            # Parse voice command
            msg_lower = message.lower()
            
            # Enable skill: "включи скилл research" or "включи research"
            match = re.search(r'включи\s+(?:скилл\s+)?(\w+)', msg_lower)
            if match:
                params["action"] = "skills_enable"
                params["skill"] = match.group(1)
            elif re.search(r'выключи\s+(?:скилл\s+)?(\w+)', msg_lower):
                match = re.search(r'выключи\s+(?:скилл\s+)?(\w+)', msg_lower)
                params["action"] = "skills_disable"
                params["skill"] = match.group(1)
            elif "статус" in msg_lower and "скилл" in msg_lower:
                params["action"] = "skills_list"
            elif "забэкапь" in msg_lower and "память" in msg_lower:
                params["action"] = "memory_backup"
            elif "перезагрузи" in msg_lower and "память" in msg_lower:
                params["action"] = "memory_reload"
            elif "очисти" in msg_lower and "память" in msg_lower:
                params["action"] = "memory_clean"
            elif "статус" in msg_lower or "состояние" in msg_lower:
                params["action"] = "system_status"
            elif "health" in msg_lower or "здоровье" in msg_lower:
                params["action"] = "system_health"
            elif "перезапусти" in msg_lower and "гейтвей" in msg_lower:
                params["action"] = "service_restart"
            else:
                params["action"] = "help"
            
        return params


# ============================================================
# SKILL EXECUTOR
# ============================================================

class SkillExecutor:
    """Execute skills with proper interfaces."""
    
    def __init__(self, skills_path: str = "/home/wner/clawd/skills"):
        self.skills_path = Path(skills_path)
        self.router = UnifiedRouter()
    
    def process(self, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Full processing pipeline: route + execute."""
        route = self.router.route(message, context)
        
        result = {
            "message": message[:100] + "..." if len(message) > 100 else message,
            "skill": route.skill.value,
            "confidence": round(route.confidence, 2),
            "tier": route.tier.tier,
            "model": route.tier.model,
            "score": route.tier.score,
            "params": route.params,
            "status": "pending",
            "output": None,
            "error": None,
        }
        
        try:
            output = self._execute_skill(route)
            result["status"] = "success"
            result["output"] = output
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            if route.fallback:
                result["fallback"] = route.fallback.value
        
        return result
    
    def _execute_skill(self, route: RoutingResult) -> Any:
        """Execute skill based on type."""
        skill = route.skill
        params = route.params
        
        # CLI-based skills
        if skill == SkillType.CAMSNAP:
            return self._run_cli_skill("camsnap", params)
        elif skill == SkillType.MCPORTER:
            return self._run_cli_skill("mcporter", params)
        elif skill == SkillType.SONGSEE:
            return self._run_cli_skill("songsee", params)
        
        # X/Twitter skills
        if skill == SkillType.BIRD:
            return self._execute_bird(params)
        elif skill == SkillType.X_ALGORITHM_OPTIMIZER:
            return self._execute_x_optimizer(params)
        
        # System management skills
        if skill == SkillType.SYSTEM_MANAGER:
            return self._execute_system_manager(params)
        
        # Python module skills
        skill_main = self.skills_path / skill.value / "scripts" / "main.py"
        if skill_main.exists():
            return self._run_python_skill(skill_main, params)
        
        # Fallback to claude-proxy
        return {"action": "delegate_to_llm", "params": params, "tier": route.tier.tier}
    
    def _execute_bird(self, params: Dict) -> Dict:
        """Execute X/Twitter actions via bird CLI."""
        action = params.get("action", "help")
        
        if action == "respond_to_tweet":
            # Generate comment + quote + nana_prompt for tweet (copy for review)
            tweet_id = params.get("tweet_id")
            link = params.get("link")
            
            comment = "Interesting perspective! Here's my take on this topic."
            quote = "Great point worth highlighting. This aligns with what I've been thinking about [relevant angle]."
            nana_prompt = f"""🐵 Nana Banana Persona Prompt:

You are Nana Banana - a witty, slightly chaotic crypto native who speaks in short, punchy takes.
Reply to: {link}
Your reply (under 280 chars):"""
            
            return {
                "action": "twitter_response_copy",
                "tweet_id": tweet_id,
                "link": link,
                "comment": comment,
                "quote": quote,
                "nana_prompt": nana_prompt,
                "status": "copy_ready",
                "copy_text": self._format_twitter_copy(tweet_id, link)
            }
        elif action == "post":
            return {
                "action": "post_tweet",
                "content": params.get("content", ""),
                "status": "ready_to_post"
            }
        else:
            return {"action": "bird_help", "available_actions": ["post", "respond_to_tweet", "reply", "like", "quote"]}
    
    def _execute_x_optimizer(self, params: Dict) -> Dict:
        """Optimize content for X algorithm."""
        return {
            "action": "optimize",
            "task": params.get("task", "general"),
            "recommendations": [
                "Add 1-2 relevant hashtags",
                "Keep under 280 characters for max reach",
                "Post during peak hours (6-9, 12-14, 18-21 UTC)",
                "Include a question to boost engagement"
            ],
            "best_practices": {
                "quote": "3.5x reach boost",
                "reply": "3.0x reach boost", 
                "repost": "2.0x reach boost",
                "like": "1.0x baseline"
            }
        }
    
    def _execute_system_manager(self, params: Dict) -> Dict:
        """Execute system management commands."""
        action = params.get("action", "help")
        
        # Build command for system-manager script
        script = self.skills_path / "system-manager" / "scripts" / "main.py"
        
        if not script.exists():
            return {"error": "system-manager not installed", "action": action}
        
        # Map actions to CLI args
        if action == "skills_enable":
            cmd = ["python3", str(script), "skills", "enable", params.get("skill", "")]
        elif action == "skills_disable":
            cmd = ["python3", str(script), "skills", "disable", params.get("skill", "")]
        elif action == "skills_list":
            cmd = ["python3", str(script), "skills", "list"]
        elif action == "memory_backup":
            cmd = ["python3", str(script), "memory", "backup"]
        elif action == "memory_reload":
            cmd = ["python3", str(script), "memory", "reload"]
        elif action == "memory_clean":
            cmd = ["python3", str(script), "memory", "clean"]
        elif action == "system_status":
            cmd = ["python3", str(script), "system", "status"]
        elif action == "system_health":
            cmd = ["python3", str(script), "system", "health"]
        elif action == "service_restart":
            cmd = ["python3", str(script), "service", "restart"]
        else:
            return {
                "action": "help",
                "available_commands": [
                    "включи скилл research",
                    "выключи скилл prices",
                    "статус скиллов",
                    "забэкапь память",
                    "перезагрузи память",
                    "очисти память",
                    "статус системы",
                    "health системы",
                    "перезапусти гейтвей"
                ]
            }
        
        # Run command
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return {
                "action": action,
                "success": result.returncode == 0,
                "output": result.stdout.strip(),
                "error": result.stderr.strip() if result.stderr else None
            }
        except Exception as e:
            return {"action": action, "error": str(e)}
    
    def _add_to_post_queue(self, params: Dict, prefix: str = "post") -> str:
        """Add content to post queue for later review/posting."""
        from datetime import datetime
        queue_dir = self.skills_path.parent / "post_queue" / "ready"
        queue_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.json"
        filepath = queue_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(params, f, indent=2)
        
        return str(filepath)
    
    def _format_twitter_copy(self, tweet_id: str, link: str) -> str:
        """Format Twitter response as copyable text with 3 separate copies."""
        from datetime import datetime
        
        comment_text = "Interesting perspective! Here's my take on this topic."
        quote_text = "Great point worth highlighting. This aligns with what I've been thinking about [relevant angle]."
        nana_prompt = """🐵 Nana Banana Persona Prompt:

You are Nana Banana - a witty, slightly chaotic crypto native who speaks in short, punchy takes. Your style:
- Minimal words, maximum impact
- Uses 🐵🍌 emojis sparingly
- Sarcastic but never mean
- Calls out nonsense directly
- Speaks like a friend, not a corporation

Reply to: {link}

Your reply (under 280 chars):""".format(link=link)
        
        return f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐦 TWITTER COPY - COMMENT (ID: {tweet_id})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 COMMENT:
«{comment_text}»
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐦 TWITTER COPY - QUOTE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔁 QUOTE:
«{quote_text}»
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🍌 NANA BANANA PROMPT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{nana_prompt}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 Copy each section above as needed.
⏰ Generated: {datetime.now().strftime('%H:%M')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    def _run_cli_skill(self, skill_name: str, params: Dict) -> Dict:
        """Run CLI-based skill."""
        script = self.skills_path / skill_name / "scripts" / "main.py"
        if not script.exists():
            return {"error": f"{skill_name} not installed"}
        
        cmd = params.get("command", "help")
        args = ["python3", str(script), cmd]
        
        # Add command-specific args
        if cmd == "snap" and "camera" in params:
            args.extend([params["camera"], "--out", "/tmp/snap.jpg"])
        elif cmd == "list":
            pass  # no extra args
        
        try:
            result = subprocess.run(args, capture_output=True, text=True, timeout=30)
            return {
                "success": result.returncode == 0,
                "output": result.stdout.strip(),
                "error": result.stderr.strip() if result.stderr else None
            }
        except subprocess.TimeoutExpired:
            return {"error": "timeout"}
        except Exception as e:
            return {"error": str(e)}
    
    def _run_python_skill(self, script: Path, params: Dict) -> Any:
        """Run Python skill via subprocess."""
        try:
            result = subprocess.run(
                ["python3", str(script), json.dumps(params)],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                try:
                    return json.loads(result.stdout)
                except:
                    return result.stdout.strip()
            return {"error": result.stderr}
        except Exception as e:
            return {"error": str(e)}


# ============================================================
# CRON JOB DEFINITIONS
# ============================================================

CRON_JOBS = {
    "price-check": {
        "schedule": "*/15 * * * *",
        "skill": SkillType.PRICES,
        "params": {"mode": "alert", "tokens": ["BTC", "ETH", "STRK"], "threshold": 5.0},
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
        "description": "Weekly style model retrain (Sunday 3AM)"
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
    "health-check": {
        "schedule": "*/5 * * * *",
        "skill": SkillType.CLAUDE_PROXY,
        "params": {"mode": "health"},
        "description": "Service health check every 5 min"
    }
}


def run_cron_job(job_name: str) -> Dict:
    """Execute a cron job by name."""
    if job_name not in CRON_JOBS:
        return {"error": f"Unknown job: {job_name}"}
    
    job = CRON_JOBS[job_name]
    executor = SkillExecutor()
    
    # Build message from params
    params = job["params"]
    if job["skill"] == SkillType.PRICES:
        message = f"check prices for {', '.join(params.get('tokens', []))}"
    elif job["skill"] == SkillType.RESEARCH:
        message = f"research digest for {', '.join(params.get('topics', []))}"
    elif job["skill"] == SkillType.POST_GENERATOR:
        message = f"generate auto post as {params.get('persona', 'default')}"
    elif job["skill"] == SkillType.QUEUE_MANAGER:
        message = f"queue cleanup max_age={params.get('max_age_hours', 24)}h"
    elif job["skill"] == SkillType.STYLE_LEARNER:
        message = "retrain style model"
    else:
        message = f"run {job_name}"
    
    result = executor.process(message)
    result["job"] = job_name
    result["schedule"] = job["schedule"]
    return result


def generate_crontab() -> str:
    """Generate crontab file content."""
    lines = [
        "# ============================================",
        "# Claude-Proxy Bot Cron Jobs",
        "# Generated by unified_orchestrator.py",
        "# Install: crontab /path/to/this/file",
        "# ============================================",
        "",
        "SHELL=/bin/bash",
        "PATH=/usr/local/bin:/usr/bin:/bin",
        "BOT_HOME=/home/wner/clawd",
        "LOG_DIR=/home/wner/clawd/logs",
        "",
    ]
    
    for name, job in CRON_JOBS.items():
        cmd = f"cd $BOT_HOME && python3 unified_orchestrator.py --job {name}"
        lines.append(f"# {job['description']}")
        lines.append(f"{job['schedule']} {cmd} >> $LOG_DIR/{name}.log 2>&1")
        lines.append("")
    
    # Add log rotation
    lines.append("# Log rotation - daily")
    lines.append("0 0 * * * find $LOG_DIR -name '*.log' -mtime +7 -delete")
    
    return "\n".join(lines)


# ============================================================
# CLI INTERFACE
# ============================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified Skill Orchestrator")
    parser.add_argument("--message", "-m", help="Process a message")
    parser.add_argument("--job", "-j", help="Run a cron job by name")
    parser.add_argument("--test-route", "-t", help="Test routing without execution")
    parser.add_argument("--generate-cron", "-g", action="store_true", help="Generate crontab")
    parser.add_argument("--list-jobs", "-l", action="store_true", help="List available jobs")
    parser.add_argument("--list-skills", "-s", action="store_true", help="List available skills")
    
    args = parser.parse_args()
    
    if args.generate_cron:
        print(generate_crontab())
        
    elif args.list_jobs:
        print("Available cron jobs:")
        for name, job in CRON_JOBS.items():
            print(f"  {name:20} {job['schedule']:20} {job['description']}")
            
    elif args.list_skills:
        print("Available skills:")
        for skill in SkillType:
            print(f"  {skill.value}")
            
    elif args.test_route:
        router = UnifiedRouter()
        result = router.route(args.test_route)
        print(json.dumps({
            "skill": result.skill.value,
            "confidence": round(result.confidence, 2),
            "tier": result.tier.tier,
            "model": result.tier.model,
            "score": result.tier.score,
            "params": result.params,
            "fallback": result.fallback.value if result.fallback else None
        }, indent=2, ensure_ascii=False))
        
    elif args.job:
        result = run_cron_job(args.job)
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        
    elif args.message:
        executor = SkillExecutor()
        result = executor.process(args.message)
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
