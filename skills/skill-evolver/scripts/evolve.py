#!/usr/bin/env python3
"""
skill-evolver evolution engine
Generates and applies improvements to Clawdbot skills
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from utils import (
    load_config,
    expand_path,
    create_backup,
    restore_backup,
    log_change,
    get_file_hash,
    severity_sort_key
)
from analyze import SkillAnalyzer


class ImprovementTemplates:
    """Templates for common improvements."""
    
    RETRY_DECORATOR = '''
def retry(max_attempts=3, delay=1, backoff=2, exceptions=(Exception,)):
    """Retry decorator with exponential backoff."""
    from functools import wraps
    import time
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            current_delay = delay
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempts += 1
                    if attempts == max_attempts:
                        raise
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator
'''

    ERROR_HANDLER = '''
try:
    {code}
except Exception as e:
    logger.error(f"Error in {function_name}: {{e}}")
    raise
'''

    LOGGING_SETUP = '''
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
'''

    DOCSTRING_TEMPLATE = '''"""
{description}

Args:
{args}

Returns:
{returns}

Raises:
{raises}
"""'''

    SKILL_MD_OVERVIEW = '''## Overview

{name} provides functionality for {purpose}.

### Key Features
- Feature 1
- Feature 2
- Feature 3
'''

    SKILL_MD_WORKFLOW = '''## Workflow

### 1. Setup
Configure the skill by editing `references/config.json`.

### 2. Usage
```bash
python scripts/main.py [options]
```

### 3. Output
Results are saved to the configured output directory.
'''

    SKILL_MD_TROUBLESHOOTING = '''## Troubleshooting

### Common Issues

**Issue**: Script fails to run
**Solution**: Check that all dependencies are installed

**Issue**: API errors
**Solution**: Verify credentials in config file

### Debug Mode
Run with `--debug` flag for verbose output:
```bash
python scripts/main.py --debug
```
'''

    VERSION_SECTION = '''
## Version History

- **v1.0.0** ({date}): Initial version
'''


class SkillEvolver:
    """Generates and applies improvements to skills."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.skills_path = expand_path(config['skills_path'])
        self.backup_path = expand_path(config.get('backup_path', '~/clawd/backups/'))
        self.log_path = expand_path(config.get('log_path', '~/clawd/skills/skill-evolver/assets/evolution.log'))
        self.dry_run = config.get('dry_run', True)
        self.require_confirmation = config.get('require_confirmation', True)
        self.max_changes = config.get('max_changes_per_run', 5)
        self.templates = ImprovementTemplates()
        self.changes_made = []
        self.analyzer = SkillAnalyzer(config)
        
    def suggest_improvements(self, skill_name: Optional[str] = None) -> List[Dict]:
        """Generate improvement suggestions without applying them."""
        self.analyzer.analyze_all()
        
        improvements = []
        
        if skill_name:
            if skill_name not in self.analyzer.results['skills']:
                return []
            skills_to_process = {skill_name: self.analyzer.results['skills'][skill_name]}
        else:
            skills_to_process = self.analyzer.results['skills']
        
        for name, analysis in skills_to_process.items():
            skill_improvements = self._generate_improvements(name, analysis)
            improvements.extend(skill_improvements)
        
        # Sort by severity
        improvements.sort(key=lambda x: severity_sort_key(x['severity']))
        
        return improvements
    
    def _generate_improvements(self, skill_name: str, analysis: Dict) -> List[Dict]:
        """Generate specific improvements for a skill."""
        improvements = []
        skill_path = self.skills_path / skill_name
        
        # Check for missing SKILL.md sections
        if analysis['structure'].get('has_skill_md'):
            skill_md_path = skill_path / "SKILL.md"
            doc = analysis.get('documentation', {})
            
            if not doc.get('has_overview'):
                improvements.append({
                    'skill': skill_name,
                    'file': 'SKILL.md',
                    'type': 'add_section',
                    'severity': 'MEDIUM',
                    'description': 'Add overview section',
                    'change': self.templates.SKILL_MD_OVERVIEW.format(
                        name=skill_name,
                        purpose='[describe purpose]'
                    ),
                    'auto_apply': True
                })
            
            if not doc.get('has_workflow'):
                improvements.append({
                    'skill': skill_name,
                    'file': 'SKILL.md',
                    'type': 'add_section',
                    'severity': 'MEDIUM',
                    'description': 'Add workflow section',
                    'change': self.templates.SKILL_MD_WORKFLOW,
                    'auto_apply': True
                })
            
            if not doc.get('has_troubleshooting'):
                improvements.append({
                    'skill': skill_name,
                    'file': 'SKILL.md',
                    'type': 'add_section',
                    'severity': 'LOW',
                    'description': 'Add troubleshooting section',
                    'change': self.templates.SKILL_MD_TROUBLESHOOTING,
                    'auto_apply': True
                })
            
            if not doc.get('has_version'):
                improvements.append({
                    'skill': skill_name,
                    'file': 'SKILL.md',
                    'type': 'add_section',
                    'severity': 'LOW',
                    'description': 'Add version tracking',
                    'change': self.templates.VERSION_SECTION.format(
                        date=datetime.now().strftime('%Y-%m-%d')
                    ),
                    'auto_apply': True
                })
        else:
            improvements.append({
                'skill': skill_name,
                'file': 'SKILL.md',
                'type': 'create_file',
                'severity': 'CRITICAL',
                'description': 'Create SKILL.md documentation',
                'change': self._generate_skill_md_template(skill_name, analysis),
                'auto_apply': False
            })
        
        # Check scripts for improvements
        for script in analysis.get('scripts', []):
            script_name = script['path'].split('/')[-1]
            
            if not script.get('has_error_handling') and len(script.get('functions', [])) > 0:
                improvements.append({
                    'skill': skill_name,
                    'file': f'scripts/{script_name}',
                    'type': 'add_error_handling',
                    'severity': 'HIGH',
                    'description': f'Add error handling to {script_name}',
                    'change': 'Add try/except blocks to main functions',
                    'auto_apply': False
                })
            
            if not script.get('has_logging'):
                improvements.append({
                    'skill': skill_name,
                    'file': f'scripts/{script_name}',
                    'type': 'add_logging',
                    'severity': 'MEDIUM',
                    'description': f'Add logging to {script_name}',
                    'change': self.templates.LOGGING_SETUP,
                    'auto_apply': True
                })
            
            if not script.get('has_docstring'):
                improvements.append({
                    'skill': skill_name,
                    'file': f'scripts/{script_name}',
                    'type': 'add_docstring',
                    'severity': 'LOW',
                    'description': f'Add module docstring to {script_name}',
                    'change': f'"""\\n{script_name}\\nPart of {skill_name} skill\\n"""',
                    'auto_apply': True
                })
            
            # Check for specific issues
            for issue in script.get('issues', []):
                if 'timeout' in issue.lower():
                    improvements.append({
                        'skill': skill_name,
                        'file': f'scripts/{script_name}',
                        'type': 'add_timeout',
                        'severity': 'HIGH',
                        'description': 'Add timeout to HTTP requests',
                        'change': 'Add timeout=30 parameter to requests calls',
                        'auto_apply': False
                    })
                
                if 'api key' in issue.lower():
                    improvements.append({
                        'skill': skill_name,
                        'file': f'scripts/{script_name}',
                        'type': 'secure_credentials',
                        'severity': 'HIGH',
                        'description': 'Move hardcoded credentials to config',
                        'change': 'Replace hardcoded keys with os.environ.get() or config file',
                        'auto_apply': False
                    })
        
        return improvements
    
    def _generate_skill_md_template(self, skill_name: str, analysis: Dict) -> str:
        """Generate a complete SKILL.md template."""
        scripts = analysis.get('structure', {}).get('scripts', [])
        
        template = f"""# {skill_name}

## Overview

{skill_name} provides functionality for [describe purpose].

### Key Features
- Feature 1
- Feature 2

## Quick Start

```bash
# Run the main script
python scripts/{scripts[0] if scripts else 'main.py'}
```

## Workflow

1. Configure settings in `references/config.json`
2. Run the skill
3. Check output

## Configuration

Edit `references/config.json`:

```json
{{
    "setting1": "value1",
    "setting2": "value2"
}}
```

## Scripts

"""
        for script in scripts:
            template += f"- `{script}`: [description]\n"
        
        template += f"""
## Troubleshooting

### Common Issues

**Issue**: Script fails
**Solution**: Check configuration and dependencies

## Version History

- **v1.0.0** ({datetime.now().strftime('%Y-%m-%d')}): Initial version
"""
        return template
    
    def apply_improvements(self, improvements: List[Dict], 
                          severity_filter: Optional[str] = None,
                          auto_only: bool = False) -> List[Dict]:
        """Apply improvements to skills."""
        applied = []
        
        # Filter improvements
        filtered = improvements
        if severity_filter:
            filtered = [i for i in filtered if i['severity'] == severity_filter.upper()]
        if auto_only:
            filtered = [i for i in filtered if i.get('auto_apply', False)]
        
        # Limit changes per run
        filtered = filtered[:self.max_changes]
        
        for improvement in filtered:
            if self.dry_run:
                print(f"[DRY RUN] Would apply: {improvement['skill']}/{improvement['file']} - {improvement['description']}")
                applied.append({**improvement, 'status': 'dry_run'})
                continue
            
            if self.require_confirmation and not improvement.get('auto_apply'):
                response = input(f"Apply {improvement['description']} to {improvement['skill']}? [y/N] ")
                if response.lower() != 'y':
                    applied.append({**improvement, 'status': 'skipped'})
                    continue
            
            result = self._apply_improvement(improvement)
            applied.append({**improvement, 'status': result})
        
        self.changes_made = applied
        return applied
    
    def _apply_improvement(self, improvement: Dict) -> str:
        """Apply a single improvement."""
        skill_path = self.skills_path / improvement['skill']
        file_path = skill_path / improvement['file']
        
        # Create backup
        if file_path.exists():
            backup_path = create_backup(file_path, self.backup_path)
            print(f"Backup created: {backup_path}")
        
        try:
            if improvement['type'] == 'create_file':
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w') as f:
                    f.write(improvement['change'])
            
            elif improvement['type'] == 'add_section':
                with open(file_path, 'a') as f:
                    f.write('\n\n' + improvement['change'])
            
            elif improvement['type'] == 'add_logging':
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Add logging import at the top
                if 'import logging' not in content:
                    lines = content.split('\n')
                    # Find first non-comment, non-import line
                    insert_idx = 0
                    for i, line in enumerate(lines):
                        if line.strip() and not line.startswith('#') and not line.startswith('import') and not line.startswith('from'):
                            insert_idx = i
                            break
                        if line.startswith('import') or line.startswith('from'):
                            insert_idx = i + 1
                    
                    lines.insert(insert_idx, improvement['change'])
                    with open(file_path, 'w') as f:
                        f.write('\n'.join(lines))
            
            elif improvement['type'] == 'add_docstring':
                with open(file_path, 'r') as f:
                    content = f.read()
                
                if not content.strip().startswith('"""') and not content.strip().startswith("'''"):
                    content = improvement['change'] + '\n\n' + content
                    with open(file_path, 'w') as f:
                        f.write(content)
            
            else:
                # For complex improvements, just log what needs to be done
                print(f"Manual intervention required: {improvement['description']}")
                return 'manual_required'
            
            # Log the change
            log_change(self.log_path, {
                'skill': improvement['skill'],
                'file': improvement['file'],
                'type': improvement['type'],
                'description': improvement['description']
            })
            
            return 'applied'
            
        except Exception as e:
            print(f"Error applying improvement: {e}")
            # Attempt rollback if backup exists
            if 'backup_path' in locals():
                restore_backup(backup_path, file_path)
                print("Rolled back to backup")
            return f'failed: {e}'
    
    def rollback(self, backup_path: str) -> bool:
        """Rollback a change from backup."""
        backup_path = expand_path(backup_path)
        if not backup_path.exists():
            print(f"Backup not found: {backup_path}")
            return False
        
        # Extract original path from backup
        # Backup format: skill-name/file.ext.TIMESTAMP
        parts = backup_path.name.rsplit('.', 1)
        if len(parts) != 2:
            print("Invalid backup filename format")
            return False
        
        original_name = parts[0]
        skill_name = backup_path.parent.name
        
        # Find the original file
        original_path = self.skills_path / skill_name / original_name
        if not original_path.parent.exists():
            original_path = self.skills_path / skill_name / "scripts" / original_name
        
        if restore_backup(backup_path, original_path):
            log_change(self.log_path, {
                'type': 'rollback',
                'backup': str(backup_path),
                'restored_to': str(original_path)
            })
            print(f"Restored {original_path} from {backup_path}")
            return True
        
        return False
    
    def generate_report(self, improvements: List[Dict], applied: List[Dict]) -> str:
        """Generate evolution report."""
        date = datetime.now().strftime('%Y-%m-%d')
        
        report = f"""# Evolution Report — {date}

## Summary
- **Improvements Identified**: {len(improvements)}
- **Changes Applied**: {len([a for a in applied if a.get('status') == 'applied'])}
- **Dry Run**: {len([a for a in applied if a.get('status') == 'dry_run'])}
- **Skipped**: {len([a for a in applied if a.get('status') == 'skipped'])}
- **Failed**: {len([a for a in applied if 'failed' in str(a.get('status', ''))])}

## Changes Made

"""
        
        for i, change in enumerate(applied, 1):
            status_icon = {
                'applied': '✅',
                'dry_run': '🔍',
                'skipped': '⏭️',
                'manual_required': '🔧'
            }.get(change.get('status', ''), '❌')
            
            report += f"### {i}. {change['skill']}/{change['file']}\n"
            report += f"**Status**: {status_icon} {change.get('status', 'unknown')}\n"
            report += f"**Type**: {change['type']}\n"
            report += f"**Description**: {change['description']}\n\n"
        
        # Pending improvements
        pending = [i for i in improvements if i not in applied]
        if pending:
            report += "## Pending Improvements\n\n"
            for imp in pending[:10]:
                report += f"- [{imp['severity']}] **{imp['skill']}**: {imp['description']}\n"
        
        report += "\n## Next Actions\n\n"
        for imp in improvements[:5]:
            if imp.get('status') != 'applied':
                report += f"- [ ] {imp['skill']}: {imp['description']}\n"
        
        return report


def main():
    parser = argparse.ArgumentParser(description='Evolve Clawdbot skills')
    parser.add_argument('--config', '-c', help='Path to config file')
    parser.add_argument('--mode', '-m', choices=['suggest', 'apply', 'auto'], default='suggest',
                       help='Operation mode')
    parser.add_argument('--skill', '-s', help='Target specific skill')
    parser.add_argument('--severity', choices=['critical', 'high', 'medium', 'low'],
                       help='Filter by severity')
    parser.add_argument('--auto-only', action='store_true', 
                       help='Only apply auto-applicable improvements')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without applying')
    parser.add_argument('--force', action='store_true', help='Skip confirmations')
    parser.add_argument('--rollback', help='Rollback from backup file')
    parser.add_argument('--output', '-o', help='Output report file')
    parser.add_argument('--report', action='store_true', help='Generate report')
    
    args = parser.parse_args()
    
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        config = {
            'skills_path': '~/clawd/skills/',
            'memory_path': '~/clawd/memory/',
            'backup_path': '~/clawd/backups/',
            'excluded_skills': ['skill-evolver'],
            'dry_run': True,
            'require_confirmation': True,
            'max_changes_per_run': 5
        }
    
    # Override config with args
    if args.dry_run:
        config['dry_run'] = True
    if args.force:
        config['require_confirmation'] = False
    
    evolver = SkillEvolver(config)
    
    # Handle rollback
    if args.rollback:
        success = evolver.rollback(args.rollback)
        sys.exit(0 if success else 1)
    
    # Generate improvements
    improvements = evolver.suggest_improvements(args.skill)
    
    if args.mode == 'suggest':
        print(f"Found {len(improvements)} potential improvements:\n")
        for imp in improvements:
            print(f"[{imp['severity']}] {imp['skill']}/{imp['file']}: {imp['description']}")
        
    elif args.mode in ['apply', 'auto']:
        if args.mode == 'auto':
            config['require_confirmation'] = False
        
        applied = evolver.apply_improvements(
            improvements,
            severity_filter=args.severity,
            auto_only=args.auto_only
        )
        
        if args.report or args.output:
            report = evolver.generate_report(improvements, applied)
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(report)
                print(f"Report saved to {args.output}")
            else:
                print(report)
        else:
            print(f"\nApplied {len([a for a in applied if a.get('status') == 'applied'])} changes")


if __name__ == "__main__":
    main()
