#!/usr/bin/env python3
"""
core - Unified core management skill

Merges: claude-proxy, orchestrator, config, mcporter
"""

import argparse
import json
import logging
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('core')


class Config:
    """Load and manage core configuration."""
    
    def __init__(self, config_path: str = None):
        base = Path(__file__).parent
        self.config_path = Path(config_path) if config_path else base / "config.yaml"
        self._load()
    
    def _load(self):
        if self.config_path.exists():
            with open(self.config_path) as f:
                import yaml
                self.data = yaml.safe_load(f) or {}
        else:
            self.data = {}
    
    @property
    def claude_proxy(self) -> Dict:
        return self.data.get("claude_proxy", {})
    
    @property
    def orchestrator(self) -> Dict:
        return self.data.get("orchestrator", {})
    
    @property
    def mcp(self) -> Dict:
        return self.data.get("mcp", {})
    
    @property
    def config(self) -> Dict:
        return self.data.get("config", {})


class SkillType(Enum):
    """Available skills for routing."""
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
    """Routing decision result."""
    skill: SkillType
    confidence: float
    params: Dict[str, Any]
    fallback: Optional[SkillType] = None
    reasoning: str = ""


# ============ CONFIG LOADER ============

class ConfigLoader:
    """Configuration management."""
    
    def __init__(self, config_dir: str = None):
        self.config_dir = Path(config_dir or Path.home() / ".config" / "clawdbot")
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def list(self) -> str:
        """List configuration keys."""
        keys = []
        for f in self.config_dir.glob("*.json"):
            with open(f) as fp:
                data = json.load(fp)
                for k in data.keys():
                    keys.append(f"{f.stem}.{k}")
        return "\n".join(keys) if keys else "No config found"
    
    def get(self, key: str) -> str:
        """Get config value."""
        parts = key.split(".")
        if len(parts) < 2:
            return f"Use format: section.key (e.g., llm.primary)"
        
        section = parts[0]
        config_file = self.config_dir / f"{section}.json"
        
        if config_file.exists():
            with open(config_file) as f:
                data = json.load(f)
                value = data
                for part in parts[1:]:
                    value = value.get(part, {})
                return json.dumps(value, indent=2) if isinstance(value, dict) else str(value)
        
        return f"Config not found: {section}"
    
    def add(self, key: str, value: str) -> str:
        """Add/update config value."""
        parts = key.split(".")
        if len(parts) < 2:
            return "Use format: section.key value"
        
        section = parts[0]
        config_file = self.config_dir / f"{section}.json"
        
        data = {}
        if config_file.exists():
            with open(config_file) as f:
                data = json.load(f)
        
        current = data
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        
        # Try to parse value
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            parsed = value
        
        current[parts[-1]] = parsed
        
        with open(config_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return f"✅ Set {key}"


# ============ MCP MANAGER ============

class MCPManager:
    """MCP server management."""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.mcp_config = self.config.mcp
    
    def _run(self, args: List[str]) -> Dict:
        """Run mcporter command."""
        cmd = ["mcporter"]
        cfg_path = self.mcp_config.get("config_path")
        if cfg_path:
            cmd.extend(["--config", str(cfg_path)])
        cmd.extend(args)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return {"success": result.returncode == 0, "output": result.stdout.strip(), "error": result.stderr.strip()}
        except FileNotFoundError:
            return {"success": False, "error": "mcporter not found"}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out"}
    
    def list_servers(self) -> str:
        """List MCP servers."""
        result = self._run(["list"])
        return result["output"] if result["success"] else f"Error: {result.get('error')}"
    
    def call_tool(self, tool: str, args: Dict = None) -> str:
        """Call an MCP tool."""
        call_args = ["call", tool, "--args", json.dumps(args or {})]
        result = self._run(call_args)
        return result["output"] if result["success"] else f"Error: {result.get('error')}"
    
    def daemon(self, action: str) -> str:
        """Control daemon."""
        result = self._run(["daemon", action])
        return f"Daemon {action}: {'OK' if result['success'] else result.get('error')}"


# ============ ROUTER ============

class AdaptiveRouter:
    """Intent-based skill router."""
    
    PATTERNS = {
        SkillType.PRICES: [r'\b(price|цена|курс|btc|eth|sol)\b', r'\$([\w]+)', r'\b(market|рынок|pump|moon)\b'],
        SkillType.RESEARCH: [r'\b(research|research|find|search|новости)\b', r'\b(what is|что такое|explain)\b'],
        SkillType.POST_GENERATOR: [r'\b(post|пост|tweet|твит|write)\b', r'\b(thread|тред|content)\b'],
        SkillType.STYLE_LEARNER: [r'\b(style|стиль|tone|тон|voice)\b', r'\b(learn|учись)\b'],
        SkillType.CAMSNAP: [r'\b(camera|камера|photo|фото|snap)\b'],
        SkillType.SONGSEE: [r'\b(song|песня|music|музыка|track)\b', r'\b(shazam|lyrics)\b'],
        SkillType.MCPORTER: [r'\b(mcp|server|сервер|connect)\b', r'\b(tool|инструмент)\b'],
        SkillType.QUEUE_MANAGER: [r'\b(queue|очередь|task|задача)\b', r'\b(schedule|расписание)\b'],
        SkillType.TWITTER_API: [r'\b(twitter|tweet|retweet)\b', r'\b(follow|mention)\b'],
        SkillType.CRYPTO_TRADING: [r'\b(whale|arbitrage|on-chain|tvl)\b', r'\b(dex|liquidity)\b'],
        SkillType.CT_INTELLIGENCE: [r'\b(competitor|trend|trending|viral)\b', r'\b(analysis|monitor)\b'],
        SkillType.ADAPTIVE_ROUTING: [r'\b(route|роут|routing)\b', r'\b(tier|уровень)\b'],
    }
    
    def __init__(self):
        self.compiled = {s: [re.compile(p, re.IGNORECASE) for p in patterns] for s, patterns in self.PATTERNS.items()}
    
    def route(self, message: str) -> RoutingResult:
        """Route message to skill."""
        scores = {}
        for skill, patterns in self.compiled.items():
            score = sum(len(p.findall(message)) * 0.3 for p in patterns)
            scores[skill] = min(score, 1.0)
        
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        best_skill, best_score = ranked[0]
        
        if best_score < 0.1:
            return RoutingResult(skill=SkillType.CLAUDE_PROXY, confidence=0.5, params={"message": message}, reasoning="Default routing")
        
        fallback = ranked[1][0] if len(ranked) > 1 and ranked[1][1] > 0.1 else None
        params = self._extract_params(best_skill, message)
        
        return RoutingResult(skill=best_skill, confidence=best_score, params=params, fallback=fallback, reasoning=f"Score: {best_score:.2f}")
    
    def _extract_params(self, skill: SkillType, message: str) -> Dict:
        """Extract skill-specific params."""
        params = {"raw_message": message}
        if skill == SkillType.PRICES:
            params["tokens"] = list(set(re.findall(r'\$([A-Za-z]+)', message) + re.findall(r'\b(btc|eth|sol|strk)\b', message.lower())))
        elif skill == SkillType.RESEARCH:
            params["query"] = message
        return params


# ============ CLAUDE PROXY ============

class ClaudeProxy:
    """Autonomous AI agent."""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.skills_path = Path.home() / "clawd" / "skills"
        self.memory_path = Path.home() / "clawd" / "memory"
        self.tasks_completed = 0
        self.errors = []
    
    def execute_task(self, task: str) -> Dict:
        """Execute a task."""
        logger.info(f"Executing: {task[:100]}...")
        start = time.time()
        
        try:
            # Route and execute
            router = AdaptiveRouter()
            route = router.route(task)
            
            output = f"Routed to: {route.skill.value} (conf: {route.confidence:.0%})"
            self.tasks_completed += 1
            
            return {"status": "success", "task": task, "output": output, "execution_time": time.time() - start}
        
        except Exception as e:
            self.errors.append({"task": task, "error": str(e)})
            return {"status": "error", "task": task, "error": str(e), "execution_time": time.time() - start}
    
    def analyze_all_skills(self) -> List[Dict]:
        """Analyze all skills."""
        results = []
        for skill_dir in self.skills_path.iterdir():
            if skill_dir.is_dir() and not skill_dir.name.startswith('.'):
                score = 60
                if (skill_dir / "SKILL.md").exists():
                    score += 20
                if (skill_dir / "scripts" / "main.py").exists():
                    score += 10
                if (skill_dir / "config.yaml").exists():
                    score += 10
                results.append({"name": skill_dir.name, "score": min(score, 100)})
        return results
    
    def interactive_mode(self):
        """Interactive CLI mode."""
        print("\n=== CORE AI AGENT ===")
        print("Type 'quit' to exit, 'status' for info.\n")
        
        while True:
            try:
                task = input("You: ").strip()
                if not task:
                    continue
                if task.lower() in ['quit', 'exit', 'q']:
                    print("Bye!")
                    break
                if task.lower() == 'status':
                    print(f"Tasks: {self.tasks_completed}, Errors: {len(self.errors)}")
                    continue
                
                result = self.execute_task(task)
                print(f"\nAgent: {result.get('output', result.get('error'))}\n")
                
            except (EOFError, KeyboardInterrupt):
                print("\nBye!")
                break


# ============ CRON JOBS ============

CRON_JOBS = {
    "price-check": {"schedule": "*/15 * * * *", "skill": "prices", "description": "Check prices every 15 min"},
    "research-digest": {"schedule": "0 8,20 * * *", "skill": "research", "description": "Morning/evening research"},
    "auto-post": {"schedule": "0 9,13,18,22 * * *", "skill": "post-generator", "description": "Automated posts 4x daily"},
    "queue-cleanup": {"schedule": "0 */6 * * *", "skill": "queue-manager", "description": "Clean stale queue items"},
    "crypto-watch": {"schedule": "*/30 * * * *", "skill": "crypto-trading", "description": "Whale transactions"},
    "trend-scan": {"schedule": "0 */4 * * *", "skill": "ct-intelligence", "description": "Trending topics"},
}


# ============ COMMAND HANDLERS ============

def cmd_proxy(args):
    """Claude Proxy commands."""
    proxy = ClaudeProxy(args.config)
    
    if args.interactive:
        proxy.interactive_mode()
    
    elif args.task:
        result = proxy.execute_task(args.task)
        print(json.dumps(result, indent=2))
    
    elif args.analyze_all:
        analyses = proxy.analyze_all_skills()
        for a in sorted(analyses, key=lambda x: x['score'], reverse=True):
            status = "✅" if a['score'] >= 80 else "⚠️" if a['score'] >= 60 else "❌"
            print(f"{status} {a['name']}: {a['score']}/100")
    
    elif args.improve_skill:
        print(f"Would improve: {args.improve_skill}")
    
    elif args.autonomous:
        print(f"Autonomous mode for {args.hours}h with focus: {args.focus}")
    
    else:
        print("Proxy Status:")
        print(f"  Skills path: {proxy.skills_path}")
        print(f"  Tasks completed: {proxy.tasks_completed}")


def cmd_route(args):
    """Routing commands."""
    router = AdaptiveRouter()
    
    if args.test:
        result = router.route(args.test)
        print(f"\n=== ROUTING TEST ===")
        print(f"Message: {args.test}")
        print(f"Skill: {result.skill.value}")
        print(f"Confidence: {result.confidence:.0%}")
        print(f"Reasoning: {result.reasoning}")
        print(f"Params: {json.dumps(result.params, indent=2)}")
    
    elif args.skills:
        for skill in SkillType:
            print(f"  • {skill.value}")
    
    elif args.cron:
        print(f"# Generated crontab ({len(CRON_JOBS)} jobs)")
        for name, config in CRON_JOBS.items():
            print(f"{config['schedule']} # {config['description']}")
    
    elif args.job:
        if args.job in CRON_JOBS:
            print(f"Running job: {args.job}")
            print(f"Skill: {CRON_JOBS[args.job]['skill']}")
        else:
            print(f"Unknown job: {args.job}")
            print(f"Available: {', '.join(CRON_JOBS.keys())}")
    
    elif args.message:
        result = router.route(args.message)
        print(f"→ {result.skill.value} ({result.confidence:.0%})")
    
    else:
        print("Usage: route <message> OR route --test <message>")


def cmd_mcp(args):
    """MCP commands."""
    mcp = MCPManager(args.config)
    
    if args.action == "list":
        print(mcp.list_servers())
    elif args.action == "daemon":
        print(mcp.daemon(args.daemon_action))
    elif args.action == "call":
        tool_args = json.loads(args.tool_args) if args.tool_args else {}
        print(mcp.call_tool(args.tool, tool_args))
    else:
        print("Usage: mcp list | mcp daemon start|status|stop | mcp call <tool> --args '{}'")


def cmd_config(args):
    """Config commands."""
    loader = ConfigLoader()
    
    if args.action == "list":
        print(loader.list())
    elif args.action == "get":
        print(loader.get(args.key))
    elif args.action == "add":
        print(loader.add(args.key, args.value))
    else:
        print("Usage: config list | config get <key> | config add <key> <value>")


def cmd_check(args):
    """Full system check."""
    proxy = ClaudeProxy(args.config)
    router = AdaptiveRouter()
    
    print("\n" + "=" * 50)
    print("CORE SYSTEM CHECK")
    print("=" * 50)
    
    print("\n--- Skills Analysis ---")
    analyses = proxy.analyze_all_skills()
    grades = {"A": 0, "B": 0, "C": 0, "D": 0}
    for a in analyses:
        grade = "A" if a['score'] >= 80 else "B" if a['score'] >= 60 else "C" if a['score'] >= 40 else "D"
        grades[grade] = grades.get(grade, 0) + 1
        status = "✅" if a['score'] >= 80 else "⚠️" if a['score'] >= 60 else "❌"
        print(f"  {status} {a['name']}: {a['score']}/100")
    print(f"\nGrades: A={grades.get('A', 0)}, B={grades.get('B', 0)}, C={grades.get('C', 0)}, D={grades.get('D', 0)}")
    
    print("\n--- Routing Test ---")
    tests = ["price of bitcoin", "research ethereum", "gm"]
    for msg in tests:
        result = router.route(msg)
        print(f"  '{msg}' → {result.skill.value} ({result.confidence:.0%})")
    
    print("\n--- Cron Jobs ---")
    print(f"  {len(CRON_JOBS)} configured jobs")
    for name, config in list(CRON_JOBS.items())[:3]:
        print(f"  • {name}: {config['schedule']}")
    
    print("\n" + "=" * 50)


def cmd_status(args):
    """Quick status."""
    proxy = ClaudeProxy(args.config)
    print("\n--- CORE STATUS ---")
    print(f"Skills path: {proxy.skills_path}")
    print(f"Tasks done: {proxy.tasks_completed}")
    print(f"Errors: {len(proxy.errors)}")
    print(f"Cron jobs: {len(CRON_JOBS)}")


def main():
    parser = argparse.ArgumentParser(description="Core - Unified core management", formatter_class=argparse.RawDescriptionHelpFormatter)
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Proxy
    p_proxy = subparsers.add_parser("proxy", help="Claude Proxy commands")
    p_proxy.add_argument("--task", "-t", help="Execute task")
    p_proxy.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    p_proxy.add_argument("--analyze-all", action="store_true", help="Analyze all skills")
    p_proxy.add_argument("--improve-skill", help="Improve a skill")
    p_proxy.add_argument("--autonomous", action="store_true", help="Autonomous mode")
    p_proxy.add_argument("--hours", type=float, default=8, help="Hours for autonomous mode")
    p_proxy.add_argument("--focus", help="Focus areas (comma-separated)")
    
    # Route
    p_route = subparsers.add_parser("route", help="Message routing")
    p_route.add_argument("message", nargs="*", help="Message to route")
    p_route.add_argument("--test", "-t", help="Test routing")
    p_route.add_argument("--skills", action="store_true", help="List skills")
    p_route.add_argument("--cron", action="store_true", help="Generate crontab")
    p_route.add_argument("--job", help="Run cron job")
    
    # MCP
    p_mcp = subparsers.add_parser("mcp", help="MCP server management")
    p_mcp.add_argument("action", choices=["list", "daemon", "call"])
    p_mcp.add_argument("--daemon-action", choices=["start", "status", "stop"])
    p_mcp.add_argument("--tool", help="Tool selector")
    p_mcp.add_argument("--tool-args", help="JSON arguments")
    
    # Config
    p_cfg = subparsers.add_parser("config", help="Configuration management")
    p_cfg.add_argument("action", choices=["list", "get", "add"])
    p_cfg.add_argument("key", nargs="?", help="Config key")
    p_cfg.add_argument("value", nargs="?", help="Config value")
    
    # Check
    subparsers.add_parser("check", help="Full system check")
    
    # Status
    subparsers.add_parser("status", help="Quick status")
    
    # Health
    p_health = subparsers.add_parser("health", help="Health check")
    p_health.add_argument("--verbose", "-v", action="store_true")
    
    args = parser.parse_args()
    
    # Load config
    base = Path(__file__).parent
    config = Config(str(base / "config.yaml"))
    args.config = config
    
    if args.command == "proxy":
        cmd_proxy(args)
    elif args.command == "route":
        if args.message:
            args.message = " ".join(args.message)
        cmd_route(args)
    elif args.command == "mcp":
        cmd_mcp(args)
    elif args.command == "config":
        cmd_config(args)
    elif args.command == "check":
        cmd_check(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "health":
        print("✅ System healthy")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
