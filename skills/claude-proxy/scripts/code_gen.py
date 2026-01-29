#!/usr/bin/env python3
"""
code_gen.py - Claude-style code generation
Generates Python, Bash, configs, and full skills
"""

import ast
import json
import logging
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from llm_client import LLMClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('code-gen')

SKILLS_PATH = Path.home() / 'clawd' / 'skills'
TEMPLATES_PATH = Path(__file__).parent.parent / 'templates'


@dataclass
class GeneratedCode:
    """Generated code result."""
    code: str
    language: str
    filename: str
    description: str
    valid: bool = True
    validation_error: str = None
    tests: List[str] = None


class CodeGenerator:
    """
    Claude-style code generator.
    
    Features:
    - Python, Bash, JSON generation
    - Syntax validation
    - Style enforcement
    - Template-based generation
    - Auto-documentation
    """
    
    SYSTEM_PROMPT = """You are an expert code generator. Generate clean, production-ready code.

Code style requirements:
1. **Python**:
   - Type hints for all functions
   - Docstrings for classes and public functions
   - Logging instead of print (except CLI output)
   - Error handling with specific exceptions
   - Follow PEP 8
   - Use pathlib for paths
   - Use dataclasses for data structures

2. **Structure**:
   - Imports at top, sorted (stdlib, third-party, local)
   - Constants in UPPER_CASE
   - Main logic in functions/classes, not module level
   - if __name__ == "__main__" block for scripts

3. **Error handling**:
   - Catch specific exceptions
   - Log errors with context
   - Return meaningful error messages
   - Never silently fail

4. **Documentation**:
   - Module docstring explaining purpose
   - Function docstrings with Args, Returns, Raises
   - Inline comments for complex logic only

Output ONLY the code, no explanations. Use ```python or ```bash markers."""

    PYTHON_TEMPLATE = '''#!/usr/bin/env python3
"""
{module_name} - {description}
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('{module_name}')


{code}


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description='{description}')
    # Add arguments here
    args = parser.parse_args()
    
    # Main logic here
    logger.info("Starting {module_name}")


if __name__ == "__main__":
    main()
'''

    SKILL_TEMPLATE = '''# {skill_name}

## Overview

{description}

## Quick Start

```bash
python scripts/main.py
```

## Workflow

1. Configure settings in `references/config.json`
2. Run the skill
3. Check output

## Configuration

Edit `references/config.json`:

```json
{config_example}
```

## Version

- v1.0.0 ({date}): Initial release
'''

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.llm = LLMClient(self.config.get('llm', {}))
        self.validate_syntax = self.config.get('validate_syntax', True)
        self.auto_format = self.config.get('auto_format', True)
        
    def generate(self,
                 description: str,
                 language: str = 'python',
                 context: str = None,
                 examples: List[str] = None) -> GeneratedCode:
        """
        Generate code from description.
        
        Args:
            description: What the code should do
            language: Target language (python, bash, json)
            context: Additional context (existing code, requirements)
            examples: Example inputs/outputs
        
        Returns:
            GeneratedCode with result
        """
        prompt = f"""Generate {language} code for:

**Description**: {description}

"""
        if context:
            prompt += f"**Context**:\n{context}\n\n"
        
        if examples:
            prompt += f"**Examples**:\n" + "\n".join(f"- {e}" for e in examples) + "\n\n"
        
        prompt += f"Generate complete, working {language} code:"
        
        response = self.llm.complete(
            messages=[{'role': 'user', 'content': prompt}],
            system=self.SYSTEM_PROMPT
        )
        
        if not response.success:
            return GeneratedCode(
                code='',
                language=language,
                filename='error.py',
                description=description,
                valid=False,
                validation_error=response.error
            )
        
        # Extract code from response
        code = self._extract_code(response.content, language)
        
        # Determine filename
        filename = self._generate_filename(description, language)
        
        # Validate if Python
        valid = True
        validation_error = None
        
        if language == 'python' and self.validate_syntax:
            valid, validation_error = self._validate_python(code)
        
        return GeneratedCode(
            code=code,
            language=language,
            filename=filename,
            description=description,
            valid=valid,
            validation_error=validation_error
        )
    
    def generate_function(self,
                         name: str,
                         description: str,
                         params: List[Dict] = None,
                         returns: str = None) -> str:
        """Generate a single function."""
        params = params or []
        
        params_str = ", ".join([
            f"{p['name']}: {p.get('type', 'Any')}" + 
            (f" = {p['default']}" if 'default' in p else '')
            for p in params
        ])
        
        prompt = f"""Generate a Python function:

Name: {name}
Description: {description}
Parameters: {json.dumps(params)}
Returns: {returns or 'None'}

Requirements:
- Include type hints
- Include docstring
- Include error handling
- Be concise but complete

Generate only the function code:"""

        response = self.llm.complete(
            messages=[{'role': 'user', 'content': prompt}],
            system=self.SYSTEM_PROMPT
        )
        
        if not response.success:
            return f"# Error generating function: {response.error}"
        
        return self._extract_code(response.content, 'python')
    
    def generate_skill(self,
                      skill_name: str,
                      description: str,
                      features: List[str] = None) -> Dict[str, str]:
        """
        Generate a complete Clawdbot skill.
        
        Args:
            skill_name: Name of the skill
            description: What the skill does
            features: List of features to implement
        
        Returns:
            Dict with file paths and contents
        """
        features = features or []
        
        files = {}
        
        # Generate SKILL.md
        config_example = json.dumps({
            "enabled": True,
            "settings": {}
        }, indent=2)
        
        files['SKILL.md'] = self.SKILL_TEMPLATE.format(
            skill_name=skill_name,
            description=description,
            config_example=config_example,
            date=datetime.now().strftime('%Y-%m-%d')
        )
        
        # Generate main.py
        main_prompt = f"""Generate the main script for a Clawdbot skill:

Skill: {skill_name}
Description: {description}
Features: {', '.join(features) if features else 'Basic functionality'}

Requirements:
- Follow the standard skill structure
- Include argparse for CLI
- Include logging
- Include config loading from references/config.json
- Implement the main functionality
- Include proper error handling

Generate complete main.py:"""

        response = self.llm.complete(
            messages=[{'role': 'user', 'content': main_prompt}],
            system=self.SYSTEM_PROMPT
        )
        
        main_code = self._extract_code(response.content, 'python') if response.success else ''
        
        # Wrap in template if too short
        if len(main_code) < 200:
            main_code = self.PYTHON_TEMPLATE.format(
                module_name=skill_name.replace('-', '_'),
                description=description,
                code=f"# TODO: Implement {skill_name}\npass"
            )
        
        files['scripts/main.py'] = main_code
        
        # Generate config.json
        files['references/config.json'] = json.dumps({
            "enabled": True,
            "settings": {
                feature.lower().replace(' ', '_'): True
                for feature in features[:5]
            }
        }, indent=2)
        
        return files
    
    def improve_code(self,
                    code: str,
                    issues: List[str] = None,
                    style: str = 'claude') -> Tuple[str, List[str]]:
        """
        Improve existing code.
        
        Args:
            code: Original code
            issues: Known issues to fix
            style: Target style (claude, pep8, minimal)
        
        Returns:
            Tuple of (improved_code, changes_made)
        """
        issues_str = "\n".join(f"- {i}" for i in issues) if issues else "No specific issues"
        
        prompt = f"""Improve this code:

```python
{code}
```

Known issues:
{issues_str}

Requirements:
- Fix all issues
- Improve code quality
- Add missing error handling
- Add missing documentation
- Keep functionality identical

Return the improved code and list changes made.

Format:
```python
<improved code>
```

Changes:
- change 1
- change 2"""

        response = self.llm.complete(
            messages=[{'role': 'user', 'content': prompt}],
            system=self.SYSTEM_PROMPT
        )
        
        if not response.success:
            return code, [f"Error: {response.error}"]
        
        improved = self._extract_code(response.content, 'python')
        
        # Extract changes
        changes = []
        changes_match = re.search(r'Changes:\s*((?:- .+\n?)+)', response.content)
        if changes_match:
            changes = [
                line.strip('- ').strip()
                for line in changes_match.group(1).split('\n')
                if line.strip().startswith('-')
            ]
        
        return improved, changes
    
    def fix_error(self, code: str, error: str) -> Tuple[str, str]:
        """
        Fix code based on error message.
        
        Args:
            code: Code with error
            error: Error message
        
        Returns:
            Tuple of (fixed_code, explanation)
        """
        prompt = f"""Fix this code error:

Code:
```python
{code}
```

Error:
```
{error}
```

Analyze the error and provide fixed code.

Format:
```python
<fixed code>
```

Explanation: <what was wrong and how you fixed it>"""

        response = self.llm.complete(
            messages=[{'role': 'user', 'content': prompt}],
            system=self.SYSTEM_PROMPT
        )
        
        if not response.success:
            return code, f"Could not fix: {response.error}"
        
        fixed = self._extract_code(response.content, 'python')
        
        # Extract explanation
        explanation = ""
        exp_match = re.search(r'Explanation:\s*(.+)', response.content, re.DOTALL)
        if exp_match:
            explanation = exp_match.group(1).strip()
        
        return fixed, explanation
    
    def _extract_code(self, content: str, language: str) -> str:
        """Extract code block from response."""
        # Try language-specific block
        pattern = rf'```{language}\s*(.*?)\s*```'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Try generic code block
        match = re.search(r'```\s*(.*?)\s*```', content, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Return content as-is if no blocks found
        return content.strip()
    
    def _validate_python(self, code: str) -> Tuple[bool, Optional[str]]:
        """Validate Python syntax."""
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, f"Syntax error at line {e.lineno}: {e.msg}"
    
    def _generate_filename(self, description: str, language: str) -> str:
        """Generate appropriate filename."""
        # Extract key words
        words = re.findall(r'\b\w+\b', description.lower())
        meaningful = [w for w in words if len(w) > 3 and w not in 
                     ['the', 'and', 'for', 'that', 'this', 'with', 'from']]
        
        name = '_'.join(meaningful[:3]) if meaningful else 'generated'
        
        ext = {
            'python': '.py',
            'bash': '.sh',
            'json': '.json',
            'yaml': '.yaml',
            'markdown': '.md'
        }.get(language, '.txt')
        
        return name + ext
    
    def save_generated(self, 
                      generated: GeneratedCode,
                      output_dir: Path = None) -> Path:
        """Save generated code to file."""
        output_dir = output_dir or Path.cwd()
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / generated.filename
        
        with open(output_path, 'w') as f:
            f.write(generated.code)
        
        # Make executable if bash
        if generated.language == 'bash':
            output_path.chmod(0o755)
        
        logger.info(f"Saved: {output_path}")
        return output_path


def generate(description: str, language: str = 'python') -> str:
    """Simple code generation interface."""
    gen = CodeGenerator()
    result = gen.generate(description, language)
    return result.code if result.valid else f"# Error: {result.validation_error}\n{result.code}"


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Code Generator')
    parser.add_argument('--generate', '-g', help='Generate code from description')
    parser.add_argument('--language', '-l', default='python', help='Target language')
    parser.add_argument('--function', '-f', help='Generate function with this name')
    parser.add_argument('--skill', '-s', help='Generate skill with this name')
    parser.add_argument('--improve', '-i', help='File to improve')
    parser.add_argument('--fix', help='File with error to fix')
    parser.add_argument('--error', help='Error message for --fix')
    parser.add_argument('--output', '-o', help='Output file/directory')
    
    args = parser.parse_args()
    
    gen = CodeGenerator()
    
    if args.generate:
        result = gen.generate(args.generate, args.language)
        if args.output:
            result.filename = args.output
            gen.save_generated(result, Path(args.output).parent)
        else:
            print(result.code)
        if not result.valid:
            print(f"\n# Warning: {result.validation_error}", file=__import__('sys').stderr)
            
    elif args.function:
        code = gen.generate_function(args.function, args.generate or 'No description')
        print(code)
        
    elif args.skill:
        files = gen.generate_skill(args.skill, args.generate or 'A Clawdbot skill')
        if args.output:
            skill_path = Path(args.output) / args.skill
        else:
            skill_path = SKILLS_PATH / args.skill
        
        for rel_path, content in files.items():
            full_path = skill_path / rel_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
            print(f"Created: {full_path}")
            
    elif args.improve:
        with open(args.improve) as f:
            code = f.read()
        improved, changes = gen.improve_code(code)
        print(improved)
        print("\n# Changes made:", file=__import__('sys').stderr)
        for c in changes:
            print(f"#   - {c}", file=__import__('sys').stderr)
            
    elif args.fix and args.error:
        with open(args.fix) as f:
            code = f.read()
        fixed, explanation = gen.fix_error(code, args.error)
        print(fixed)
        print(f"\n# {explanation}", file=__import__('sys').stderr)
        
    else:
        parser.print_help()
