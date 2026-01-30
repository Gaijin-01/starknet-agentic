#!/usr/bin/env python3
"""
System Manager for Clawdbot
Manages skills, memory, and services via voice/text commands.
"""

#!/usr/bin/env python3
"""System Manager for Clawdbot - Skills, memory, and service management."""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


# Paths
CLAWDBOT_DIR = Path.home() / ".clawdbot"
CLAWDBOT_CONFIG = CLAWDBOT_DIR / "clawdbot.json"
SKILLS_DIR = Path.home() / "clawd" / "skills"
MEMORY_DIR = Path.home() / "clawd" / "memory"


class SystemManager:
    """System administration manager."""
    
    # Known skills
    ALL_SKILLS = [
        "prices", "research", "post-generator", "queue-manager",
        "style-learner", "camsnap", "mcporter", "songsee",
        "adaptive-routing", "claude-proxy", "x-algorithm-optimizer"
    ]
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load Clawdbot config."""
        if CLAWDBOT_CONFIG.exists():
            with open(CLAWDBOT_CONFIG) as f:
                return json.load(f)
        return {"skills": {"enabled": [], "disabled": []}}
    
    def _save_config(self):
        """Save Clawdbot config."""
        CLAWDBOT_DIR.mkdir(parents=True, exist_ok=True)
        with open(CLAWDBOT_CONFIG, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    # ============ SKILL MANAGEMENT ============
    
    def cmd_skills_list(self) -> str:
        """List all skills with status."""
        enabled = self.config.get("skills", {}).get("enabled", [])
        disabled = self.config.get("skills", {}).get("disabled", [])
        
        # Default: all enabled except explicitly disabled
        if not enabled and not disabled:
            enabled = [s for s in self.ALL_SKILLS]
        
        lines = ["=== SKILLS STATUS ==="]
        for skill in self.ALL_SKILLS:
            status = "✅" if skill in enabled else "❌"
            lines.append(f"{status} {skill}")
        lines.append(f"\nEnabled: {len(enabled)}")
        lines.append(f"Disabled: {len(disabled)}")
        return "\n".join(lines)
    
    def cmd_skills_enable(self, skill: str) -> str:
        """Enable a skill."""
        skill = skill.lower()
        if skill not in self.ALL_SKILLS:
            return f"Unknown skill: {skill}"
        
        enabled = self.config.setdefault("skills", {}).setdefault("enabled", [])
        disabled = self.config.setdefault("skills", {}).setdefault("disabled", [])
        
        if skill in enabled:
            return f"Skill '{skill}' already enabled"
        
        enabled.append(skill)
        if skill in disabled:
            disabled.remove(skill)
        
        self._save_config()
        return f"✅ Enabled: {skill}"
    
    def cmd_skills_disable(self, skill: str) -> str:
        """Disable a skill."""
        skill = skill.lower()
        if skill not in self.ALL_SKILLS:
            return f"Unknown skill: {skill}"
        
        enabled = self.config.setdefault("skills", {}).setdefault("enabled", [])
        disabled = self.config.setdefault("skills", {}).setdefault("disabled", [])
        
        if skill in disabled:
            return f"Skill '{skill}' already disabled"
        
        disabled.append(skill)
        if skill in enabled:
            enabled.remove(skill)
        
        self._save_config()
        return f"❌ Disabled: {skill}"
    
    # ============ MEMORY OPERATIONS ============
    
    def cmd_memory_backup(self) -> str:
        """Backup memory directory."""
        if not MEMORY_DIR.exists():
            return "Memory directory not found"
        
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_file = MEMORY_DIR.parent / f"memory-backup-{timestamp}.tar.gz"
        
        subprocess.run(
            ["tar", "-czf", str(backup_file), "memory/"],
            cwd=MEMORY_DIR.parent,
            capture_output=True
        )
        
        size = backup_file.stat().st_size
        return f"✅ Backup created: {backup_file.name} ({size} bytes)"
    
    def cmd_memory_restore(self, backup: str) -> str:
        """Restore from backup."""
        # Find backup
        backups = list(MEMORY_DIR.parent.glob("memory-backup-*.tar.gz"))
        if not backups:
            return "No backups found"
        
        if backup == "latest":
            backup_file = max(backups, key=lambda f: f.stat().st_mtime)
        else:
            backup_file = MEMORY_DIR.parent / backup
            if not backup_file.exists():
                return f"Backup not found: {backup}"
        
        # Extract
        subprocess.run(
            ["tar", "-xzf", str(backup_file), "-C", str(MEMORY_DIR.parent)],
            capture_output=True
        )
        
        return f"✅ Restored from: {backup_file.name}"
    
    def cmd_memory_clean(self, days: int = 7) -> str:
        """Clean old memory files."""
        if not MEMORY_DIR.exists():
            return "Memory directory not found"
        
        removed = 0
        for f in MEMORY_DIR.glob("*.md"):
            age = (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).days
            if age > days:
                f.unlink()
                removed += 1
        
        return f"✅ Removed {removed} files older than {days} days"
    
    def cmd_memory_reload(self) -> str:
        """Signal to reload memory (for next session)."""
        # Touch a reload marker
        marker = MEMORY_DIR / ".reload"
        marker.touch()
        return "✅ Memory reload scheduled for next session"
    
    # ============ SERVICE CONTROL ============
    
    def cmd_service_status(self) -> str:
        """Check service status."""
        # Check gateway
        result = subprocess.run(
            ["clawdbot", "gateway", "status"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return f"✅ Gateway: running\n{result.stdout}"
        else:
            return f"❌ Gateway: not running\n{result.stderr or 'Unknown status'}"
    
    def cmd_service_restart(self, service: str = "gateway") -> str:
        """Restart a service."""
        if service == "gateway":
            subprocess.run(["clawdbot", "gateway", "restart"], capture_output=True)
            return "🔄 Gateway restart initiated"
        return f"Unknown service: {service}"
    
    # ============ SYSTEM STATUS ============
    
    def cmd_system_status(self) -> str:
        """Show system status."""
        # Git status
        result = subprocess.run(
            ["git", "log", "--oneline", "-5"],
            cwd=SKILLS_DIR.parent,
            capture_output=True,
            text=True
        )
        commits = result.stdout.strip() if result.stdout else "No commits"
        
        # Disk usage
        result = subprocess.run(
            ["df", "-h", str(SKILLS_DIR.parent)],
            capture_output=True,
            text=True
        )
        disk = result.stdout.split("\n")[-2] if result.stdout else "Unknown"
        
        # Cron jobs
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        cron_count = len([l for l in result.stdout.split("\n") if l and not l.startswith("#")])
        
        return f"""=== SYSTEM STATUS ===
📦 Git: {commits.split(chr(10))[0] if commits else 'N/A'}
💾 Disk: {disk.split()[4] if disk else 'N%'}
⏰ Cron: {cron_count} jobs
🟢 Uptime: {datetime.now().strftime('%H:%M')}
"""
    
    def cmd_system_health(self) -> str:
        """Quick health check."""
        issues = []
        
        # Check skills
        for skill in ["prices", "research", "post-generator"]:
            skill_path = SKILLS_DIR / skill
            if not (skill_path / "SKILL.md").exists():
                issues.append(f"Missing SKILL.md: {skill}")
        
        # Check orchestrator
        orchestrator = SKILLS_DIR.parent / "unified_orchestrator.py"
        if not orchestrator.exists():
            issues.append("Missing unified_orchestrator.py")
        
        if issues:
            return "⚠️ ISSUES FOUND:\n" + "\n".join(f"  - {i}" for i in issues)
        else:
            return "✅ System healthy"


def main():
    parser = argparse.ArgumentParser(description="System Manager for Clawdbot")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Skills
    p_skills = subparsers.add_parser("skills", help="Skill management")
    p_skills.add_argument("action", choices=["list", "enable", "disable"])
    p_skills.add_argument("skill", nargs="?", help="Skill name")
    
    # Memory
    p_mem = subparsers.add_parser("memory", help="Memory operations")
    p_mem.add_argument("action", choices=["backup", "restore", "clean", "reload"])
    p_mem.add_argument("target", nargs="?", help="Backup file or days")
    
    # Service
    p_svc = subparsers.add_parser("service", help="Service control")
    p_svc.add_argument("action", choices=["status", "restart"])
    p_svc.add_argument("service", nargs="?", default="gateway")
    
    # System
    p_sys = subparsers.add_parser("system", help="System status")
    p_sys.add_argument("action", choices=["status", "health"])
    
    # Voice command parser (natural language)
    p_voice = subparsers.add_parser("voice", help="Parse voice command")
    p_voice.add_argument("command", nargs="*", help="Voice command")
    
    args = parser.parse_args()
    
    manager = SystemManager()
    
    if args.command == "skills":
        if args.action == "list":
            print(manager.cmd_skills_list())
        elif args.action == "enable":
            if args.skill:
                print(manager.cmd_skills_enable(args.skill))
            else:
                print("Usage: skills enable <skill_name>")
        elif args.action == "disable":
            if args.skill:
                print(manager.cmd_skills_disable(args.skill))
            else:
                print("Usage: skills disable <skill_name>")
    
    elif args.command == "memory":
        if args.action == "backup":
            print(manager.cmd_memory_backup())
        elif args.action == "restore":
            target = args.target or "latest"
            print(manager.cmd_memory_restore(target))
        elif args.action == "clean":
            days = int(args.target) if args.target else 7
            print(manager.cmd_memory_clean(days))
        elif args.action == "reload":
            print(manager.cmd_memory_reload())
    
    elif args.command == "service":
        if args.action == "status":
            print(manager.cmd_service_status())
        elif args.action == "restart":
            print(manager.cmd_service_restart(args.service))
    
    elif args.command == "system":
        if args.action == "status":
            print(manager.cmd_system_status())
        elif args.action == "health":
            print(manager.cmd_system_health())
    
    elif args.command == "voice":
        # Natural language command parsing
        cmd = " ".join(args.command).lower()
        
        if "включи" in cmd and "скилл" in cmd:
            skill = cmd.replace("включи", "").replace("скилл", "").strip()
            print(manager.cmd_skills_enable(skill))
        elif "выключи" in cmd and "скилл" in cmd:
            skill = cmd.replace("выключи", "").replace("скилл", "").strip()
            print(manager.cmd_skills_disable(skill))
        elif "статус" in cmd and "скилл" in cmd:
            print(manager.cmd_skills_list())
        elif "забэкапь" in cmd and "память" in cmd:
            print(manager.cmd_memory_backup())
        elif "перезагрузи" in cmd and "память" in cmd:
            print(manager.cmd_memory_reload())
        elif "очисти" in cmd and "память" in cmd:
            print(manager.cmd_memory_clean())
        elif "статус" in cmd and ("систем" in cmd or "состояние" in cmd):
            print(manager.cmd_system_status())
        elif "здоровье" in cmd or "health" in cmd:
            print(manager.cmd_system_health())
        elif "перезапусти" in cmd and "гейтвей" in cmd:
            print(manager.cmd_service_restart("gateway"))
        else:
            print("Unknown command. Try: включи скилл research, статус системы, забэкапь память")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
