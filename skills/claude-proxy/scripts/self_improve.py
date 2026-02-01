#!/usr/bin/env python3
"""
self_improve.py - Autonomous self-improvement system
Analyzes and improves Clawdbot skills using LLM-powered analysis
"""

import json
import logging
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from llm_client import LLMClient
from reasoning import ReasoningEngine
from code_gen import CodeGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('self-improve')

SKILLS_PATH = Path.home() / 'clawd' / 'skills'
BACKUP_PATH = Path.home() / 'clawd' / 'backups' / 'skills'
MEMORY_PATH = Path.home() / 'clawd' / 'memory'


@dataclass
class SkillAnalysis:
    """Analysis result for a skill."""
    name: str
    path: str
    score: int
    issues: List[Dict]
    improvements: List[Dict]
    documentation_quality: int
    code_quality: int
    test_coverage: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ImprovementResult:
    """Result of applying an improvement."""
    skill: str
    improvement: str
    success: bool
    changes_made: List[str]
    backup_path: str = None
    error: str = None


class SelfImprover:
    """
    Autonomous skill improvement system.
    
    Uses LLM to:
    - Analyze skill quality beyond regex patterns
    - Generate intelligent improvements
    - Create missing documentation
    - Fix code issues
    - Add tests
    """
    
    ANALYSIS_PROMPT = """Analyze this Clawdbot skill:

**Skill Name**: {skill_name}

**SKILL.md**:
```markdown
{skill_md}
```

**Main Script** ({script_name}):
```python
{main_script}
```

**Config** (if exists):
```json
{config}
```

Provide detailed analysis:

```json
{{
  "overall_score": 0-100,
  "documentation_quality": 0-100,
  "code_quality": 0-100,
  "issues": [
    {{"severity": "high|medium|low", "category": "...", "description": "...", "location": "..."}}
  ],
  "improvements": [
    {{"priority": "high|medium|low", "type": "...", "description": "...", "effort": "small|medium|large"}}
  ],
  "strengths": ["..."],
  "missing_features": ["..."]
}}
```"""

    IMPROVEMENT_PROMPT = """Apply this improvement to the skill:

**Skill**: {skill_name}
**Improvement**: {improvement}
**Current Code**:
```python
{current_code}
```

Generate the improved code. Keep all existing functionality, only add/fix what's needed.

```python
<improved code>
```

Changes made:
- <change 1>
- <change 2>"""

    DOC_GENERATION_PROMPT = """Generate documentation for this skill:

**Skill Name**: {skill_name}
**Main Script**:
```python
{main_script}
```

Generate a comprehensive SKILL.md following this structure:
- Overview (what the skill does)
- Quick Start (basic usage)
- Workflow (how it works)
- Configuration (config options)
- Examples (usage examples)
- Troubleshooting (common issues)
- Version (changelog)

```markdown
<SKILL.md content>
```"""

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.llm = LLMClient(self.config.get('llm', {}))
        self.reasoning = ReasoningEngine(self.config)
        self.code_gen = CodeGenerator(self.config)
        self.dry_run = self.config.get('dry_run', True)
        self.backup_enabled = self.config.get('backup', True)
        self.history = self._load_history()
        
    def _load_history(self) -> List[Dict]:
        """Load improvement history."""
        history_file = MEMORY_PATH / 'improvement_history.json'
        if history_file.exists():
            with open(history_file) as f:
                return json.load(f)
        return []
    
    def _save_history(self):
        """Save improvement history."""
        MEMORY_PATH.mkdir(parents=True, exist_ok=True)
        history_file = MEMORY_PATH / 'improvement_history.json'
        with open(history_file, 'w') as f:
            json.dump(self.history[-500:], f, indent=2)
    
    def analyze_skill(self, skill_name: str) -> SkillAnalysis:
        """
        Perform deep LLM-powered analysis of a skill.
        
        Args:
            skill_name: Name of the skill to analyze
        
        Returns:
            SkillAnalysis with detailed results
        """
        skill_path = SKILLS_PATH / skill_name
        
        if not skill_path.exists():
            raise ValueError(f"Skill not found: {skill_name}")
        
        # Read skill files
        skill_md = ""
        skill_md_path = skill_path / "SKILL.md"
        if skill_md_path.exists():
            skill_md = skill_md_path.read_text()[:5000]  # Truncate for token limits
        
        main_script = ""
        script_name = "main.py"
        for script_path in (skill_path / "scripts").glob("*.py"):
            if script_path.name == "main.py" or main_script == "":
                main_script = script_path.read_text()[:8000]
                script_name = script_path.name
        
        config = "{}"
        config_path = skill_path / "references" / "config.json"
        if config_path.exists():
            config = config_path.read_text()[:2000]
        
        # Check if any providers are available
        providers = self.llm.check_providers()
        working_providers = [k for k, v in providers.items() if v.get('available', False)]

        if not working_providers:
            logger.warning(f"No LLM providers available for {skill_name}, using fallback analysis")
            # Fallback: use basic structural analysis without LLM
            return self._basic_analysis(skill_name, skill_path, skill_md, main_script)

        # Ask LLM for analysis
        prompt = self.ANALYSIS_PROMPT.format(
            skill_name=skill_name,
            skill_md=skill_md or "(No SKILL.md found)",
            script_name=script_name,
            main_script=main_script or "(No scripts found)",
            config=config
        )

        response = self.llm.complete(
            messages=[{'role': 'user', 'content': prompt}],
            system="You are a code quality expert. Analyze thoroughly and provide actionable feedback."
        )

        if not response.success:
            logger.warning(f"LLM analysis failed for {skill_name}, using fallback")
            return self._basic_analysis(skill_name, skill_path, skill_md, main_script)
        
        # Parse LLM response
        analysis = self._parse_analysis(response.content)
        
        return SkillAnalysis(
            name=skill_name,
            path=str(skill_path),
            score=analysis.get('overall_score', 50),
            issues=analysis.get('issues', []),
            improvements=analysis.get('improvements', []),
            documentation_quality=analysis.get('documentation_quality', 50),
            code_quality=analysis.get('code_quality', 50),
            test_coverage=analysis.get('test_coverage', 0)
        )
    
    def analyze_all_skills(self) -> List[SkillAnalysis]:
        """Analyze all skills in the skills directory."""
        analyses = []
        
        for skill_dir in SKILLS_PATH.iterdir():
            if skill_dir.is_dir() and not skill_dir.name.startswith('.'):
                if skill_dir.name == 'claude-proxy':  # Don't analyze self
                    continue
                    
                try:
                    logger.info(f"Analyzing: {skill_dir.name}")
                    analysis = self.analyze_skill(skill_dir.name)
                    analyses.append(analysis)
                except Exception as e:
                    logger.error(f"Failed to analyze {skill_dir.name}: {e}")
        
        return sorted(analyses, key=lambda a: a.score)
    
    def improve_skill(self, 
                      skill_name: str, 
                      improvement: Dict = None,
                      auto_select: bool = True) -> ImprovementResult:
        """
        Apply an improvement to a skill.
        
        Args:
            skill_name: Skill to improve
            improvement: Specific improvement to apply (or auto-select)
            auto_select: Automatically select highest priority improvement
        
        Returns:
            ImprovementResult with changes made
        """
        skill_path = SKILLS_PATH / skill_name
        
        if not skill_path.exists():
            return ImprovementResult(
                skill=skill_name,
                improvement="",
                success=False,
                changes_made=[],
                error=f"Skill not found: {skill_name}"
            )
        
        # Get improvement if not provided
        if not improvement and auto_select:
            analysis = self.analyze_skill(skill_name)
            if not analysis.improvements:
                return ImprovementResult(
                    skill=skill_name,
                    improvement="",
                    success=True,
                    changes_made=["No improvements needed"]
                )
            improvement = analysis.improvements[0]  # Highest priority
        
        if not improvement:
            return ImprovementResult(
                skill=skill_name,
                improvement="",
                success=False,
                changes_made=[],
                error="No improvement specified"
            )
        
        logger.info(f"Applying improvement to {skill_name}: {improvement.get('description', '')}")
        
        # Create backup
        backup_path = None
        if self.backup_enabled and not self.dry_run:
            backup_path = self._create_backup(skill_name)
        
        # Read current code
        main_script = ""
        main_path = skill_path / "scripts" / "main.py"
        if main_path.exists():
            main_script = main_path.read_text()
        
        # Generate improved code
        prompt = self.IMPROVEMENT_PROMPT.format(
            skill_name=skill_name,
            improvement=json.dumps(improvement),
            current_code=main_script
        )
        
        response = self.llm.complete(
            messages=[{'role': 'user', 'content': prompt}],
            system="You are a code improvement expert. Make minimal, targeted changes."
        )
        
        if not response.success:
            return ImprovementResult(
                skill=skill_name,
                improvement=improvement.get('description', ''),
                success=False,
                changes_made=[],
                backup_path=backup_path,
                error=response.error
            )
        
        # Extract improved code and changes
        improved_code = self._extract_code(response.content)
        changes = self._extract_changes(response.content)
        
        # Apply changes
        if not self.dry_run:
            main_path.parent.mkdir(parents=True, exist_ok=True)
            main_path.write_text(improved_code)
            logger.info(f"Updated: {main_path}")
        else:
            logger.info(f"[DRY RUN] Would update: {main_path}")
        
        # Record history
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'skill': skill_name,
            'improvement': improvement,
            'changes': changes,
            'dry_run': self.dry_run
        })
        self._save_history()
        
        return ImprovementResult(
            skill=skill_name,
            improvement=improvement.get('description', ''),
            success=True,
            changes_made=changes,
            backup_path=backup_path
        )
    
    def generate_documentation(self, skill_name: str) -> str:
        """Generate SKILL.md for a skill that's missing documentation."""
        skill_path = SKILLS_PATH / skill_name
        
        if not skill_path.exists():
            raise ValueError(f"Skill not found: {skill_name}")
        
        # Read main script
        main_script = ""
        for script_path in (skill_path / "scripts").glob("*.py"):
            main_script = script_path.read_text()[:8000]
            break
        
        if not main_script:
            return f"# {skill_name}\n\nNo scripts found to document."
        
        prompt = self.DOC_GENERATION_PROMPT.format(
            skill_name=skill_name,
            main_script=main_script
        )
        
        response = self.llm.complete(
            messages=[{'role': 'user', 'content': prompt}],
            system="You are a technical writer. Create clear, comprehensive documentation."
        )
        
        if not response.success:
            return f"# {skill_name}\n\nFailed to generate documentation: {response.error}"
        
        doc = self._extract_markdown(response.content)
        
        # Save if not dry run
        if not self.dry_run:
            skill_md_path = skill_path / "SKILL.md"
            skill_md_path.write_text(doc)
            logger.info(f"Created: {skill_md_path}")
        
        return doc
    
    def create_missing_scripts(self) -> List[str]:
        """Find skills missing main.py and create them."""
        created = []
        
        for skill_dir in SKILLS_PATH.iterdir():
            if not skill_dir.is_dir() or skill_dir.name.startswith('.'):
                continue
            
            scripts_dir = skill_dir / "scripts"
            main_py = scripts_dir / "main.py"
            
            if scripts_dir.exists() and not main_py.exists():
                # Check if there are other Python files
                other_scripts = list(scripts_dir.glob("*.py"))
                if other_scripts:
                    continue  # Has other scripts, skip
                
                logger.info(f"Creating main.py for: {skill_dir.name}")
                
                # Read SKILL.md for context
                skill_md = ""
                skill_md_path = skill_dir / "SKILL.md"
                if skill_md_path.exists():
                    skill_md = skill_md_path.read_text()[:3000]
                
                # Generate main.py
                code = self.code_gen.generate(
                    f"Main script for {skill_dir.name} skill. Context: {skill_md[:500]}",
                    'python'
                )
                
                if not self.dry_run:
                    scripts_dir.mkdir(parents=True, exist_ok=True)
                    main_py.write_text(code.code)
                    main_py.chmod(0o755)
                
                created.append(skill_dir.name)
        
        return created
    
    def _create_backup(self, skill_name: str) -> str:
        """Create backup of a skill before modification."""
        skill_path = SKILLS_PATH / skill_name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = BACKUP_PATH / skill_name / timestamp
        
        backup_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(skill_path, backup_dir)
        
        logger.info(f"Backup created: {backup_dir}")
        return str(backup_dir)
    
    def restore_backup(self, skill_name: str, backup_timestamp: str = None) -> bool:
        """Restore a skill from backup."""
        skill_path = SKILLS_PATH / skill_name
        backup_base = BACKUP_PATH / skill_name
        
        if not backup_base.exists():
            logger.error(f"No backups found for {skill_name}")
            return False
        
        # Find backup
        if backup_timestamp:
            backup_dir = backup_base / backup_timestamp
        else:
            # Use latest
            backups = sorted(backup_base.iterdir(), reverse=True)
            if not backups:
                return False
            backup_dir = backups[0]
        
        if not backup_dir.exists():
            logger.error(f"Backup not found: {backup_dir}")
            return False
        
        # Remove current and restore
        if skill_path.exists():
            shutil.rmtree(skill_path)
        
        shutil.copytree(backup_dir, skill_path)
        logger.info(f"Restored {skill_name} from {backup_dir}")

        return True

    def _basic_analysis(self, skill_name: str, skill_path: Path,
                        skill_md: str, main_script: str) -> SkillAnalysis:
        """
        Basic structural analysis without LLM.

        Falls back to this when LLM providers are unavailable.
        Uses simple heuristics to assess skill quality.
        """
        issues = []
        improvements = []
        doc_quality = 50
        code_quality = 50

        # Check SKILL.md
        if not skill_md or len(skill_md.strip()) < 10:
            issues.append({
                'severity': 'high',
                'category': 'documentation',
                'description': 'SKILL.md is missing or empty',
                'location': 'SKILL.md'
            })
            improvements.append({
                'priority': 'high',
                'type': 'documentation',
                'description': 'Create SKILL.md with overview, workflow, and examples'
            })
        else:
            doc_quality = 70
            if '## Overview' not in skill_md:
                issues.append({
                    'severity': 'medium',
                    'category': 'documentation',
                    'description': 'SKILL.md missing Overview section',
                    'location': 'SKILL.md'
                })
            if '## Workflow' not in skill_md and '## Usage' not in skill_md:
                issues.append({
                    'severity': 'medium',
                    'category': 'documentation',
                    'description': 'SKILL.md missing Workflow/Usage section',
                    'location': 'SKILL.md'
                })

        # Check scripts
        if skill_path is None:
            issues.append({
                'severity': 'high',
                'category': 'structure',
                'description': 'Skill path is missing',
                'location': skill_name
            })
            return SkillAnalysis(
                name=skill_name,
                path="unknown",
                score=0,
                issues=issues,
                improvements=improvements,
                documentation_quality=0,
                code_quality=0,
                test_coverage=0
            )

        scripts_dir = skill_path / "scripts"
        if not scripts_dir.exists():
            issues.append({
                'severity': 'high',
                'category': 'structure',
                'description': 'scripts/ directory is missing',
                'location': 'scripts/'
            })
        else:
            scripts = list(scripts_dir.glob("*.py"))
            if not scripts:
                issues.append({
                    'severity': 'high',
                    'category': 'structure',
                    'description': 'No Python scripts found',
                    'location': 'scripts/'
                })
            else:
                code_quality = 60
                for script in scripts:
                    content = script.read_text()
                    # Basic checks
                    if '"""' not in content and "'''" not in content:
                        issues.append({
                            'severity': 'low',
                            'category': 'code',
                            'description': f'{script.name} missing docstring',
                            'location': script.name
                        })
                    if 'except' not in content and 'try:' in content:
                        issues.append({
                            'severity': 'medium',
                            'category': 'code',
                            'description': f'{script.name} has try without except',
                            'location': script.name
                        })

        # Check references
        refs_dir = skill_path / "references"
        if not refs_dir.exists():
            improvements.append({
                'priority': 'low',
                'type': 'structure',
                'description': 'Create references/ directory for configs'
            })

        # Calculate score
        score = 100
        for issue in issues:
            if issue['severity'] == 'high':
                score -= 20
            elif issue['severity'] == 'medium':
                score -= 10
            else:
                score -= 5
        score = max(0, min(100, score))

        return SkillAnalysis(
            name=skill_name,
            path=str(skill_path),
            score=score,
            issues=issues,
            improvements=improvements,
            documentation_quality=doc_quality,
            code_quality=code_quality,
            test_coverage=0
        )

    def _parse_analysis(self, content: str) -> Dict:
        """Parse LLM analysis response."""
        import re
        
        # Try to extract JSON
        json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass
        
        # Try direct parse
        try:
            start = content.find('{')
            end = content.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(content[start:end])
        except:
            pass
        
        return {}
    
    def _extract_code(self, content: str) -> str:
        """Extract code from response."""
        import re
        match = re.search(r'```python\s*(.*?)\s*```', content, re.DOTALL)
        if match:
            return match.group(1)
        return content
    
    def _extract_markdown(self, content: str) -> str:
        """Extract markdown from response."""
        import re
        match = re.search(r'```markdown\s*(.*?)\s*```', content, re.DOTALL)
        if match:
            return match.group(1)
        return content
    
    def _extract_changes(self, content: str) -> List[str]:
        """Extract list of changes from response."""
        import re
        changes = []
        
        # Find "Changes made:" section
        changes_match = re.search(r'Changes\s*(?:made)?:\s*((?:[-•]\s*.+\n?)+)', content)
        if changes_match:
            for line in changes_match.group(1).split('\n'):
                line = line.strip()
                if line.startswith(('-', '•', '*')):
                    changes.append(line.lstrip('-•* '))
        
        return changes
    
    def get_improvement_stats(self) -> Dict:
        """Get statistics about improvements made."""
        total = len(self.history)
        successful = len([h for h in self.history if not h.get('dry_run')])
        
        by_skill = {}
        for h in self.history:
            skill = h.get('skill', 'unknown')
            by_skill[skill] = by_skill.get(skill, 0) + 1
        
        return {
            'total_improvements': total,
            'applied': successful,
            'dry_runs': total - successful,
            'by_skill': by_skill,
            'last_improvement': self.history[-1] if self.history else None
        }


def improve(skill_name: str = None, dry_run: bool = True) -> str:
    """Simple improvement interface."""
    improver = SelfImprover({'dry_run': dry_run})
    
    if skill_name:
        result = improver.improve_skill(skill_name)
        return f"{'[DRY RUN] ' if dry_run else ''}Improved {skill_name}: {result.changes_made}"
    else:
        analyses = improver.analyze_all_skills()
        return json.dumps([
            {'name': a.name, 'score': a.score, 'issues': len(a.issues)}
            for a in analyses
        ], indent=2)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Self-Improvement System')
    parser.add_argument('--analyze', '-a', help='Analyze specific skill')
    parser.add_argument('--analyze-all', action='store_true', help='Analyze all skills')
    parser.add_argument('--improve', '-i', help='Improve specific skill')
    parser.add_argument('--generate-docs', '-d', help='Generate docs for skill')
    parser.add_argument('--create-missing', action='store_true', help='Create missing main.py')
    parser.add_argument('--restore', help='Restore skill from backup')
    parser.add_argument('--stats', action='store_true', help='Show improvement stats')
    parser.add_argument('--dry-run', action='store_true', default=True, help='Dry run mode')
    parser.add_argument('--apply', action='store_true', help='Actually apply changes')
    parser.add_argument('--report', action='store_true', help='Generate report')
    
    args = parser.parse_args()
    
    config = {'dry_run': not args.apply}
    improver = SelfImprover(config)
    
    if args.analyze:
        analysis = improver.analyze_skill(args.analyze)
        print(f"\n{'='*60}")
        print(f"Skill: {analysis.name}")
        print(f"Score: {analysis.score}/100")
        print(f"Documentation: {analysis.documentation_quality}/100")
        print(f"Code Quality: {analysis.code_quality}/100")
        print(f"{'='*60}")
        print(f"\nIssues ({len(analysis.issues)}):")
        for issue in analysis.issues[:5]:
            print(f"  [{issue.get('severity', 'medium')}] {issue.get('description', 'N/A')}")
        print(f"\nImprovements ({len(analysis.improvements)}):")
        for imp in analysis.improvements[:5]:
            print(f"  [{imp.get('priority', 'medium')}] {imp.get('description', 'N/A')}")
            
    elif args.analyze_all:
        analyses = improver.analyze_all_skills()
        
        if args.report:
            print(f"# Skill Analysis Report — {datetime.now().strftime('%Y-%m-%d')}\n")
            print(f"| Skill | Score | Issues | Doc | Code |")
            print(f"|-------|-------|--------|-----|------|")
            for a in analyses:
                print(f"| {a.name} | {a.score} | {len(a.issues)} | {a.documentation_quality} | {a.code_quality} |")
        else:
            for a in analyses:
                status = "✅" if a.score >= 80 else "⚠️" if a.score >= 60 else "❌"
                print(f"{status} {a.name}: {a.score}/100 ({len(a.issues)} issues)")
                
    elif args.improve:
        result = improver.improve_skill(args.improve)
        print(f"\n{'='*60}")
        print(f"Skill: {result.skill}")
        print(f"Success: {result.success}")
        print(f"Backup: {result.backup_path or 'N/A'}")
        print(f"{'='*60}")
        print(f"\nChanges:")
        for change in result.changes_made:
            print(f"  - {change}")
        if result.error:
            print(f"\nError: {result.error}")
            
    elif args.generate_docs:
        doc = improver.generate_documentation(args.generate_docs)
        print(doc)
        
    elif args.create_missing:
        created = improver.create_missing_scripts()
        print(f"Created main.py for: {', '.join(created) or 'none'}")
        
    elif args.restore:
        success = improver.restore_backup(args.restore)
        print(f"Restore {'successful' if success else 'failed'}")
        
    elif args.stats:
        stats = improver.get_improvement_stats()
        print(json.dumps(stats, indent=2))
        
    else:
        parser.print_help()
