"""
Adaptive Routing Classifier for Clawdbot

This module scores user queries based on complexity (1-100) and determines
appropriate model tiers for routing.
"""

import re
from dataclasses import dataclass
from typing import Literal


# Complexity indicators for scoring
COMPLEXITY_INDICATORS = {
    # High complexity indicators (70-100)
    "architectural": 30,
    "system design": 30,
    "distributed systems": 35,
    "scalability": 30,
    "microservices": 30,
    "multi-step": 25,
    "comprehensive analysis": 30,
    "research": 25,
    "trade-offs": 25,
    "performance optimization": 30,
    "security audit": 30,
    "refactoring": 20,
    "migration": 20,
    "evaluation": 20,
    "comparison": 15,
    "design patterns": 20,
    "best practices": 15,
    "deep dive": 30,
    "end-to-end": 25,
    "root cause": 25,
    "bottlenecks": 25,
    
    # Medium complexity indicators (30-70)
    "function": 15,
    "class": 15,
    "api": 15,
    "debug": 15,
    "fix": 12,
    "implement": 18,
    "create": 12,
    "build": 15,
    "explain": 12,
    "analyze": 20,
    "summarize": 15,
    "document": 10,
    "test": 12,
    "refactor": 15,
    "optimize": 20,
    "review": 15,
    "convert": 8,
    "parse": 10,
    "validate": 8,
    "generate": 12,
    "write code": 15,
    "coding": 15,
    "programming": 15,
    "script": 10,
    "database": 18,
    "query": 10,
    
    # Simple query indicators (1-30)
    "what is": 5,
    "who is": 5,
    "when did": 5,
    "where is": 5,
    "define": 6,
    "hello": 2,
    "hi": 2,
    "hey": 2,
    "thanks": 2,
    "thank you": 2,
    "goodbye": 2,
    "bye": 2,
    "yes": 1,
    "no": 1,
    "ok": 1,
    "sure": 1,
    "maybe": 1,
}

# Query patterns
PATTERNS = {
    "greeting": r"^(hi|hello|hey|good morning|good afternoon|good evening|howdy)\b",
    "simple_question": r"^(what|who|when|where|why|how)\s+(is|are|was|were|do|does|did|can|could)\s+",
    "gratitude": r"^(thanks|thank you|appreciate|cheers)\b",
    "code_request": r"(write|create|implement|build|make|develop)\s+(a\s+)?(function|class|script|api|module|component|service)",
    "debug_request": r"(debug|fix|error|bug|issue|problem|not working|broken)",
    "analysis_request": r"(analyze|review|examine|investigate|assess|evaluate)",
    "complex_reasoning": r"(design|architect|architecture|system|trade-off|performance|scalability|security|optimization)",
    "multi_step": r"(step by step|first|then|next|after|finally|comprehensive|complete)",
    "research_request": r"(research|find|search|look up|investigate|explore)",
    "comparison": r"(compare|versus|vs|difference|similarities|pros and cons)",
}

# System prompts for each tier
SYSTEM_PROMPTS = {
    "fast": "Be concise. Answer in 1-2 sentences.",
    "standard": "Be thorough but efficient. Provide complete answers.",
    "deep": "Think step by step. Provide detailed analysis with reasoning.",
}


@dataclass
class ClassificationResult:
    """Result of query classification."""
    score: int
    tier: Literal["fast", "standard", "deep"]
    reasoning: str
    suggested_model: str
    system_prompt: str


def classify(query: str) -> ClassificationResult:
    """
    Classify a user query based on complexity and return routing information.
    
    Args:
        query: The user's input query
        
    Returns:
        ClassificationResult with score, tier, reasoning, model, and system prompt
    """
    if not query or not isinstance(query, str):
        return ClassificationResult(
            score=10,
            tier="fast",
            reasoning="Empty or invalid query, defaulting to fast tier",
            suggested_model="MiniMax-M2.1",
            system_prompt=SYSTEM_PROMPTS["fast"]
        )
    
    query_lower = query.lower().strip()
    score = 10  # Base score for any non-empty query
    
    # Check for patterns
    if re.search(PATTERNS["greeting"], query_lower):
        score -= 5
    
    if re.search(PATTERNS["simple_question"], query_lower):
        score -= 3
    
    if re.search(PATTERNS["gratitude"], query_lower):
        score -= 5
    
    # Add scores for complexity indicators
    reasons = []
    for indicator, points in COMPLEXITY_INDICATORS.items():
        if indicator in query_lower:
            score += points
            reasons.append(f"Contains '{indicator}' (+{points})")
    
    # Check patterns
    if re.search(PATTERNS["code_request"], query_lower):
        score += 15
        reasons.append("Code generation request")
    
    if re.search(PATTERNS["debug_request"], query_lower):
        score += 12
        reasons.append("Debug/fix request")
    
    if re.search(PATTERNS["analysis_request"], query_lower):
        score += 18
        reasons.append("Analysis/review request")
    
    if re.search(PATTERNS["complex_reasoning"], query_lower):
        score += 22
        reasons.append("Complex reasoning request")
    
    if re.search(PATTERNS["multi_step"], query_lower):
        score += 20
        reasons.append("Multi-step request")
    
    if re.search(PATTERNS["research_request"], query_lower):
        score += 18
        reasons.append("Research request")
    
    if re.search(PATTERNS["comparison"], query_lower):
        score += 15
        reasons.append("Comparison request")
    
    # Length-based adjustments
    word_count = len(query.split())
    if word_count < 5:
        score -= 5
    elif word_count > 100:
        score += 10
    elif word_count > 50:
        score += 5
    
    # Question marks suggest inquiry (lower complexity)
    question_count = query.count("?")
    if question_count > 0:
        score -= min(question_count * 2, 10)
    
    # Code blocks or technical syntax
    if "```" in query or "`" in query:
        score += 8
        reasons.append("Contains code/technical syntax")
    
    # URLs or references
    if "http" in query_lower or "www." in query_lower:
        score += 5
        reasons.append("Contains URL/reference")
    
    # Ensure score is within bounds
    score = max(1, min(100, score))
    
    # Determine tier
    if score < 30:
        tier = "fast"
        model = "MiniMax-M2.1"
    elif score <= 70:
        tier = "standard"
        model = "MiniMax-M2.1"
    else:
        tier = "deep"
        model = "MiniMax-M2.1-Deep"
    
    # Build reasoning
    if reasons:
        reasoning = f"Score {score}: " + "; ".join(reasons[:5])  # Top 5 reasons
    else:
        reasoning = f"Score {score}: General query classification"
    
    return ClassificationResult(
        score=score,
        tier=tier,
        reasoning=reasoning,
        suggested_model=model,
        system_prompt=SYSTEM_PROMPTS[tier]
    )


def route_query(query: str) -> dict:
    """
    Route a query based on its complexity score.
    
    Args:
        query: The user's input query
        
    Returns:
        Dictionary with routing information
    """
    result = classify(query)
    return {
        "query": query[:100] + "..." if len(query) > 100 else query,
        "score": result.score,
        "tier": result.tier,
        "model": result.suggested_model,
        "system_prompt": result.system_prompt,
        "reasoning": result.reasoning,
    }


# Alias for backward compatibility
get_classification = classify


if __name__ == "__main__":
    # Test the classifier with sample queries
    test_queries = [
        # Simple queries (1-30)
        "Hi, how are you?",
        "What is Python?",
        "Thanks for your help!",
        
        # Standard queries (30-70)
        "Write a Python function to calculate factorial",
        "Fix this bug in my JavaScript code",
        "Summarize this article",
        "Create a REST API endpoint",
        
        # Complex queries (70-100)
        "Design a scalable microservices architecture for an e-commerce platform with trade-offs analysis",
        "Analyze the performance bottlenecks in our distributed system and suggest optimizations",
        "Compare PostgreSQL vs MongoDB for a high-traffic application with detailed analysis",
    ]
    
    print("=" * 80)
    print("ADAPTIVE ROUTING CLASSIFIER - TEST RESULTS")
    print("=" * 80)
    
    for i, query in enumerate(test_queries, 1):
        result = classify(query)
        print(f"\n[Test Query {i}]")
        print(f"Query: {query}")
        print(f"Score: {result.score}/100")
        print(f"Tier:  {result.tier.upper()}")
        print(f"Model: {result.suggested_model}")
        print(f"Prompt: {result.system_prompt}")
        print(f"Reasoning: {result.reasoning}")
        print("-" * 80)
