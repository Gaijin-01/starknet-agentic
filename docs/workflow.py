#!/usr/bin/env python3
"""
Master Workflow: Research → Style → Generate → Optimize → Queue → Post
Usage: python3 workflow.py "<query>" [--type gm|news|insight]

Chain: research → style-learner → post-generator → x-algorithm-optimizer → queue-manager → bird
"""

import sys
import json
import subprocess
import os
from pathlib import Path
from datetime import datetime

SKILLS_DIR = Path.home() / "clawd" / "skills"
CONFIG_FILE = SKILLS_DIR / "config" / "config.json"

def load_config():
    """Load centralized config"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}

def run_script(skill, script, args, capture=True):
    """Run a skill script and return output"""
    script_path = SKILLS_DIR / skill / "scripts" / f"{script}.py"
    cmd = ["python3", str(script_path)] + args
    result = subprocess.run(cmd, capture_output=capture, text=True)
    if capture:
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    return "", "", 0

def log_step(step, message, emoji="🔧"):
    """Log workflow step"""
    print(f"\n{emoji} [{step}] {message}")
    print("-" * 40)

def research_topic(query, max_results=5):
    """Research a topic using Brave API"""
    log_step("RESEARCH", f"Investigating: {query}")
    output, err, code = run_script("research", "research", ["--query", query, "--max", str(max_results)])
    if code == 0:
        try:
            data = json.loads(output)
            results = data.get("results", [])
            print(f"   📚 Found {len(results)} sources")
            return results
        except json.JSONDecodeError:
            print(f"   ⚠️ Raw output: {output[:200]}")
    return []

def analyze_style(context=""):
    """Use style-learner to get current persona style"""
    log_step("STYLE", "Analyzing persona style")
    output, err, code = run_script("style-learner", "main", ["analyze", "--format", "json"])
    if code == 0:
        try:
            style = json.loads(output)
            print(f"   🎭 Persona: {style.get('name', 'unknown')}")
            print(f"   📝 Tone: {', '.join(style.get('tone', []))}")
            return style
        except:
            pass
    return {}

def generate_post(content_type, context="", style=None):
    """Generate content using post-generator with persona"""
    log_step("GENERATE", f"Creating {content_type} post")
    
    args = ["generate", "--type", content_type]
    if context:
        args.extend(["--context", context])
    if style:
        args.extend(["--style", json.dumps(style)])
    
    output, err, code = run_script("post-generator", "post_generator", args)
    if code == 0:
        print(f"   ✍️  Generated: {output[:100]}...")
        return output
    return None

def optimize_content(content):
    """Score and optimize content with x-algorithm-optimizer"""
    log_step("OPTIMIZE", "Scoring for X algorithm")
    
    # Get config weights
    config = load_config()
    weights = config.get("algorithm", {}).get("weights", {})
    
    output, err, code = run_script("x-algorithm-optimizer", "algorithm_scorer", [
        "--score", content,
        "--type", "text",
        "--json"
    ])
    
    if code == 0:
        try:
            score_data = json.loads(output)
            score = score_data.get("final_score", 0)
            print(f"   📊 Score: {score:.2f}")
            return score_data.get("optimized_content", content)
        except:
            print(f"   📊 Raw: {output[:200]}")
    
    return content

def add_to_queue(content, content_type):
    """Add content to queue"""
    log_step("QUEUE", f"Adding {content_type} to queue")
    
    output, err, code = run_script("queue-manager", "queue_manager", [
        "add",
        "--content", content,
        "--type", content_type,
        "--timestamp"
    ])
    
    if code == 0:
        print(f"   ✅ {output}")
        return True
    return False

def get_current_hour():
    """Get current UTC hour for peak hours check"""
    return datetime.utcnow().hour

def is_peak_hour(config):
    """Check if current time is in peak hours"""
    peak_hours = config.get("x", {}).get("peak_hours", [])
    current_hour = get_current_time()
    
    for hour_range in peak_hours:
        start, end = hour_range.split("-")
        start_h, end_h = int(start.split(":")[0]), int(end.split(":")[0])
        if start_h <= current_hour < end_h:
            return True
    return False

def post_to_x(content):
    """Post content to X using bird"""
    log_step("POST", "Publishing to X")
    output, err, code = run_script("bird", "tweet", [content])
    if code == 0:
        print(f"   🐦 Posted: {output}")
        return True
    return False

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\n💡 Examples:")
        print("   python3 workflow.py \"starknet news\" --type news")
        print("   python3 workflow.py \"bitcoin analysis\" --type insight")
        print("   python3 workflow.py \"gm crypto\" --type gm")
        return

    query = sys.argv[1]
    content_type = "insight"  # Default
    
    for i, arg in enumerate(sys.argv):
        if arg == "--type" and i+1 < len(sys.argv):
            content_type = sys.argv[i+1]

    print("\n🚀 Master Workflow Started")
    print(f"   Query: {query}")
    print(f"   Type: {content_type}")
    print(f"   Time: {get_current_hour()} UTC")
    print("=" * 50)

    config = load_config()
    
    # Check peak hours
    if not is_peak_hour(config):
        print(f"\n⚠️  Warning: Not peak hours. Consider waiting.")
    
    # Step 1: Research
    results = research_topic(query, max_results=5)
    
    # Step 2: Get Style
    style = analyze_style()
    
    # Step 3: Generate
    context = json.dumps(results) if results else ""
    content = generate_post(content_type, context, style)
    
    if content:
        # Step 4: Optimize
        optimized = optimize_content(content)
        
        # Step 5: Queue
        add_to_queue(optimized, content_type)
        
        # Step 6: Optional - Post immediately
        if "--post" in sys.argv:
            post_to_x(optimized)
    
    print("\n✅ Workflow Complete!")

def get_current_hour():
    return datetime.utcnow().hour

if __name__ == "__main__":
    main()
