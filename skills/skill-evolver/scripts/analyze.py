#!/usr/bin/env python3
"""
skill-evolver analysis engine
Scans and analyzes all Clawdbot skills
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from utils import (
    load_config,
    get_skill_dirs,
    read_skill_md,
    parse_skill_structure,
    analyze_skill_md,
    analyze_python_file,
    calculate_skill_score,
    severity_sort_key,
    expand_path
)


class SkillAnalyzer:
    """Analyzes Clawdbot skills for completeness and quality."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.skills_path = Path(config['skills_path'])
        self.memory_path = Path(config.get('memory_path', '~/clawd/memory'))
        self.excluded = config.get('excluded_skills', ['skill-evolver'])
        self.results = {}
        
    def analyze_all(self) -> Dict:
        """Analyze all skills in the skills directory."""
        skills = get_skill_dirs(self.skills_path, self.excluded)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'skills_path': str(self.skills_path),
            'total_skills': len(skills),
            'skills': {},
            'summary': {
                'total_score': 0,
                'avg_score': 0,
                'issues': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
                'healthy': 0,
                'needs_work': 0
            }
        }
        
        for skill_path in skills:
            skill_result = self.analyze_skill(skill_path)
            results['skills'][skill_path.name] = skill_result
            
            # Update summary
            results['summary']['total_score'] += skill_result['score']
            
            for issue in skill_result['issues']:
                if issue.startswith('CRITICAL'):
                    results['summary']['issues']['critical'] += 1
                elif issue.startswith('HIGH'):
                    results['summary']['issues']['high'] += 1
                elif issue.startswith('MEDIUM'):
                    results['summary']['issues']['medium'] += 1
                else:
                    results['summary']['issues']['low'] += 1
            
            if skill_result['score'] >= 80:
                results['summary']['healthy'] += 1
            else:
                results['summary']['needs_work'] += 1
        
        if results['total_skills'] > 0:
            results['summary']['avg_score'] = round(
                results['summary']['total_score'] / results['total_skills'], 1
            )
        
        self.results = results
        return results
    
    def analyze_skill(self, skill_path: Path) -> Dict:
        """Analyze a single skill."""
        result = {
            'name': skill_path.name,
            'path': str(skill_path),
            'score': 0,
            'status': 'unknown',
            'structure': {},
            'documentation': {},
            'scripts': [],
            'issues': [],
            'recommendations': []
        }
        
        # Parse structure
        result['structure'] = parse_skill_structure(skill_path)
        
        # Analyze SKILL.md
        skill_md_content = read_skill_md(skill_path)
        if skill_md_content:
            result['documentation'] = analyze_skill_md(skill_md_content)
        
        # Analyze scripts
        scripts_dir = skill_path / "scripts"
        if scripts_dir.exists():
            for script in scripts_dir.glob('*.py'):
                script_analysis = analyze_python_file(script)
                result['scripts'].append(script_analysis)
        
        # Calculate score
        result['score'], result['issues'] = calculate_skill_score(
            result['structure'],
            result['documentation'],
            result['scripts']
        )
        
        # Determine status
        if result['score'] >= 90:
            result['status'] = 'excellent'
        elif result['score'] >= 80:
            result['status'] = 'healthy'
        elif result['score'] >= 60:
            result['status'] = 'needs_work'
        else:
            result['status'] = 'critical'
        
        # Generate recommendations
        result['recommendations'] = self._generate_recommendations(result)
        
        return result
    
    def _generate_recommendations(self, result: Dict) -> List[str]:
        """Generate improvement recommendations based on analysis."""
        recommendations = []
        
        # Documentation recommendations
        if not result['structure'].get('has_skill_md'):
            recommendations.append("Create SKILL.md with overview, workflow, and examples")
        else:
            doc = result['documentation']
            if not doc.get('has_overview'):
                recommendations.append("Add overview/introduction section to SKILL.md")
            if not doc.get('has_workflow'):
                recommendations.append("Add workflow/usage section to SKILL.md")
            if not doc.get('has_examples'):
                recommendations.append("Add code examples to SKILL.md")
            if not doc.get('has_troubleshooting'):
                recommendations.append("Add troubleshooting section to SKILL.md")
            if not doc.get('has_version'):
                recommendations.append("Add version tracking to SKILL.md")
        
        # Script recommendations
        if not result['structure'].get('has_scripts'):
            recommendations.append("Create scripts/ directory with executable scripts")
        else:
            for script in result['scripts']:
                if not script.get('has_error_handling'):
                    recommendations.append(f"Add error handling to {script['path'].split('/')[-1]}")
                if not script.get('has_docstring'):
                    recommendations.append(f"Add docstring to {script['path'].split('/')[-1]}")
                if not script.get('has_logging'):
                    recommendations.append(f"Add logging to {script['path'].split('/')[-1]}")
        
        # Configuration recommendations
        if not result['structure'].get('has_references'):
            recommendations.append("Create references/ directory for config files")
        
        return recommendations[:5]  # Limit to top 5
    
    def analyze_metrics(self) -> Dict:
        """Analyze usage metrics from memory/transcripts."""
        metrics = {
            'available': False,
            'total_invocations': 0,
            'success_rate': 0,
            'error_rate': 0,
            'avg_tokens': 0,
            'by_skill': {}
        }
        
        memory_path = expand_path(self.memory_path)
        if not memory_path.exists():
            return metrics
        
        metrics['available'] = True
        
        # Look for transcript files
        transcripts_path = memory_path / "transcripts"
        if transcripts_path.exists():
            for transcript in transcripts_path.glob('*.json'):
                try:
                    with open(transcript) as f:
                        data = json.load(f)
                        # Parse transcript data for skill usage
                        # This is a placeholder - actual implementation depends on transcript format
                        metrics['total_invocations'] += 1
                except:
                    pass
        
        return metrics
    
    def generate_report(self, format: str = 'markdown') -> str:
        """Generate analysis report."""
        if not self.results:
            self.analyze_all()
        
        if format == 'json':
            return json.dumps(self.results, indent=2)
        
        # Markdown format
        r = self.results
        s = r['summary']
        
        report = f"""# Skill Evolution Report — {datetime.now().strftime('%Y-%m-%d')}

## Summary
- **Skills Analyzed**: {r['total_skills']}
- **Average Score**: {s['avg_score']}/100
- **Issues Found**: {s['issues']['critical'] + s['issues']['high'] + s['issues']['medium'] + s['issues']['low']}
- **Critical**: {s['issues']['critical']} | **High**: {s['issues']['high']} | **Medium**: {s['issues']['medium']} | **Low**: {s['issues']['low']}

## Skill Scores

| Skill | Score | Status |
|-------|-------|--------|
"""
        
        # Sort skills by score
        sorted_skills = sorted(
            r['skills'].items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        status_icons = {
            'excellent': '✅',
            'healthy': '✅',
            'needs_work': '⚠️',
            'critical': '❌'
        }
        
        for name, skill in sorted_skills:
            icon = status_icons.get(skill['status'], '❓')
            report += f"| {name} | {skill['score']} | {icon} {skill['status'].replace('_', ' ').title()} |\n"
        
        # Issues by severity
        all_issues = []
        for name, skill in r['skills'].items():
            for issue in skill['issues']:
                all_issues.append((name, issue))
        
        all_issues.sort(key=lambda x: severity_sort_key(x[1]))
        
        if any(i[1].startswith('CRITICAL') for i in all_issues):
            report += "\n## Critical Issues\n"
            for name, issue in all_issues:
                if issue.startswith('CRITICAL'):
                    report += f"- **{name}**: {issue.replace('CRITICAL: ', '')}\n"
        
        if any(i[1].startswith('HIGH') for i in all_issues):
            report += "\n## High Priority Issues\n"
            for name, issue in all_issues:
                if issue.startswith('HIGH'):
                    report += f"- **{name}**: {issue.replace('HIGH: ', '')}\n"
        
        if any(i[1].startswith('MEDIUM') for i in all_issues):
            report += "\n## Medium Priority Issues\n"
            for name, issue in all_issues:
                if issue.startswith('MEDIUM'):
                    report += f"- **{name}**: {issue.replace('MEDIUM: ', '')}\n"
        
        # Recommendations
        report += "\n## Top Recommendations\n"
        rec_count = 0
        for name, skill in sorted_skills:
            if rec_count >= 10:
                break
            for rec in skill['recommendations'][:2]:
                report += f"- **{name}**: {rec}\n"
                rec_count += 1
                if rec_count >= 10:
                    break
        
        # Next actions
        report += "\n## Next Actions\n"
        action_count = 0
        for name, skill in all_issues[:5]:
            if skill.startswith('CRITICAL') or skill.startswith('HIGH'):
                report += f"- [ ] Fix: {name} - {skill.split(': ', 1)[1] if ': ' in skill else skill}\n"
                action_count += 1
        
        if action_count == 0:
            report += "- [ ] Review medium priority issues\n"
            report += "- [ ] Add missing documentation sections\n"
        
        return report


def main():
    parser = argparse.ArgumentParser(description='Analyze Clawdbot skills')
    parser.add_argument('--config', '-c', help='Path to config file')
    parser.add_argument('--skill', '-s', help='Analyze specific skill only')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--format', '-f', choices=['markdown', 'json'], default='markdown')
    parser.add_argument('--include-metrics', action='store_true', help='Include usage metrics')
    parser.add_argument('--validate-config', action='store_true', help='Validate configuration')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    
    args = parser.parse_args()
    
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        print("Error: Config file not found. Creating default config...")
        # Use default config
        config = {
            'skills_path': '~/clawd/skills/',
            'memory_path': '~/clawd/memory/',
            'backup_path': '~/clawd/backups/',
            'excluded_skills': ['skill-evolver']
        }
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)
    
    if args.validate_config:
        print("Configuration:")
        print(json.dumps(config, indent=2))
        skills_path = expand_path(config['skills_path'])
        print(f"\nSkills path exists: {skills_path.exists()}")
        if skills_path.exists():
            print(f"Skills found: {len(list(skills_path.iterdir()))}")
        sys.exit(0)
    
    if args.debug:
        print(f"Config: {json.dumps(config, indent=2)}")
    
    analyzer = SkillAnalyzer(config)
    
    if args.skill:
        skill_path = Path(config['skills_path']) / args.skill
        if not skill_path.exists():
            print(f"Error: Skill '{args.skill}' not found at {skill_path}")
            sys.exit(1)
        result = analyzer.analyze_skill(skill_path)
        if args.format == 'json':
            output = json.dumps(result, indent=2)
        else:
            output = f"# Analysis: {args.skill}\n\n"
            output += f"**Score**: {result['score']}/100\n"
            output += f"**Status**: {result['status']}\n\n"
            output += "## Issues\n"
            for issue in sorted(result['issues'], key=severity_sort_key):
                output += f"- {issue}\n"
            output += "\n## Recommendations\n"
            for rec in result['recommendations']:
                output += f"- {rec}\n"
    else:
        analyzer.analyze_all()
        
        if args.include_metrics:
            metrics = analyzer.analyze_metrics()
            analyzer.results['metrics'] = metrics
        
        output = analyzer.generate_report(args.format)
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(output)
        print(f"Report saved to {output_path}")
    else:
        print(output)


if __name__ == "__main__":
    main()
