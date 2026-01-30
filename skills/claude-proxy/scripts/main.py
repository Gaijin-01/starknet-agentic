#!/usr/bin/env python3
"""
claude-proxy main.py - Autonomous AI agent
Works as Claude's backup when he's unavailable
"""

#!/usr/bin/env python3
"""Claude-Proxy autonomous AI agent main module."""

import argparse
import json
import logging
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Local imports
from llm_client import LLMClient, ask
from reasoning import ReasoningEngine, reason
from code_gen import CodeGenerator, generate
from self_improve import SelfImprover, improve

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('claude-proxy')

MEMORY_PATH = Path.home() / 'clawd' / 'memory'
SKILLS_PATH = Path.home() / 'clawd' / 'skills'


class ClaudeProxy:
    """
    Autonomous AI agent that works as Claude's backup.
    
    Capabilities:
    - Task analysis and execution
    - Code generation and improvement
    - Skill management and evolution
    - Autonomous operation mode
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or self._load_config()
        self.llm = LLMClient(self.config.get('llm', {}))
        self.reasoning = ReasoningEngine(self.config.get('reasoning', {}))
        self.code_gen = CodeGenerator(self.config.get('code_gen', {}))
        self.improver = SelfImprover(self.config.get('self_improve', {}))
        self.session_start = datetime.now()
        self.tasks_completed = 0
        self.errors = []
        
    def _load_config(self) -> Dict:
        """Load configuration."""
        config_file = Path(__file__).parent.parent / 'references' / 'config.json'
        if config_file.exists():
            with open(config_file) as f:
                return json.load(f)
        return {
            'llm': {'primary': 'minimax', 'fallback': ['openai', 'ollama']},
            'reasoning': {'self_reflect': True, 'verbose': True},
            'code_gen': {'validate_syntax': True},
            'self_improve': {'dry_run': True, 'backup': True},
            'autonomous': {
                'max_tasks_per_hour': 20,
                'focus_areas': ['error-fixing', 'skill-improvement'],
                'alert_on_error': True
            }
        }
    
    def execute_task(self, task: str, context: str = "") -> Dict:
        """
        Execute a task using structured reasoning.
        
        Args:
            task: Task description
            context: Additional context
        
        Returns:
            Execution result with status and output
        """
        logger.info(f"Executing task: {task[:100]}...")
        start_time = time.time()
        
        try:
            # Analyze task
            result = self.reasoning.reason(task, context)
            
            # Determine action type
            task_lower = task.lower()
            
            if any(kw in task_lower for kw in ['generate', 'create', 'write', 'code']):
                # Code generation task
                output = self._handle_code_task(task, result)
            elif any(kw in task_lower for kw in ['improve', 'fix', 'update', 'optimize']):
                # Improvement task
                output = self._handle_improvement_task(task, result)
            elif any(kw in task_lower for kw in ['analyze', 'check', 'review', 'status']):
                # Analysis task
                output = self._handle_analysis_task(task, result)
            else:
                # General task - use reasoning result
                output = result.conclusion
            
            self.tasks_completed += 1
            
            return {
                'status': 'success',
                'task': task,
                'output': output,
                'confidence': result.confidence,
                'execution_time': time.time() - start_time
            }
            
        except Exception as e:
            logger.error(f"Task failed: {e}")
            self.errors.append({'task': task, 'error': str(e)})
            return {
                'status': 'error',
                'task': task,
                'error': str(e),
                'execution_time': time.time() - start_time
            }
    
    def _handle_code_task(self, task: str, reasoning_result) -> str:
        """Handle code generation tasks."""
        # Extract what needs to be generated
        code_result = self.code_gen.generate(task)
        
        if code_result.valid:
            return f"Generated {code_result.filename}:\n\n```{code_result.language}\n{code_result.code}\n```"
        else:
            return f"Code generation had issues: {code_result.validation_error}\n\n```\n{code_result.code}\n```"
    
    def _handle_improvement_task(self, task: str, reasoning_result) -> str:
        """Handle improvement tasks."""
        # Extract skill name from task
        import re
        skill_match = re.search(r'(\w+-\w+|\w+)(?:\s+skill)?', task)
        skill_name = skill_match.group(1) if skill_match else None
        
        if skill_name and (SKILLS_PATH / skill_name).exists():
            result = self.improver.improve_skill(skill_name)
            return f"Improvement result for {skill_name}:\n" + \
                   f"- Success: {result.success}\n" + \
                   f"- Changes: {', '.join(result.changes_made)}"
        else:
            return reasoning_result.conclusion
    
    def _handle_analysis_task(self, task: str, reasoning_result) -> str:
        """Handle analysis tasks."""
        task_lower = task.lower()
        
        if 'skill' in task_lower:
            # Skill analysis
            import re
            skill_match = re.search(r'(\w+-\w+|\w+)(?:\s+skill)?', task)
            if skill_match:
                skill_name = skill_match.group(1)
                if (SKILLS_PATH / skill_name).exists():
                    analysis = self.improver.analyze_skill(skill_name)
                    return f"Analysis of {skill_name}:\n" + \
                           f"- Score: {analysis.score}/100\n" + \
                           f"- Issues: {len(analysis.issues)}\n" + \
                           f"- Improvements: {len(analysis.improvements)}"
        
        return reasoning_result.conclusion
    
    def interactive_mode(self):
        """Run in interactive mode."""
        print("\n" + "="*60)
        print("  CLAUDE-PROXY - Autonomous AI Agent")
        print("  Type 'help' for commands, 'quit' to exit")
        print("="*60 + "\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if user_input.lower() == 'help':
                    self._print_help()
                    continue
                
                if user_input.lower() == 'status':
                    self._print_status()
                    continue
                
                # Execute as task
                result = self.execute_task(user_input)
                
                print(f"\nAgent: {result.get('output', result.get('error', 'No output'))}")
                print(f"[Confidence: {result.get('confidence', 0):.0%}, Time: {result.get('execution_time', 0):.1f}s]\n")
                
            except KeyboardInterrupt:
                print("\nInterrupted. Type 'quit' to exit.")
            except Exception as e:
                print(f"\nError: {e}\n")
    
    def autonomous_mode(self, 
                       hours: float = 8,
                       interval_minutes: int = 30,
                       focus: List[str] = None):
        """
        Run in fully autonomous mode.
        
        Args:
            hours: How long to run
            interval_minutes: Time between task cycles
            focus: Areas to focus on
        """
        focus = focus or self.config.get('autonomous', {}).get('focus_areas', [])
        end_time = datetime.now() + timedelta(hours=hours)
        
        logger.info(f"Starting autonomous mode for {hours}h")
        logger.info(f"Focus areas: {focus}")
        
        cycle = 0
        
        while datetime.now() < end_time:
            cycle += 1
            logger.info(f"\n{'='*40}\nAutonomous cycle {cycle}\n{'='*40}")
            
            try:
                # Determine tasks based on focus
                tasks = self._generate_autonomous_tasks(focus)
                
                for task in tasks[:3]:  # Max 3 tasks per cycle
                    result = self.execute_task(task['description'], task.get('context', ''))
                    
                    if result['status'] == 'error':
                        logger.warning(f"Task failed: {result.get('error')}")
                    else:
                        logger.info(f"Task completed: {task['description'][:50]}...")
                    
                    time.sleep(10)  # Brief pause between tasks
                
            except Exception as e:
                logger.error(f"Cycle error: {e}")
            
            # Wait for next cycle
            logger.info(f"Sleeping for {interval_minutes} minutes...")
            time.sleep(interval_minutes * 60)
        
        logger.info(f"Autonomous mode completed. Tasks: {self.tasks_completed}, Errors: {len(self.errors)}")
    
    def _generate_autonomous_tasks(self, focus: List[str]) -> List[Dict]:
        """Generate tasks based on focus areas and current state."""
        tasks = []
        
        if 'error-fixing' in focus:
            # Check for recent errors
            state_file = MEMORY_PATH / 'agent_state.json'
            if state_file.exists():
                with open(state_file) as f:
                    state = json.load(f)
                errors = state.get('errors', [])[-5:]
                if errors:
                    tasks.append({
                        'description': f"Analyze and fix recent error: {errors[-1].get('error', 'unknown')[:100]}",
                        'context': json.dumps(errors[-1]),
                        'priority': 'high'
                    })
        
        if 'skill-improvement' in focus:
            # Analyze skills and pick one to improve
            analyses = self.improver.analyze_all_skills()
            low_score = [a for a in analyses if a.score < 70]
            if low_score:
                worst = low_score[0]
                tasks.append({
                    'description': f"Improve skill {worst.name} (score: {worst.score})",
                    'context': f"Issues: {worst.issues[:3]}",
                    'priority': 'medium'
                })
        
        if 'monitoring' in focus:
            tasks.append({
                'description': "Check system health and report status",
                'priority': 'low'
            })
        
        if 'documentation' in focus:
            # Find skills with poor documentation
            for skill_dir in SKILLS_PATH.iterdir():
                skill_md = skill_dir / "SKILL.md"
                if skill_dir.is_dir() and (not skill_md.exists() or skill_md.stat().st_size < 500):
                    tasks.append({
                        'description': f"Generate documentation for {skill_dir.name}",
                        'priority': 'low'
                    })
                    break
        
        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        tasks.sort(key=lambda t: priority_order.get(t.get('priority', 'low'), 2))
        
        return tasks
    
    def _print_help(self):
        """Print help information."""
        print("""
Commands:
  help      - Show this help
  status    - Show agent status
  quit      - Exit interactive mode

Task examples:
  "Analyze the web-search skill"
  "Generate a Python function to fetch crypto prices"
  "Improve the error handling in alert-system"
  "Create a new skill for Twitter analytics"
  "Fix the recent browser CDP error"
  "Check system health"
""")
    
    def _print_status(self):
        """Print agent status."""
        runtime = datetime.now() - self.session_start
        providers = self.llm.check_providers()
        
        print(f"""
Agent Status:
  Runtime: {runtime}
  Tasks completed: {self.tasks_completed}
  Errors: {len(self.errors)}
  
LLM Providers:
  {json.dumps(providers, indent=2)}
  
Memory: {MEMORY_PATH}
Skills: {SKILLS_PATH}
""")


def main():
    parser = argparse.ArgumentParser(
        description='Claude-Proxy - Autonomous AI Agent',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Execute a single task
  python main.py --task "Analyze and fix errors in whale-tracker skill"
  
  # Interactive mode
  python main.py --interactive
  
  # Generate code
  python main.py --generate-code "async function to fetch crypto prices"
  
  # Improve a skill
  python main.py --improve-skill x-persona-adapter
  
  # Full autonomous mode
  python main.py --autonomous --hours 8 --focus error-fixing,skill-improvement
        """
    )
    
    # Task execution
    parser.add_argument('--task', '-t', help='Execute a single task')
    parser.add_argument('--context', '-c', help='Additional context for task')
    
    # Interactive mode
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Run in interactive mode')
    
    # Code generation
    parser.add_argument('--generate-code', '-g', help='Generate code from description')
    parser.add_argument('--language', '-l', default='python', help='Target language')
    parser.add_argument('--output', '-o', help='Output file path')
    
    # Skill improvement
    parser.add_argument('--improve-skill', help='Improve a specific skill')
    parser.add_argument('--analyze-skill', help='Analyze a specific skill')
    parser.add_argument('--analyze-all', action='store_true', help='Analyze all skills')
    parser.add_argument('--apply', action='store_true', help='Apply changes (not dry-run)')
    
    # Autonomous mode
    parser.add_argument('--autonomous', action='store_true',
                       help='Run in autonomous mode')
    parser.add_argument('--hours', type=float, default=8,
                       help='Hours to run in autonomous mode')
    parser.add_argument('--interval', type=int, default=30,
                       help='Minutes between autonomous cycles')
    parser.add_argument('--focus', help='Focus areas (comma-separated)')
    
    # Reasoning
    parser.add_argument('--reason', help='Reason about a goal')
    parser.add_argument('--decide', help='Make a decision')
    parser.add_argument('--options', nargs='+', help='Options for decision')
    
    # Utility
    parser.add_argument('--check-providers', action='store_true',
                       help='Check LLM provider availability')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Build config
    config = {}
    if args.apply:
        config['self_improve'] = {'dry_run': False}
    
    proxy = ClaudeProxy(config)
    
    # Execute based on arguments
    if args.interactive:
        proxy.interactive_mode()
        
    elif args.task:
        result = proxy.execute_task(args.task, args.context or '')
        print(json.dumps(result, indent=2, default=str))
        
    elif args.generate_code:
        code = proxy.code_gen.generate(args.generate_code, args.language)
        if args.output:
            Path(args.output).write_text(code.code)
            print(f"Saved to: {args.output}")
        else:
            print(code.code)
        if not code.valid:
            print(f"\n# Warning: {code.validation_error}", file=sys.stderr)
            
    elif args.improve_skill:
        result = proxy.improver.improve_skill(args.improve_skill)
        print(f"Skill: {result.skill}")
        print(f"Success: {result.success}")
        print(f"Changes: {', '.join(result.changes_made)}")
        if result.error:
            print(f"Error: {result.error}")
            
    elif args.analyze_skill:
        analysis = proxy.improver.analyze_skill(args.analyze_skill)
        print(f"Score: {analysis.score}/100")
        print(f"Issues: {len(analysis.issues)}")
        for issue in analysis.issues[:5]:
            print(f"  - [{issue.get('severity')}] {issue.get('description')}")
            
    elif args.analyze_all:
        analyses = proxy.improver.analyze_all_skills()
        for a in analyses:
            status = "✅" if a.score >= 80 else "⚠️" if a.score >= 60 else "❌"
            print(f"{status} {a.name}: {a.score}/100")
            
    elif args.autonomous:
        focus = args.focus.split(',') if args.focus else None
        proxy.autonomous_mode(args.hours, args.interval, focus)
        
    elif args.reason:
        result = proxy.reasoning.reason(args.reason, args.context or '')
        print(f"Confidence: {result.confidence:.0%}")
        print(f"\n{result.conclusion}")
        
    elif args.decide and args.options:
        options = [{'name': o, 'description': o} for o in args.options]
        result = proxy.reasoning.decide(args.decide, options)
        print(json.dumps(result, indent=2))
        
    elif args.check_providers:
        providers = proxy.llm.check_providers()
        print(json.dumps(providers, indent=2))
        
    elif args.status:
        proxy._print_status()
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
