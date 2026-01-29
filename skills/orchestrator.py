#!/usr/bin/env python3
"""
Claude-Proxy Orchestrator

Central skill router + executor for Clawdbot.
Routes user queries to appropriate skills and manages cron jobs.
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# Setup logging
LOG_DIR = Path("/home/wner/clawd/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "orchestrator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("orchestrator")


# Routing patterns
ROUTING_TABLE = [
    (["$", "price", "курс", "стоимость"], "prices", "Token price lookup"),
    (["search", "news", "что такое", "исследуй"], "research", "Web search & research"),
    (["post", "tweet", "напиши", "tweet"], "post-generator", "Post generation"),
    (["style", "стиль", "persona", "голос"], "style-learner", "Style learning"),
    (["snap", "camera", "камера", "снимок"], "camsnap", "Camera snapshots"),
    (["mcp", "server"], "mcporter", "MCP server management"),
    (["song", "audio", "spectrogram"], "songsee", "Audio visualization"),
    (["route", "adaptive", "tier"], "adaptive-routing", "Query routing"),
]


def classify_query(query: str) -> dict:
    """
    Classify a query and determine which skill to use.
    
    Returns:
        dict with skill, confidence, and reasoning
    """
    query_lower = query.lower()
    
    for patterns, skill, reason in ROUTING_TABLE:
        for pattern in patterns:
            if pattern in query_lower:
                return {
                    "skill": skill,
                    "confidence": 0.9,
                    "reason": reason,
                    "matched": pattern
                }
    
    # Default to claude-proxy
    return {
        "skill": "claude-proxy",
        "confidence": 1.0,
        "reason": "No pattern match - using default LLM",
        "matched": None
    }


def route_query(query: str) -> dict:
    """Full routing analysis for a query."""
    classification = classify_query(query)
    
    return {
        "query": query,
        "timestamp": datetime.now().isoformat(),
        "routing": classification,
        "model_tier": get_model_tier(query)
    }


def get_model_tier(query: str) -> str:
    """Determine model tier based on query complexity."""
    score = score_complexity(query)
    
    if score < 30:
        return "fast"
    elif score < 70:
        return "standard"
    else:
        return "deep"


def score_complexity(query: str) -> int:
    """Score query complexity (1-100)."""
    score = 50  # Base score
    
    # High complexity indicators
    high_complexity = ["design", "architecture", "scalable", "optimize", "research"]
    for word in high_complexity:
        if word in query.lower():
            score += 20
    
    # Medium complexity
    medium_complexity = ["write", "code", "fix", "debug", "analyze", "create"]
    for word in medium_complexity:
        if word in query.lower():
            score += 10
    
    # Low complexity (reductions)
    low_complexity = ["hi", "hello", "how are", "thanks", "?"]
    for phrase in low_complexity:
        if phrase in query.lower():
            score -= 15
    
    # Length adjustments
    if len(query.split()) > 10:
        score += 10
    elif len(query.split()) < 3:
        score -= 10
    
    return max(1, min(100, score))


def execute_skill(skill: str, query: str) -> str:
    """Execute a skill and return the result."""
    skill_path = Path(f"/home/wner/clawd/skills/{skill}/scripts/main.py")
    
    if not skill_path.exists():
        return f"Skill '{skill}' not found"
    
    try:
        result = subprocess.run(
            [sys.executable, str(skill_path), query],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.stdout.strip() if result.stdout else result.stderr.strip()
    except subprocess.TimeoutExpired:
        return f"Skill '{skill}' timed out"
    except Exception as e:
        return f"Skill '{skill}' error: {str(e)}"


# Cron job handlers
def job_price_check():
    """Run price check for tracked tokens."""
    logger.info("Running price check...")
    subprocess.run(
        [sys.executable, "/home/wner/clawd/skills/prices/scripts/prices.py"],
        capture_output=True
    )
    logger.info("Price check completed")


def job_research_digest():
    """Generate research digest."""
    logger.info("Running research digest...")
    subprocess.run(
        [sys.executable, "/home/wner/clawd/skills/research/scripts/research.py", "--digest"],
        capture_output=True
    )
    logger.info("Research digest completed")


def job_auto_post():
    """Generate and queue auto post."""
    logger.info("Running auto post...")
    subprocess.run(
        [sys.executable, "/home/wner/clawd/skills/post-generator/scripts/post_generator.py", "--auto"],
        capture_output=True
    )
    logger.info("Auto post completed")


def job_health_check():
    """Check service health."""
    logger.info("Running health check...")
    # Check if core services are running
    services = ["claud-proxy", "gateway"]
    for service in services:
        subprocess.run(
            ["systemctl", "is-active", service],
            capture_output=True
        )
    logger.info("Health check completed")


def job_queue_cleanup():
    """Clean up old queue entries."""
    logger.info("Running queue cleanup...")
    queue_dir = Path("/home/wner/clawd/post_queue")
    if queue_dir.exists():
        for f in queue_dir.glob("*.txt"):
            # Remove files older than 7 days
            if (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).days > 7:
                f.unlink()
    logger.info("Queue cleanup completed")


def job_backup():
    """Create daily backup."""
    logger.info("Running backup...")
    backup_file = f"/home/wner/clawd/memory-backup-{datetime.now().strftime('%Y%m%d-%H%M')}.tar.gz"
    subprocess.run(
        ["tar", "-czf", backup_file, "memory/"],
        cwd="/home/wner/clawd",
        capture_output=True
    )
    logger.info(f"Backup created: {backup_file}")


# Job registry
JOBS = {
    "price-check": job_price_check,
    "research-digest": job_research_digest,
    "auto-post": job_auto_post,
    "health-check": job_health_check,
    "queue-cleanup": job_queue_cleanup,
    "backup": job_backup,
}


def generate_crontab() -> str:
    """Generate crontab configuration."""
    return """# Claude-Proxy Cron Jobs
# Generated by orchestrator.py

# Environment
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin:/home/wner/.local/bin

# Price check every 15 minutes
*/15 * * * * /usr/bin/python3 /home/wner/clawd/skills/prices/scripts/prices.py >> /home/wner/clawd/logs/prices.log 2>&1

# Health check every 5 minutes
*/5 * * * * /usr/bin/python3 /home/wner/clawd/skills/orchestrator.py --job health-check >> /home/wner/clawd/logs/health.log 2>&1

# Auto posts - 4 times daily
0 9 * * * /usr/bin/python3 /home/wner/clawd/skills/post-generator/scripts/post_generator.py --auto >> /home/wner/clawd/logs/posts.log 2>&1
0 13 * * * /usr/bin/python3 /home/wner/clawd/skills/post-generator/scripts/post_generator.py --auto >> /home/wner/clawd/logs/posts.log 2>&1
0 18 * * * /usr/bin/python3 /home/wner/clawd/skills/post-generator/scripts/post_generator.py --auto >> /home/wner/clawd/logs/posts.log 2>&1
0 22 * * * /usr/bin/python3 /home/wner/clawd/skills/post-generator/scripts/post_generator.py --auto >> /home/wner/clawd/logs/posts.log 2>&1

# Research digests - twice daily
0 8 * * * /usr/bin/python3 /home/wner/clawd/skills/research/scripts/research.py --digest >> /home/wner/clawd/logs/research.log 2>&1
0 20 * * * /usr/bin/python3 /home/wner/clawd/skills/research/scripts/research.py --digest >> /home/wner/clawd/logs/research.log 2>&1

# Queue cleanup every 6 hours
0 */6 * * * /usr/bin/python3 /home/wner/clawd/skills/orchestrator.py --job queue-cleanup >> /home/wner/clawd/logs/maintenance.log 2>&1

# Daily backup at 4 AM
0 4 * * * /usr/bin/python3 /home/wner/clawd/skills/orchestrator.py --job backup >> /home/wner/clawd/logs/backup.log 2>&1

# Style model retrain - Sunday at 3 AM
0 3 * * 0 /usr/bin/python3 /home/wner/clawd/skills/style-learner/scripts/main.py --retrain >> /home/wner/clawd/logs/style.log 2>&1
"""


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Claude-Proxy Orchestrator - Skill router and job scheduler"
    )
    parser.add_argument(
        "--test-route",
        help="Test routing for a query"
    )
    parser.add_argument(
        "--job",
        choices=list(JOBS.keys()),
        help="Run a specific cron job"
    )
    parser.add_argument(
        "--generate-cron",
        action="store_true",
        help="Generate crontab configuration"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.test_route:
        routing = route_query(args.test_route)
        print(json.dumps(routing, indent=2, ensure_ascii=False))
    
    elif args.job:
        if args.job in JOBS:
            JOBS[args.job]()
            print(f"Job '{args.job}' completed")
        else:
            print(f"Unknown job: {args.job}")
            sys.exit(1)
    
    elif args.generate_cron:
        print(generate_crontab())
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
