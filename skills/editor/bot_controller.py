#!/usr/bin/env python3
"""
BotController — High-level operational controller for Clawdbot + EDITOR
Defines WHAT the bot does, WHEN, and HOW agents interact.

Based on bot.controller.js specification.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class Mode(Enum):
    AUTO = "auto"
    MANUAL = "manual"
    DRY_RUN = "dry_run"


@dataclass
class AgentResult:
    agent: str
    success: bool
    output: Dict
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class BotController:
    """
    High-level operational controller for Clawdbot + EDITOR.
    
    Orchestrates agents through the editorial pipeline:
    IntakeAgent → ClassifierAgent → MetaControllerAgent → 
    StylerAgent → SafetyAgent → FormatterAgent
    """
    
    def __init__(self, mode: Mode = Mode.AUTO):
        self.mode = mode
        self.log = []
        self.execution_trace = []
    
    # =============================
    # AGENT DEFINITIONS
    # =============================
    
    AGENTS = {
        "IntakeAgent": {
            "role": "Normalize input text and metadata",
            "actions": ["clean_text", "detect_language", "extract_metadata"],
            "output_fields": ["normalized_text", "language", "metadata"]
        },
        "ClassifierAgent": {
            "role": "Detect topic(s) and user intent",
            "actions": ["topic_classification", "intent_detection", "confidence_scoring"],
            "output_fields": ["topics", "intent", "confidence"]
        },
        "MetaControllerAgent": {
            "role": "Select editorial intent and style parameters",
            "actions": ["match_rules", "score_editorial_intents", "select_params"],
            "output_fields": ["editorial_intent", "style_params", "decision_trace"]
        },
        "StylerAgent": {
            "role": "Execute text transformation via LLM (MiniMax-2.1)",
            "actions": ["rewrite", "expand", "compress", "fragment"],
            "constraints": ["apply_params_exactly", "no_reasoning_explanation"],
            "output_fields": ["styled_text"]
        },
        "SafetyAgent": {
            "role": "Enforce safety anchors and anti-cringe rules",
            "actions": ["detect_violations", "soften_or_block"],
            "output_fields": ["safe_text", "violations", "passed"]
        },
        "FormatterAgent": {
            "role": "Adapt output to target platform",
            "actions": ["format_twitter", "format_thread", "format_markdown"],
            "output_fields": ["final_output"]
        }
    }
    
    # =============================
    # EXECUTION PIPELINE
    # =============================
    
    DEFAULT_PIPELINE = [
        "IntakeAgent",
        "ClassifierAgent",
        "MetaControllerAgent",
        "StylerAgent",
        "SafetyAgent",
        "FormatterAgent"
    ]
    
    CONDITIONAL_BRANCHES = [
        {"if": {"safetyPassed": False}, "then": "block_output"},
        {"if": {"mode": "dry_run"}, "then": "skip_generation"}
    ]
    
    # =============================
    # FAILURE MODES
    # =============================
    
    FAILURE_HANDLING = {
        "lowConfidence": {"threshold": 0.4, "action": "fallback_to_ct"},
        "styleConflict": {"action": "reduce_fragmentation"},
        "tokenOverflow": {"action": "compress_then_retry"}
    }
    
    # =============================
    # HARD RULES (NON-NEGOTIABLE)
    # =============================
    
    HARD_RULES = [
        "User override always wins",
        "SafetyAgent cannot be bypassed",
        "MiniMax never decides style",
        "No external actions without permission"
    ]
    
    # =============================
    # EXECUTION
    # =============================
    
    def execute(self, text: str, user_overrides: Dict = None, 
               platform: str = "twitter", dry_run: bool = False) -> Dict:
        """
        Execute full editorial pipeline.
        
        Args:
            text: Input text
            user_overrides: Preset or custom params from user
            platform: Target platform (twitter, thread, markdown)
            dry_run: Only analyze, don't generate
        
        Returns:
            Full execution trace + output
        """
        self.execution_trace = []
        self.log.append({"event": "pipeline_start", "text": text[:50], "mode": self.mode.value})
        
        # Track results
        results = {}
        
        # === Stage 1: IntakeAgent ===
        result1 = self._run_intake_agent(text)
        results["IntakeAgent"] = result1
        self.execution_trace.append({"agent": result1.agent, "success": result1.success, "output": result1.output, "timestamp": result1.timestamp})
        
        # === Stage 2: ClassifierAgent ===
        result2 = self._run_classifier_agent(result1.output["normalized_text"])
        results["ClassifierAgent"] = result2
        self.execution_trace.append({"agent": result2.agent, "success": result2.success, "output": result2.output, "timestamp": result2.timestamp})
        
        # Check confidence
        if result2.output.get("confidence", 1.0) < self.FAILURE_HANDLING["lowConfidence"]["threshold"]:
            self.log.append({"event": "low_confidence", "action": "fallback_to_ct"})
            user_overrides = user_overrides or {"preset": "ct"}
        
        # === Stage 3: MetaControllerAgent ===
        result3 = self._run_meta_controller_agent(
            result2.output["topics"],
            result2.output["intent"],
            user_overrides
        )
        results["MetaControllerAgent"] = result3
        self.execution_trace.append({"agent": result3.agent, "success": result3.success, "output": result3.output, "timestamp": result3.timestamp})
        
        # === Conditional: dry_run ===
        if dry_run or self.mode == Mode.DRY_RUN:
            return {
                "status": "dry_run",
                "analysis": result3.output,
                "trace": self.execution_trace,
                "log": self.log
            }
        
        # === Stage 4: StylerAgent ===
        result4 = self._run_styler_agent(
            result1.output["normalized_text"],
            result3.output["style_params"]
        )
        results["StylerAgent"] = result4
        self.execution_trace.append({"agent": result4.agent, "success": result4.success, "output": result4.output, "timestamp": result4.timestamp})
        
        # === Stage 5: SafetyAgent ===
        result5 = self._run_safety_agent(result4.output["styled_text"])
        results["SafetyAgent"] = result5
        self.execution_trace.append({"agent": result5.agent, "success": result5.success, "output": result5.output, "timestamp": result5.timestamp})
        
        # Conditional: safety check
        if not result5.output["passed"]:
            self.log.append({"event": "safety_failed", "violations": result5.output["violations"]})
            return {
                "status": "blocked",
                "reason": "safety_violation",
                "violations": result5.output["violations"],
                "trace": self.execution_trace,
                "log": self.log
            }
        
        # === Stage 6: FormatterAgent ===
        result6 = self._run_formatter_agent(
            result5.output["safe_text"],
            platform
        )
        results["FormatterAgent"] = result6
        self.execution_trace.append({"agent": result6.agent, "success": result6.success, "output": result6.output, "timestamp": result6.timestamp})
        
        self.log.append({"event": "pipeline_complete", "output_length": len(result6.output["final_output"])})
        
        return {
            "status": "success",
            "output": result6.output["final_output"],
            "analysis": {
                "topics": result2.output["topics"],
                "intent": result2.output["intent"],
                "style_params": result3.output["style_params"],
                "violations": result5.output["violations"]
            },
            "trace": self.execution_trace,
            "log": self.log
        }
    
    # =============================
    # AGENT IMPLEMENTATIONS
    # =============================
    
    def _run_intake_agent(self, text: str) -> AgentResult:
        """Normalize input text and metadata."""
        # Basic cleaning
        normalized = text.strip().replace('\n\n\n', '\n\n')
        
        # Simple language detection
        hebrew_chars = sum(1 for c in text if '\u0590' <= c <= '\u05ff')
        language = "he" if hebrew_chars > 3 else "en"
        
        return AgentResult(
            agent="IntakeAgent",
            success=True,
            output={
                "normalized_text": normalized,
                "language": language,
                "metadata": {"timestamp": datetime.now().isoformat()}
            }
        )
    
    def _run_classifier_agent(self, text: str) -> AgentResult:
        """Detect topic(s) and user intent."""
        text_lower = text.lower()
        
        # Topic detection
        topics = []
        topic_keywords = {
            "crypto": ["starknet", "zk", "crypto", "defi", "l2", "token", "rollup"],
            "geopolitics": ["war", "government", "iran", "israel", "usa", "china"],
            "ct-drama": ["twitter", "x", "ct", "drama", "beef"],
            "philosophy": ["meaning", "purpose", "reality", "truth", "system"],
            "personal": ["gm", "shalom", "tired", "feeling"],
            "meme": ["lmao", "meme", "funny", "joke", "lfg"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(kw in text_lower for kw in keywords):
                topics.append(topic)
        
        if not topics:
            topics = ["crypto"]  # Default
        
        # Intent detection
        intents = {
            "engage": ["gm", "lfg", "watch", "everyone"],
            "attack": ["suck", "wrong", "you're not", "💀"],
            "signal": ["know", "understand", "obviously"],
            "myth-building": ["future", "ready", "they don't", "we will"],
            "process": ["thinking", "wonder", "question", "maybe"]
        }
        
        scores = {}
        for intent, patterns in intents.items():
            scores[intent] = sum(1 for p in patterns if p in text_lower)
        
        best_intent = max(scores.items(), key=lambda x: x[1])
        intent = best_intent[0] if best_intent[1] > 0 else "engage"
        confidence = min(best_intent[1] / 3, 1.0)
        
        return AgentResult(
            agent="ClassifierAgent",
            success=True,
            output={
                "topics": topics,
                "intent": intent,
                "confidence": confidence
            }
        )
    
    def _run_meta_controller_agent(self, topics: List[str], intent: str,
                                   user_overrides: Dict = None) -> AgentResult:
        """Select editorial intent and style parameters."""
        
        # Check user overrides first (HARD RULE: User override always wins)
        if user_overrides:
            if "preset" in user_overrides:
                presets = {
                    "normal": (30, 30, 20, 10, 5),
                    "ct": (55, 40, 45, 30, 25),
                    "shizo": (70, 60, 50, 45, 40),
                    "v-myaso": (85, 70, 70, 70, 60)
                }
                if user_overrides["preset"] in presets:
                    frag, iron, agg, meme, myth = presets[user_overrides["preset"]]
                    return AgentResult(
                        agent="MetaControllerAgent",
                        success=True,
                        output={
                            "editorial_intent": f"preset:{user_overrides['preset']}",
                            "style_params": {
                                "fragmentation": frag,
                                "irony": iron,
                                "aggression": agg,
                                "meme_density": meme,
                                "myth_layer": myth
                            },
                            "decision_trace": ["user_override", user_overrides["preset"]]
                        }
                    )
        
        # Default: CT behavior
        params = {
            "fragmentation": 55,
            "irony": 40,
            "aggression": 45,
            "meme_density": 30,
            "myth_layer": 25
        }
        
        # Adjust for intent
        if intent == "attack":
            params["aggression"] = 80
        elif intent == "myth-building":
            params["myth_layer"] = 70
            params["fragmentation"] = 60
        
        return AgentResult(
            agent="MetaControllerAgent",
            success=True,
            output={
                "editorial_intent": intent,
                "style_params": params,
                "decision_trace": ["default_ct", f"intent:{intent}"]
            }
        )
    
    def _run_styler_agent(self, text: str, params: Dict) -> AgentResult:
        """Execute text transformation via LLM (MiniMax-2.1)."""
        # In real implementation, this would call the LLM with explicit params
        # For now, return placeholder
        
        # Apply fragmentation
        styled = text
        if params.get("fragmentation", 0) > 60:
            styled = styled.replace(" ", "\n")
        
        # Apply meme markers
        if params.get("meme_density", 0) > 40:
            if "gm" in styled.lower() and "🐺" not in styled:
                styled = f"{styled} 🐺"
            if params.get("meme_density", 0) > 60:
                styled = f"{styled} 🔥"
        
        return AgentResult(
            agent="StylerAgent",
            success=True,
            output={"styled_text": styled}
        )
    
    def _run_safety_agent(self, text: str) -> AgentResult:
        """Enforce safety anchors and anti-cringe rules."""
        violations = []
        
        # Check for absolute claims
        absolutes = ["i know the truth", "i am certain", "this is absolute", "no doubt"]
        for abs in absolutes:
            if abs in text.lower():
                violations.append(abs)
        
        # Add hyperbole marker if needed
        result = text
        if len(text) > 50 and "🔥" not in text:
            if any(w in text.lower() for w in ["will", "always", "never", "forever"]):
                result = f"{result} 🔥"
                violations.append("Added hyperbole marker")
        
        passed = len([v for v in violations if v not in ["Added hyperbole marker"]]) == 0
        
        return AgentResult(
            agent="SafetyAgent",
            success=True,
            output={
                "safe_text": result,
                "violations": violations,
                "passed": passed
            }
        )
    
    def _run_formatter_agent(self, text: str, platform: str) -> AgentResult:
        """Adapt output to target platform."""
        if platform == "twitter":
            # Short, ensure not too long
            if len(text) > 280:
                text = text[:277] + "..."
        
        return AgentResult(
            agent="FormatterAgent",
            success=True,
            output={"final_output": text}
        )
    
    # =============================
    # ACCESSOR METHODS
    # =============================
    
    def get_agents(self) -> Dict:
        """Return agent definitions."""
        return self.AGENTS
    
    def get_hard_rules(self) -> List[str]:
        """Return non-negotiable rules."""
        return self.HARD_RULES
    
    def get_pipeline(self) -> List[str]:
        """Return execution pipeline."""
        return self.DEFAULT_PIPELINE
    
    def get_log(self) -> List[Dict]:
        """Return execution log."""
        return self.log


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="BotController - Editorial Pipeline Orchestrator")
    parser.add_argument("--text", required=True, help="Input text")
    parser.add_argument("--preset", help="Style preset (normal, ct, shizo, v-myaso)")
    parser.add_argument("--platform", default="twitter", help="Target platform")
    parser.add_argument("--dry-run", action="store_true", help="Analyze only")
    parser.add_argument("--agents", action="store_true", help="List agents")
    parser.add_argument("--rules", action="store_true", help="Show hard rules")
    
    args = parser.parse_args()
    
    controller = BotController()
    
    if args.agents:
        print(json.dumps(controller.get_agents(), indent=2))
        return
    
    if args.rules:
        print("\n".join(controller.get_hard_rules()))
        return
    
    user_overrides = {"preset": args.preset} if args.preset else None
    result = controller.execute(
        text=args.text,
        user_overrides=user_overrides,
        platform=args.platform,
        dry_run=args.dry_run
    )
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
