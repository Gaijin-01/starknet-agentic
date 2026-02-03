#!/usr/bin/env python3
"""
system - Unified system management skill

Merges: system-manager, skill-evolver, adaptive-routing
"""

import argparse
import json
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class Config:
    """Load and manage system configuration."""
    
    def __init__(self, config_path: str = None):
        base = Path(__file__).parent
        self.config_path = Path(config_path) if config_path else base / "config.yaml"
        self._load()
    
    def _load(self):
        if self.config_path.exists():
            with open(self.config_path) as f:
                self.data = json.load(f) if self.config_path.suffix == '.json' else {}
                # Try YAML if JSON fails
                if not self.data and self.config_path.suffix in ['.yaml', '.yml']:
                    import yaml
                    with open(self.config_path) as f:
                        self.data = yaml.safe_load(f) or {}
        else:
            self.data = {}
    
    @property
    def system(self) -> Dict:
        return self.data.get("system", {})
    
    @property
    def evolve(self) -> Dict:
        return self.data.get("evolve", {})
    
    @property
    def routing(self) -> Dict:
        return self.data.get("routing", {})


@dataclass
class RoutingResult:
    """Message routing result."""
    skill: str
    confidence: float
    params: Dict
    fallback: Optional[str]
    reasoning: str
    timestamp: str


class SystemManager:
    """System administration manager."""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.clawdbot_dir = Path.home() / ".clawdbot"
        self.clawdbot_config = self.clawdbot_dir / "clawdbot.json"
        self.skills_dir = Path.home() / "clawd" / "skills"
        self.memory_dir = Path.home() / "clawd" / "memory"
    
    def _load_config(self) -> dict:
        """Load Clawdbot config."""
        if self.clawdbot_config.exists():
            with open(self.clawdbot_config) as f:
                return json.load(f)
        return {"skills": {"enabled": [], "disabled": []}}
    
    def _save_config(self):
        """Save Clawdbot config."""
        self.clawdbot_dir.mkdir(parents=True, exist_ok=True)
        with open(self.clawdbot_config, 'w') as f:
            json.dump(self.config._load() if hasattr(self.config, '_load') else {}, f, indent=2)
    
    # === SKILL MANAGEMENT ===
    
    def cmd_skills_list(self) -> str:
        """List all skills with status."""
        enabled = self._load_config().get("skills", {}).get("enabled", [])
        disabled = self._load_config().get("skills", {}).get("disabled", [])
        default = self.config.system.get("skills", {}).get("default_enabled", [])
        
        lines = ["=== SKILLS STATUS ==="]
        all_skills = set(default + enabled + disabled)
        
        for skill in sorted(all_skills):
            if skill in disabled:
                status = "❌"
            elif skill in enabled or not disabled:
                status = "✅"
            else:
                status = "➖"
            lines.append(f"{status} {skill}")
        
        lines.append(f"\nEnabled: {len([s for s in all_skills if s in enabled or (not enabled and s not in disabled)])}")
        return "\n".join(lines)
    
    def cmd_skills_enable(self, skill: str) -> str:
        """Enable a skill."""
        skill = skill.lower()
        cfg = self._load_config()
        enabled = cfg.setdefault("skills", {}).setdefault("enabled", [])
        disabled = cfg.setdefault("skills", {}).setdefault("disabled", [])
        
        if skill in enabled:
            return f"Skill '{skill}' already enabled"
        
        enabled.append(skill)
        if skill in disabled:
            disabled.remove(skill)
        
        with open(self.clawdbot_config, 'w') as f:
            json.dump(cfg, f, indent=2)
        
        return f"✅ Enabled: {skill}"
    
    def cmd_skills_disable(self, skill: str) -> str:
        """Disable a skill."""
        skill = skill.lower()
        cfg = self._load_config()
        enabled = cfg.setdefault("skills", {}).setdefault("enabled", [])
        disabled = cfg.setdefault("skills", {}).setdefault("disabled", [])
        
        if skill in disabled:
            return f"Skill '{skill}' already disabled"
        
        disabled.append(skill)
        if skill in enabled:
            enabled.remove(skill)
        
        with open(self.clawdbot_config, 'w') as f:
            json.dump(cfg, f, indent=2)
        
        return f"❌ Disabled: {skill}"
    
    # === MEMORY OPERATIONS ===
    
    def cmd_memory_backup(self) -> str:
        """Backup memory directory."""
        if not self.memory_dir.exists():
            return "Memory directory not found"
        
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_file = self.memory_dir.parent / f"memory-backup-{timestamp}.tar.gz"
        
        subprocess.run(
            ["tar", "-czf", str(backup_file), "memory/"],
            cwd=self.memory_dir.parent,
            capture_output=True
        )
        
        size = backup_file.stat().st_size
        return f"✅ Backup: {backup_file.name} ({size:,} bytes)"
    
    def cmd_memory_restore(self, backup: str) -> str:
        """Restore from backup."""
        backups = list(self.memory_dir.parent.glob("memory-backup-*.tar.gz"))
        if not backups:
            return "No backups found"
        
        if backup == "latest":
            backup_file = max(backups, key=lambda f: f.stat().st_mtime)
        else:
            backup_file = self.memory_dir.parent / backup
            if not backup_file.exists():
                return f"Backup not found: {backup}"
        
        subprocess.run(
            ["tar", "-xzf", str(backup_file), "-C", str(self.memory_dir.parent)],
            capture_output=True
        )
        
        return f"✅ Restored: {backup_file.name}"
    
    def cmd_memory_clean(self, days: int = 7) -> str:
        """Clean old memory files."""
        if not self.memory_dir.exists():
            return "Memory directory not found"
        
        removed = 0
        for f in self.memory_dir.glob("*.md"):
            age = (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).days
            if age > days:
                f.unlink()
                removed += 1
        
        return f"✅ Cleaned: {removed} files older than {days} days"
    
    # === SERVICE CONTROL ===
    
    def cmd_service_status(self) -> str:
        """Check service status."""
        result = subprocess.run(
            ["clawdbot", "gateway", "status"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return f"✅ Gateway: running\n{result.stdout}"
        return f"❌ Gateway: not running"
    
    def cmd_service_restart(self, service: str = "gateway") -> str:
        """Restart a service."""
        subprocess.run(["clawdbot", "gateway", "restart"], capture_output=True)
        return f"🔄 {service} restart initiated"
    
    # === SYSTEM STATUS ===
    
    def cmd_system_status(self) -> str:
        """Show system status."""
        result = subprocess.run(
            ["git", "log", "--oneline", "-3"],
            cwd=self.skills_dir.parent,
            capture_output=True,
            text=True
        )
        commits = result.stdout.strip() if result.stdout else "No changes"
        
        result = subprocess.run(
            ["df", "-h", str(self.skills_dir.parent)],
            capture_output=True,
            text=True
        )
        disk = result.stdout.split("\n")[-1] if result.stdout else "Unknown"
        
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        cron_count = len([l for l in result.stdout.split("\n") if l and not l.startswith("#")])
        
        return f"""=== SYSTEM STATUS ===
📦 Git: {commits.split(chr(10))[0] if commits else 'N/A'}
💾 Disk: {disk.split()[4] if disk else 'N%'}
⏰ Cron: {cron_count} jobs
🟢 Time: {datetime.now().strftime('%H:%M')}"""
    
    def cmd_system_health(self) -> str:
        """Quick health check."""
        issues = []
        
        # Check skills
        for skill in ["prices", "research", "post-generator"]:
            skill_path = self.skills_dir / skill
            if not (skill_path / "SKILL.md").exists():
                issues.append(f"Missing SKILL.md: {skill}")
        
        # Check orchestrator
        orchestrator = self.skills_dir.parent / "unified_orchestrator.py"
        if not orchestrator.exists():
            issues.append("Missing unified_orchestrator.py")
        
        if issues:
            return "⚠️ ISSUES:\n" + "\n".join(f"  - {i}" for i in issues)
        return "✅ System healthy"


class SkillEvolver:
    """Skill analysis and improvement."""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.skills_dir = Path.home() / "clawd" / "skills"
    
    def analyze_skill(self, skill: str) -> Dict:
        """Analyze a single skill."""
        skill_path = self.skills_dir / skill
        
        if not skill_path.exists():
            return {"error": f"Skill not found: {skill}"}
        
        score = 0
        issues = []
        suggestions = []
        
        # Check for SKILL.md
        if (skill_path / "SKILL.md").exists():
            score += 20
        else:
            issues.append("Missing SKILL.md")
            suggestions.append("Add documentation file")
        
        # Check scripts directory
        scripts_dir = skill_path / "scripts"
        if scripts_dir.exists():
            score += 20
            
            # Check for main.py
            if (scripts_dir / "main.py").exists():
                score += 10
                
                # Read and check for docstrings
                try:
                    with open(scripts_dir / "main.py") as f:
                        content = f.read()
                        if '"""' in content or "'''" in content:
                            score += 10
                        else:
                            issues.append("main.py missing docstrings")
                            suggestions.append("Add module docstring")
                except Exception:
                    pass
            else:
                issues.append("Missing scripts/main.py")
                suggestions.append("Add main.py entry point")
        else:
            issues.append("Missing scripts/ directory")
        
        # Check for config.yaml
        if (skill_path / "config.yaml").exists():
            score += 10
        else:
            suggestions.append("Consider adding config.yaml")
        
        # Check for tests
        if (skill_path / "test*.py").exists() or (skill_path / "tests").exists():
            score += 10
        else:
            suggestions.append("Consider adding tests")
        
        # Check Git status
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=skill_path,
            capture_output=True,
            text=True
        )
        uncommitted = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
        if uncommitted == 0:
            score += 20
        else:
            suggestions.append(f"{uncommitted} uncommitted changes")
        
        return {
            "skill": skill,
            "score": score,
            "grade": "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "D",
            "issues": issues,
            "suggestions": suggestions,
            "timestamp": datetime.now().isoformat()
        }
    
    def analyze_all(self) -> List[Dict]:
        """Analyze all skills."""
        results = []
        for skill in sorted(self.skills_dir.iterdir()):
            if skill.is_dir() and not skill.name.startswith('.'):
                result = self.analyze_skill(skill.name)
                results.append(result)
        return results


class AdaptiveRouter:
    """Message routing to skills."""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.routing_config = self.config.routing
    
    def route(self, message: str) -> RoutingResult:
        """Route a message to the best skill."""
        msg_lower = message.lower()
        
        # Check keywords for each skill
        skills = self.routing_config.get("skills", {})
        best_skill = "default"
        best_confidence = self.routing_config.get("confidence_threshold", 0.6)
        matched_keywords = []
        
        for skill_name, skill_config in skills.items():
            if skill_name == "default":
                continue
            
            keywords = skill_config.get("keywords", [])
            priority = skill_config.get("priority", 1)
            
            matches = sum(1 for kw in keywords if kw.lower() in msg_lower)
            
            if matches > 0:
                confidence = min(0.95, 0.5 + (matches * 0.1) + (priority / 20))
                
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_skill = skill_name
                    matched_keywords = [kw for kw in keywords if kw.lower() in msg_lower]
        
        return RoutingResult(
            skill=best_skill,
            confidence=best_confidence,
            params={"matched_keywords": matched_keywords},
            fallback="default" if best_skill != "default" else None,
            reasoning=f"Matched {len(matched_keywords)} keywords" if matched_keywords else "Default routing",
            timestamp=datetime.now().isoformat()
        )
    
    def route_batch(self, messages: List[str]) -> List[RoutingResult]:
        """Route multiple messages."""
        return [self.route(msg) for msg in messages]


def cmd_system(args):
    """System management commands."""
    manager = SystemManager(args.config)
    
    if args.action == "skills":
        if args.subaction == "list":
            print(manager.cmd_skills_list())
        elif args.subaction in ("enable", "disable"):
            if args.skill:
                if args.subaction == "enable":
                    print(manager.cmd_skills_enable(args.skill))
                else:
                    print(manager.cmd_skills_disable(args.skill))
            else:
                print(f"Usage: system skills {args.subaction} <skill_name>")
    
    elif args.action == "memory":
        if args.subaction == "backup":
            print(manager.cmd_memory_backup())
        elif args.subaction == "restore":
            target = args.target or "latest"
            print(manager.cmd_memory_restore(target))
        elif args.subaction == "clean":
            days = int(args.target) if args.target else 7
            print(manager.cmd_memory_clean(days))
    
    elif args.action == "service":
        if args.subaction == "status":
            print(manager.cmd_service_status())
        elif args.subaction == "restart":
            print(manager.cmd_service_restart(args.service or "gateway"))
    
    elif args.action == "status":
        print(manager.cmd_system_status())
    
    elif args.action == "health":
        print(manager.cmd_system_health())


def cmd_evolve(args):
    """Skill evolution commands."""
    evolver = SkillEvolver(args.config)
    
    if args.all:
        results = evolver.analyze_all()
        print(f"\n=== SKILL ANALYSIS ({len(results)} skills) ===\n")
        for r in results:
            print(f"{r['grade']} {r['skill']:<25} Score: {r['score']}/100")
        print()
    else:
        result = evolver.analyze_skill(args.skill)
        print(f"\n=== {result['skill'].upper()} ANALYSIS ===")
        print(f"Score: {result['score']}/100 ({result['grade']})")
        if result['issues']:
            print(f"\nIssues:")
            for i in result['issues']:
                print(f"  ⚠️ {i}")
        if result['suggestions']:
            print(f"\nSuggestions:")
            for s in result['suggestions']:
                print(f"  💡 {s}")
        print()


def cmd_route(args):
    """Routing commands."""
    router = AdaptiveRouter(args.config)
    
    if args.interactive:
        print("\n=== INTERACTIVE ROUTING ===")
        print("Type 'quit' to exit.\n")
        while True:
            try:
                msg = input("Message: ").strip()
                if msg.lower() in ['quit', 'exit', 'q']:
                    print("Bye!")
                    break
                if not msg:
                    continue
                result = router.route(msg)
                print(f"  → {result.skill} (conf: {result.confidence:.0%})")
                print()
            except (EOFError, KeyboardInterrupt):
                print("\nBye!")
                break
    
    elif args.batch:
        messages = []
        if args.file:
            with open(args.file) as f:
                messages = [line.strip() for line in f if line.strip()]
        
        if messages:
            print(f"Routing {len(messages)} messages...\n")
            results = router.route_batch(messages)
            for msg, result in zip(messages, results):
                print(f"[{result.skill}] {result.confidence:.0%} | {msg[:50]}")
    
    else:
        result = router.route(args.message)
        print(f"\n=== ROUTING RESULT ===")
        print(f"Skill:      {result.skill}")
        print(f"Confidence: {result.confidence:.0%}")
        print(f"Reasoning:  {result.reasoning}")
        print()


def cmd_check(args):
    """Full system check."""
    manager = SystemManager()
    evolver = SkillEvolver()
    router = AdaptiveRouter()
    
    print("\n" + "=" * 50)
    print("SYSTEM CHECK")
    print("=" * 50)
    
    print("\n--- System Status ---")
    print(manager.cmd_system_status())
    
    print("\n--- Health ---")
    print(manager.cmd_system_health())
    
    print("\n--- Skills ---")
    skills = evolver.analyze_all()
    grades = {"A": 0, "B": 0, "C": 0, "D": 0}
    for s in skills:
        grades[s['grade']] = grades.get(s['grade'], 0) + 1
    print(f"Skills analyzed: {len(skills)}")
    print(f"Grades: A={grades.get('A', 0)}, B={grades.get('B', 0)}, C={grades.get('C', 0)}, D={grades.get('D', 0)}")
    
    print("\n--- Routing Test ---")
    test_messages = ["price of bitcoin", "research ethereum", "gm"]
    for msg in test_messages:
        result = router.route(msg)
        print(f"  '{msg}' → {result.skill} ({result.confidence:.0%})")
    
    print("\n" + "=" * 50)


def main():
    parser = argparse.ArgumentParser(
        description="System - Unified system management",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # System management
    p_sys = subparsers.add_parser("system", help="System management")
    p_sys.add_argument("action", choices=["skills", "memory", "service", "status", "health"])
    p_sys.add_argument("subaction", nargs="?", help="Sub-action")
    p_sys.add_argument("skill", nargs="?", help="Skill name")
    p_sys.add_argument("--service", help="Service name")
    p_sys.add_argument("--target", help="Target (backup file or days)")
    
    # Skill evolution
    p_ev = subparsers.add_parser("evolve", help="Skill analysis and improvement")
    p_ev.add_argument("--skill", "-s", help="Skill name")
    p_ev.add_argument("--all", action="store_true", help="Analyze all skills")
    
    # Routing
    p_rt = subparsers.add_parser("route", help="Route a message")
    p_rt.add_argument("message", nargs="*", help="Message to route")
    p_rt.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    p_rt.add_argument("--batch", "-b", action="store_true", help="Batch mode")
    p_rt.add_argument("--file", "-f", help="File with messages")
    
    # Full check
    subparsers.add_parser("check", help="Full system check")
    
    # Health
    p_health = subparsers.add_parser("health", help="Health check")
    p_health.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Load config
    base = Path(__file__).parent
    config = Config(str(base / "config.yaml"))
    
    # Attach config to args for subcommands
    args.config = config
    
    if args.command == "system":
        cmd_system(args)
    elif args.command == "evolve":
        if not args.skill and not args.all:
            print("Usage: evolve --skill <name> OR evolve --all")
            skills_dir = Path.home() / "clawd" / "skills"
            for s in sorted(skills_dir.iterdir()):
                if s.is_dir() and not s.name.startswith('.'):
                    print(f"  - {s.name}")
        else:
            cmd_evolve(args)
    elif args.command == "route":
        if args.interactive:
            cmd_route(args)
        elif args.batch:
            cmd_route(args)
        elif args.message:
            args.message = " ".join(args.message)
            cmd_route(args)
        else:
            print("Usage: route 'message' OR route --interactive OR route --batch --file <file>")
    elif args.command == "check":
        cmd_check(args)
    elif args.command == "health":
        manager = SystemManager(config)
        print(manager.cmd_system_health())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
