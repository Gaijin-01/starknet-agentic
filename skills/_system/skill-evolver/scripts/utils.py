#!/usr/bin/env python3
"""
skill-evolver utilities
Shared functions for analysis and evolution
"""

import os
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib


def expand_path(path: str) -> Path:
    """Expand ~ and environment variables in path."""
    return Path(os.path.expanduser(os.path.expandvars(path)))


def load_config(config_path: Optional[str] = None) -> Dict:
    """Load configuration from JSON file."""
    if config_path is None:
        config_path = Path(__file__).parent.parent / "references" / "config.json"
    else:
        config_path = expand_path(config_path)
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Expand paths in config
    for key in ['skills_path', 'memory_path', 'backup_path']:
        if key in config:
            config[key] = str(expand_path(config[key]))
    
    return config


def get_skill_dirs(skills_path: str, excluded: List[str] = None) -> List[Path]:
    """Get all skill directories."""
    excluded = excluded or []
    skills_path = expand_path(skills_path)
    
    if not skills_path.exists():
        return []
    
    skills = []
    
    # First, check for skills directly in the root
    for item in skills_path.iterdir():
        if item.is_dir() and item.name not in excluded and not item.name.startswith('.'):
            # Check if it's a valid skill (has SKILL.md)
            if (item / "SKILL.md").exists():
                skills.append(item)
    
    # If no skills found directly, look inside subdirectories (_system, _integrations, etc.)
    if not skills:
        for category in ['_system', '_integrations', 'available_skills']:
            category_path = skills_path / category
            if category_path.exists() and category_path.is_dir():
                for item in category_path.iterdir():
                    if item.is_dir() and item.name not in excluded:
                        # Check if it's a valid skill (has SKILL.md)
                        if (item / "SKILL.md").exists():
                            skills.append(item)
    
    return sorted(skills)


def read_skill_md(skill_path: Path) -> Optional[str]:
    """Read SKILL.md content from a skill directory."""
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        with open(skill_md, 'r', encoding='utf-8') as f:
            return f.read()
    return None


def parse_skill_structure(skill_path: Path) -> Dict:
    """Parse skill directory structure."""
    structure = {
        'name': skill_path.name,
        'path': str(skill_path),
        'has_skill_md': False,
        'has_scripts': False,
        'has_references': False,
        'has_assets': False,
        'scripts': [],
        'references': [],
        'assets': [],
        'total_files': 0,
        'total_lines': 0
    }
    
    if (skill_path / "SKILL.md").exists():
        structure['has_skill_md'] = True
        structure['skill_md_lines'] = len(open(skill_path / "SKILL.md").readlines())
    
    scripts_dir = skill_path / "scripts"
    if scripts_dir.exists():
        structure['has_scripts'] = True
        for script in scripts_dir.glob('*'):
            if script.is_file():
                structure['scripts'].append(script.name)
                structure['total_files'] += 1
                try:
                    structure['total_lines'] += len(open(script).readlines())
                except:
                    pass
    
    refs_dir = skill_path / "references"
    if refs_dir.exists():
        structure['has_references'] = True
        for ref in refs_dir.glob('*'):
            if ref.is_file():
                structure['references'].append(ref.name)
                structure['total_files'] += 1
    
    assets_dir = skill_path / "assets"
    if assets_dir.exists():
        structure['has_assets'] = True
        for asset in assets_dir.glob('*'):
            if asset.is_file():
                structure['assets'].append(asset.name)
                structure['total_files'] += 1
    
    return structure


def analyze_skill_md(content: str) -> Dict:
    """Analyze SKILL.md content for completeness."""
    analysis = {
        'has_overview': False,
        'has_workflow': False,
        'has_examples': False,
        'has_config': False,
        'has_troubleshooting': False,
        'has_version': False,
        'sections': [],
        'code_blocks': 0,
        'word_count': 0
    }
    
    # Extract sections (headers)
    headers = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
    analysis['sections'] = headers
    
    content_lower = content.lower()
    
    # Check for key sections
    analysis['has_overview'] = bool(re.search(r'#+\s*(overview|introduction|about)', content_lower))
    analysis['has_workflow'] = bool(re.search(r'#+\s*(workflow|how it works|process|usage)', content_lower))
    analysis['has_examples'] = bool(re.search(r'#+\s*(example|usage|quick start)', content_lower))
    analysis['has_config'] = bool(re.search(r'#+\s*(config|configuration|settings|setup)', content_lower))
    analysis['has_troubleshooting'] = bool(re.search(r'#+\s*(troubleshoot|debug|faq|issues)', content_lower))
    analysis['has_version'] = bool(re.search(r'(v\d+\.\d+|version\s*:?\s*\d+)', content_lower))
    
    # Count code blocks
    analysis['code_blocks'] = len(re.findall(r'```', content)) // 2
    
    # Word count
    analysis['word_count'] = len(content.split())
    
    return analysis


def analyze_python_file(file_path: Path) -> Dict:
    """Analyze a Python file for quality metrics."""
    analysis = {
        'path': str(file_path),
        'lines': 0,
        'functions': [],
        'classes': [],
        'has_docstring': False,
        'has_error_handling': False,
        'has_logging': False,
        'has_type_hints': False,
        'imports': [],
        'issues': []
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception as e:
        analysis['issues'].append(f"Cannot read file: {e}")
        return analysis
    
    analysis['lines'] = len(lines)
    
    # Check for module docstring
    if content.strip().startswith('"""') or content.strip().startswith("'''"):
        analysis['has_docstring'] = True
    
    # Extract functions
    analysis['functions'] = re.findall(r'def\s+(\w+)\s*\(', content)
    
    # Extract classes
    analysis['classes'] = re.findall(r'class\s+(\w+)\s*[:\(]', content)
    
    # Check for error handling
    analysis['has_error_handling'] = 'try:' in content or 'except' in content
    
    # Check for logging
    analysis['has_logging'] = 'logging' in content or 'logger' in content.lower() or 'print(' in content
    
    # Check for type hints
    analysis['has_type_hints'] = bool(re.search(r'def\s+\w+\s*\([^)]*:\s*\w+', content))
    
    # Extract imports
    analysis['imports'] = re.findall(r'^(?:from\s+(\S+)|import\s+(\S+))', content, re.MULTILINE)
    analysis['imports'] = [i[0] or i[1] for i in analysis['imports']]
    
    # Check for common issues
    if not analysis['has_error_handling'] and len(analysis['functions']) > 2:
        analysis['issues'].append("No error handling in file with multiple functions")
    
    if 'requests' in str(analysis['imports']) and 'timeout' not in content:
        analysis['issues'].append("HTTP requests without timeout parameter")
    
    if 'api_key' in content.lower() or 'apikey' in content.lower():
        if re.search(r'["\'][a-zA-Z0-9]{20,}["\']', content):
            analysis['issues'].append("Possible hardcoded API key detected")
    
    return analysis


def calculate_skill_score(structure: Dict, skill_md_analysis: Dict, script_analyses: List[Dict]) -> Tuple[int, List[str]]:
    """Calculate overall skill health score (0-100)."""
    score = 0
    issues = []
    
    # SKILL.md exists (20 points)
    if structure['has_skill_md']:
        score += 20
    else:
        issues.append("CRITICAL: Missing SKILL.md")
    
    # Documentation quality (15 points)
    if skill_md_analysis:
        doc_score = 0
        if skill_md_analysis['has_overview']:
            doc_score += 3
        else:
            issues.append("MEDIUM: Missing overview section")
        if skill_md_analysis['has_workflow']:
            doc_score += 4
        else:
            issues.append("MEDIUM: Missing workflow section")
        if skill_md_analysis['has_examples']:
            doc_score += 4
        else:
            issues.append("MEDIUM: Missing examples")
        if skill_md_analysis['code_blocks'] >= 2:
            doc_score += 4
        score += doc_score
    
    # Scripts present (20 points)
    if structure['has_scripts'] and structure['scripts']:
        score += 20
    elif structure['has_scripts']:
        score += 10
        issues.append("LOW: Scripts directory empty")
    else:
        issues.append("HIGH: No scripts directory")
    
    # Error handling (15 points)
    if script_analyses:
        has_error_handling = any(s['has_error_handling'] for s in script_analyses)
        if has_error_handling:
            score += 15
        else:
            issues.append("HIGH: No error handling in scripts")
    
    # Dependencies declared (10 points)
    if skill_md_analysis and skill_md_analysis.get('has_config'):
        score += 10
    else:
        if structure['has_references']:
            score += 5
        issues.append("LOW: Dependencies/config not documented")
    
    # Examples provided (10 points)
    if skill_md_analysis and skill_md_analysis.get('code_blocks', 0) >= 1:
        score += 10
    else:
        issues.append("MEDIUM: No code examples in documentation")
    
    # Version tracking (10 points)
    if skill_md_analysis and skill_md_analysis.get('has_version'):
        score += 10
    else:
        issues.append("LOW: No version tracking")
    
    # Script-specific issues
    for sa in script_analyses:
        issues.extend([f"MEDIUM: {sa['path'].split('/')[-1]}: {i}" for i in sa['issues']])
    
    return min(score, 100), issues


def create_backup(file_path: Path, backup_dir: Path) -> Path:
    """Create timestamped backup of a file."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create skill-specific backup directory
    skill_name = file_path.parent.name
    if file_path.parent.name in ['scripts', 'references', 'assets']:
        skill_name = file_path.parent.parent.name
    
    backup_skill_dir = backup_dir / skill_name
    backup_skill_dir.mkdir(parents=True, exist_ok=True)
    
    backup_path = backup_skill_dir / f"{file_path.name}.{timestamp}"
    shutil.copy2(file_path, backup_path)
    
    return backup_path


def restore_backup(backup_path: Path, original_path: Path) -> bool:
    """Restore a file from backup."""
    if not backup_path.exists():
        return False
    shutil.copy2(backup_path, original_path)
    return True


def log_change(log_path: Path, change: Dict):
    """Log a change to the evolution log."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        **change
    }
    
    # Append to log file
    with open(log_path, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')


def get_file_hash(file_path: Path) -> str:
    """Get SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def format_report(title: str, sections: Dict[str, str]) -> str:
    """Format a markdown report."""
    lines = [f"# {title}", ""]
    
    for section_title, content in sections.items():
        lines.append(f"## {section_title}")
        lines.append(content)
        lines.append("")
    
    return "\n".join(lines)


def severity_sort_key(issue: str) -> int:
    """Sort key for issue severity."""
    if issue.startswith("CRITICAL"):
        return 0
    elif issue.startswith("HIGH"):
        return 1
    elif issue.startswith("MEDIUM"):
        return 2
    else:
        return 3


if __name__ == "__main__":
    # Test utilities
    print("Testing utils...")
    config = load_config()
    print(f"Config loaded: {json.dumps(config, indent=2)}")
