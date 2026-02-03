#!/usr/bin/env python3
"""
reasoning.py - Claude-style reasoning engine
Implements structured thinking, chain-of-thought, and self-reflection
"""

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from llm_client import LLMClient, LLMResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('reasoning')

MEMORY_PATH = Path.home() / 'clawd' / 'memory'


@dataclass
class ThinkingStep:
    """A single step in the reasoning chain."""
    step_type: str  # analyze, plan, execute, validate, reflect
    content: str
    confidence: float = 0.8
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ReasoningResult:
    """Result of a reasoning session."""
    goal: str
    conclusion: str
    steps: List[ThinkingStep]
    success: bool = True
    confidence: float = 0.8
    execution_time_ms: float = 0
    tokens_used: int = 0


class ReasoningEngine:
    """
    Claude-style reasoning engine.
    
    Implements:
    - Structured thinking (Goal → Context → Plan → Execute → Validate)
    - Chain-of-thought prompting
    - Self-reflection and correction
    - Confidence scoring
    """
    
    SYSTEM_PROMPT = """You are an autonomous AI agent assistant, designed to think and act like Claude.

Your thinking style:
1. **Structured**: Always use Goal → Assumptions → Plan → Execution → Result format
2. **Precise**: No fluff, maximum conciseness, technical English
3. **Confident**: Never say "I think", "probably", "maybe" - state facts or explicit assumptions
4. **Self-correcting**: If something seems wrong, acknowledge and fix it
5. **Practical**: Focus on working solutions, not theoretical discussions

When analyzing problems:
- Break down complex tasks into smaller steps
- Identify dependencies and blockers
- Consider edge cases and failure modes
- Propose multiple approaches when appropriate
- Choose the best approach with clear reasoning

When generating solutions:
- Provide complete, working code
- Include error handling
- Add logging where appropriate
- Document assumptions
- Test mentally before outputting

Format your response as structured JSON when asked for analysis."""

    REASONING_TEMPLATE = """**Goal**: {goal}

**Context**: {context}

**Task**: Analyze this situation and provide a structured response.

Required format:
```json
{{
  "analysis": "Your analysis of the situation",
  "assumptions": ["assumption 1", "assumption 2"],
  "plan": [
    {{"step": 1, "action": "...", "reason": "..."}},
    {{"step": 2, "action": "...", "reason": "..."}}
  ],
  "risks": ["risk 1", "risk 2"],
  "recommendation": "Your recommended approach",
  "confidence": 0.85
}}
```

Provide your analysis:"""

    REFLECTION_TEMPLATE = """Review your previous response:

**Original Goal**: {goal}
**Your Response**: {response}

Questions to consider:
1. Does this fully address the goal?
2. Are there any logical errors?
3. Did you miss any edge cases?
4. Is the solution practical and complete?
5. What could be improved?

If you find issues, provide corrections. If the response is good, confirm it.

Format:
```json
{{
  "assessment": "good" | "needs_improvement",
  "issues_found": [],
  "corrections": "...",
  "final_confidence": 0.9
}}
```"""

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.llm = LLMClient(self.config.get('llm', {}))
        self.memory = self._load_memory()
        self.max_iterations = self.config.get('max_iterations', 5)
        self.min_confidence = self.config.get('min_confidence', 0.7)
        self.verbose = self.config.get('verbose', True)
        
    def _load_memory(self) -> Dict:
        """Load reasoning memory."""
        memory_file = MEMORY_PATH / 'reasoning_memory.json'
        if memory_file.exists():
            with open(memory_file) as f:
                return json.load(f)
        return {
            'successful_patterns': [],
            'failed_patterns': [],
            'learned_rules': []
        }
    
    def _save_memory(self):
        """Save reasoning memory."""
        MEMORY_PATH.mkdir(parents=True, exist_ok=True)
        memory_file = MEMORY_PATH / 'reasoning_memory.json'
        with open(memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def reason(self, 
               goal: str,
               context: str = "",
               constraints: List[str] = None,
               examples: List[Dict] = None) -> ReasoningResult:
        """
        Execute structured reasoning process.
        
        Args:
            goal: What we're trying to achieve
            context: Relevant background information
            constraints: Limitations to consider
            examples: Similar past cases for reference
        
        Returns:
            ReasoningResult with conclusion and steps
        """
        import time
        start_time = time.time()
        
        steps = []
        total_tokens = 0
        
        # Step 1: Initial Analysis
        if self.verbose:
            logger.info(f"Reasoning about: {goal[:100]}...")
        
        analysis_prompt = self.REASONING_TEMPLATE.format(
            goal=goal,
            context=context or "No additional context provided"
        )
        
        if constraints:
            analysis_prompt += f"\n\nConstraints:\n" + "\n".join(f"- {c}" for c in constraints)
        
        if examples:
            analysis_prompt += f"\n\nSimilar cases:\n" + json.dumps(examples[:3], indent=2)
        
        # Check memory for similar patterns
        similar = self._find_similar_patterns(goal)
        if similar:
            analysis_prompt += f"\n\nPrevious successful approach for similar task:\n{similar}"
        
        response = self.llm.complete(
            messages=[{'role': 'user', 'content': analysis_prompt}],
            system=self.SYSTEM_PROMPT
        )
        
        if not response.success:
            return ReasoningResult(
                goal=goal,
                conclusion=f"Failed to reason: {response.error}",
                steps=steps,
                success=False,
                confidence=0
            )
        
        total_tokens += response.tokens_used
        
        # Parse analysis
        analysis = self._parse_json_response(response.content)
        
        steps.append(ThinkingStep(
            step_type='analyze',
            content=response.content,
            confidence=analysis.get('confidence', 0.8) if analysis else 0.5
        ))
        
        # Step 2: Self-reflection (if enabled)
        if self.config.get('self_reflect', True):
            reflection = self._reflect(goal, response.content)
            total_tokens += reflection.get('tokens', 0)
            
            steps.append(ThinkingStep(
                step_type='reflect',
                content=json.dumps(reflection),
                confidence=reflection.get('final_confidence', 0.8)
            ))
            
            # Apply corrections if needed
            if reflection.get('assessment') == 'needs_improvement':
                steps.append(ThinkingStep(
                    step_type='correct',
                    content=reflection.get('corrections', ''),
                    confidence=reflection.get('final_confidence', 0.7)
                ))
        
        # Step 3: Generate conclusion
        conclusion = self._generate_conclusion(goal, steps)
        
        # Calculate final confidence
        confidences = [s.confidence for s in steps]
        final_confidence = sum(confidences) / len(confidences) if confidences else 0.5
        
        # Record to memory
        self._record_pattern(goal, steps, final_confidence)
        
        execution_time = (time.time() - start_time) * 1000
        
        return ReasoningResult(
            goal=goal,
            conclusion=conclusion,
            steps=steps,
            success=True,
            confidence=final_confidence,
            execution_time_ms=execution_time,
            tokens_used=total_tokens
        )
    
    def _reflect(self, goal: str, response: str) -> Dict:
        """Self-reflect on response quality."""
        reflection_prompt = self.REFLECTION_TEMPLATE.format(
            goal=goal,
            response=response[:2000]  # Truncate for token limits
        )
        
        result = self.llm.complete(
            messages=[{'role': 'user', 'content': reflection_prompt}],
            system=self.SYSTEM_PROMPT
        )
        
        if not result.success:
            return {'assessment': 'unknown', 'final_confidence': 0.7}
        
        parsed = self._parse_json_response(result.content)
        parsed['tokens'] = result.tokens_used
        return parsed or {'assessment': 'good', 'final_confidence': 0.8}
    
    def _generate_conclusion(self, goal: str, steps: List[ThinkingStep]) -> str:
        """Generate final conclusion from reasoning steps."""
        # Extract key insights from steps
        insights = []
        for step in steps:
            if step.step_type == 'analyze':
                parsed = self._parse_json_response(step.content)
                if parsed:
                    insights.append(f"Analysis: {parsed.get('recommendation', 'N/A')}")
            elif step.step_type == 'correct':
                insights.append(f"Correction: {step.content[:200]}")
        
        if not insights:
            return "Unable to reach conclusion"
        
        return "\n".join(insights)
    
    def _parse_json_response(self, content: str) -> Optional[Dict]:
        """Extract JSON from LLM response."""
        # Try to find JSON block
        json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass
        
        # Try direct JSON parse
        try:
            return json.loads(content)
        except:
            pass
        
        # Try to find JSON-like structure
        try:
            start = content.find('{')
            end = content.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(content[start:end])
        except:
            pass
        
        return None
    
    def _find_similar_patterns(self, goal: str) -> Optional[str]:
        """Find similar successful patterns from memory."""
        goal_lower = goal.lower()
        keywords = set(goal_lower.split())
        
        best_match = None
        best_score = 0
        
        for pattern in self.memory.get('successful_patterns', [])[-50:]:
            pattern_keywords = set(pattern.get('goal', '').lower().split())
            overlap = len(keywords & pattern_keywords)
            
            if overlap > best_score and overlap >= 2:
                best_score = overlap
                best_match = pattern
        
        if best_match:
            return best_match.get('approach', '')
        return None
    
    def _record_pattern(self, goal: str, steps: List[ThinkingStep], confidence: float):
        """Record reasoning pattern to memory."""
        pattern = {
            'goal': goal,
            'timestamp': datetime.now().isoformat(),
            'confidence': confidence,
            'approach': steps[-1].content[:500] if steps else ''
        }
        
        if confidence >= 0.7:
            self.memory['successful_patterns'].append(pattern)
            # Keep last 100
            self.memory['successful_patterns'] = self.memory['successful_patterns'][-100:]
        else:
            self.memory['failed_patterns'].append(pattern)
            self.memory['failed_patterns'] = self.memory['failed_patterns'][-50:]
        
        self._save_memory()
    
    def decide(self,
               question: str,
               options: List[Dict],
               criteria: List[str] = None) -> Dict:
        """
        Make a decision between options.
        
        Args:
            question: The decision to make
            options: List of options with 'name' and 'description'
            criteria: Evaluation criteria
        
        Returns:
            Decision with chosen option and reasoning
        """
        criteria = criteria or ['effectiveness', 'simplicity', 'reliability']
        
        prompt = f"""**Decision Required**: {question}

**Options**:
{json.dumps(options, indent=2)}

**Evaluation Criteria**: {', '.join(criteria)}

Evaluate each option against the criteria and choose the best one.

Format:
```json
{{
  "evaluations": [
    {{"option": "name", "scores": {{"criterion": score}}, "total": X}},
    ...
  ],
  "chosen": "option name",
  "reasoning": "why this is the best choice",
  "confidence": 0.85
}}
```"""
        
        response = self.llm.complete(
            messages=[{'role': 'user', 'content': prompt}],
            system=self.SYSTEM_PROMPT
        )
        
        if not response.success:
            return {'error': response.error, 'chosen': options[0]['name'] if options else None}
        
        result = self._parse_json_response(response.content)
        return result or {'chosen': options[0]['name'] if options else None, 'reasoning': response.content}
    
    def decompose_task(self, task: str, max_steps: int = 10) -> List[Dict]:
        """
        Break down a complex task into smaller steps.
        
        Args:
            task: Complex task description
            max_steps: Maximum number of steps
        
        Returns:
            List of subtasks with dependencies
        """
        prompt = f"""**Task**: {task}

Break this down into smaller, actionable steps. Each step should be:
- Specific and concrete
- Independently executable
- Properly ordered with dependencies

Format:
```json
{{
  "steps": [
    {{
      "id": 1,
      "action": "what to do",
      "details": "how to do it",
      "dependencies": [],
      "estimated_time": "5m"
    }},
    ...
  ],
  "total_estimated_time": "30m",
  "complexity": "medium"
}}
```

Maximum {max_steps} steps."""
        
        response = self.llm.complete(
            messages=[{'role': 'user', 'content': prompt}],
            system=self.SYSTEM_PROMPT
        )
        
        if not response.success:
            return [{'id': 1, 'action': task, 'details': 'Execute as single task'}]
        
        result = self._parse_json_response(response.content)
        return result.get('steps', []) if result else []


def reason(goal: str, context: str = "") -> str:
    """Simple interface for reasoning."""
    engine = ReasoningEngine()
    result = engine.reason(goal, context)
    return result.conclusion


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Reasoning Engine')
    parser.add_argument('--goal', '-g', help='Goal to reason about')
    parser.add_argument('--context', '-c', default='', help='Additional context')
    parser.add_argument('--decide', '-d', help='Decision question')
    parser.add_argument('--options', nargs='+', help='Options for decision')
    parser.add_argument('--decompose', help='Task to decompose')
    parser.add_argument('--verbose', '-v', action='store_true')
    
    args = parser.parse_args()
    
    config = {'verbose': args.verbose, 'self_reflect': True}
    engine = ReasoningEngine(config)
    
    if args.goal:
        result = engine.reason(args.goal, args.context)
        print(f"\n{'='*60}")
        print(f"Goal: {result.goal}")
        print(f"Confidence: {result.confidence:.0%}")
        print(f"Time: {result.execution_time_ms:.0f}ms")
        print(f"{'='*60}")
        print(f"\nConclusion:\n{result.conclusion}")
        
    elif args.decide and args.options:
        options = [{'name': o, 'description': o} for o in args.options]
        result = engine.decide(args.decide, options)
        print(json.dumps(result, indent=2))
        
    elif args.decompose:
        steps = engine.decompose_task(args.decompose)
        print(json.dumps(steps, indent=2))
        
    else:
        print("Use --goal, --decide, or --decompose")
