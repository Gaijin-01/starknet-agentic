#!/usr/bin/env python3
"""
BotController — High-level operational controller for Clawdbot + EDITOR
Defines WHAT the bot does, WHEN, and HOW agents interact.

Based on bot.controller.js specification.
Includes comprehensive error handling with retry logic.
LLM integration via MiniMax API.
"""

import json
import logging
import time
import httpx
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime
from pathlib import Path

# LLM Configuration with Dual Key Failover
LLM_BASE_URL = "https://api.minimax.io/anthropic/v1/messages"
LLM_MODEL = "MiniMax-M2.1"

# Dual keys from Gateway config (2026-01-30)
LLM_KEYS = {
    "primary": "sk-cp-Y6dI0qnh9jWg_dY6wdNMoLyQyEeT8forPrE701R9dd35YG2liv2bvbEq1H4tEmD6JJk0tZh3b0pEW2UN1ECjlwXPowePAKuVoHReh6v_S4zQqrQvtvik8Zs",
    "secondary": "sk-api-3ktqRHdx04SqZxt1ViooHTwmqscojyphek6W9JyelPlJox3wghXs4EZMGmpcH2ZTl44MHPsqWA9n1nupo1h2NURq6mFygLeaILRrvSobqRb7np8YqGnVzNc"
}

# Current active key (for failover tracking)
_current_key = {"name": "primary", "consecutive_failures": 0}

# Configure logging
LOG_DIR = Path("/home/wner/clawd/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "bot_controller.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("BotController")


class Mode(Enum):
    AUTO = "auto"
    MANUAL = "manual"
    DRY_RUN = "dry_run"


class BotError(Exception):
    """Base exception for BotController errors."""
    def __init__(self, message: str, stage: str = None, recoverable: bool = True):
        super().__init__(message)
        self.message = message
        self.stage = stage
        self.recoverable = recoverable


class LLMError(BotError):
    """LLM API error."""
    def __init__(self, message: str, retry_after: int = None):
        super().__init__(message, stage="StylerAgent", recoverable=True)
        self.retry_after = retry_after


class ValidationError(BotError):
    """Input validation error."""
    def __init__(self, message: str, field: str = None):
        super().__init__(message, stage="IntakeAgent", recoverable=False)
        self.field = field


@dataclass
class AgentResult:
    """Result from an agent execution."""
    agent: str
    success: bool
    output: Dict
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    error: Optional[str] = None
    retry_count: int = 0


class BotController:
    """
    High-level operational controller for Clawdbot + EDITOR.
    
    Orchestrates agents through the editorial pipeline:
    IntakeAgent → ClassifierAgent → MetaControllerAgent → 
    StylerAgent → SafetyAgent → FormatterAgent
    
    Features:
    - Comprehensive error handling with retry logic
    - Graceful degradation on failures
    - Structured logging
    - Execution tracing
    """
    
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0  # seconds
    RETRY_BACKOFF = 2.0  # exponential backoff multiplier
    
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
    # INITIALIZATION
    # =============================
    
    def __init__(self, mode: Mode = Mode.AUTO, max_retries: int = None):
        """
        Initialize BotController.
        
        Args:
            mode: Execution mode (AUTO, MANUAL, DRY_RUN)
            max_retries: Maximum retry attempts for failed operations
        """
        self.mode = mode
        self.max_retries = max_retries or self.MAX_RETRIES
        self.log = []
        self.execution_trace = []
        self.stats = {
            "total_runs": 0,
            "successful": 0,
            "failed": 0,
            "retries": 0
        }
        logger.info(f"BotController initialized in {mode.value} mode")
    
    # =============================
    # ERROR HANDLING
    # =============================
    
    def _execute_with_retry(self, func, *args, **kwargs) -> AgentResult:
        """
        Execute function with retry logic.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            AgentResult with success status and output/error
        """
        agent_name = getattr(func, '__name__', 'unknown')
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                output = func(*args, **kwargs)
                return AgentResult(
                    agent=agent_name,
                    success=True,
                    output=output
                )
            except LLMError as e:
                last_error = e
                wait_time = self.RETRY_DELAY * (self.RETRY_BACKOFF ** attempt)
                logger.warning(f"LLM error in {agent_name}: {e.message}, retrying in {wait_time}s")
                time.sleep(wait_time)
            except (ValidationError, KeyError) as e:
                # Non-retryable errors
                logger.error(f"Non-recoverable error in {agent_name}: {e}")
                return AgentResult(
                    agent=agent_name,
                    success=False,
                    output={},
                    error=str(e)
                )
            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error in {agent_name}: {e}", exc_info=True)
                if attempt < self.max_retries - 1:
                    wait_time = self.RETRY_DELAY * (self.RETRY_BACKOFF ** attempt)
                    logger.info(f"Retrying {agent_name} in {wait_time}s (attempt {attempt + 2})")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Max retries exceeded for {agent_name}")
        
        # All retries failed
        self.stats["retries"] += 1
        return AgentResult(
            agent=agent_name,
            success=False,
            output={},
            error=str(last_error),
            retry_count=self.max_retries
        )
    
    def _safe_get(self, data: Dict, key: str, default: Any = None) -> Any:
        """Safely get a value from a dictionary."""
        try:
            return data.get(key, default)
        except (AttributeError, TypeError):
            return default
    
    # =============================
    # EXECUTION
    # =============================
    
    def execute(self, text: str, user_overrides: Dict = None, 
               platform: str = "twitter", dry_run: bool = False) -> Dict:
        """
        Execute full editorial pipeline with error handling.
        
        Args:
            text: Input text
            user_overrides: Preset or custom params from user
            platform: Target platform (twitter, thread, markdown)
            dry_run: Only analyze, don't generate
        
        Returns:
            Full execution trace + output
        """
        self.stats["total_runs"] += 1
        self.execution_trace = []
        self.log = []
        
        # Input validation
        if not text:
            error_msg = "Empty text provided"
            logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg,
                "stage": "validation",
                "trace": self.execution_trace,
                "log": self.log
            }
        
        self.log.append({
            "event": "pipeline_start", 
            "text": text[:50] + "..." if len(text) > 50 else text, 
            "mode": self.mode.value,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"Starting pipeline with text: {text[:50]}...")
        
        # Track results
        results = {}
        
        try:
            # === Stage 1: IntakeAgent ===
            result1 = self._execute_with_retry(
                self._run_intake_agent, 
                text
            )
            results["IntakeAgent"] = result1
            self.execution_trace.append({
                "agent": result1.agent, 
                "success": result1.success, 
                "output": result1.output,
                "error": result1.error,
                "timestamp": result1.timestamp
            })
            
            if not result1.success:
                raise BotError(f"IntakeAgent failed: {result1.error}", stage="IntakeAgent")
            
            normalized_text = self._safe_get(result1.output, "normalized_text", "")
            
            # === Stage 2: ClassifierAgent ===
            result2 = self._execute_with_retry(
                self._run_classifier_agent, 
                normalized_text
            )
            results["ClassifierAgent"] = result2
            self.execution_trace.append({
                "agent": result2.agent, 
                "success": result2.success, 
                "output": result2.output,
                "error": result2.error,
                "timestamp": result2.timestamp
            })
            
            if not result2.success:
                raise BotError(f"ClassifierAgent failed: {result2.error}", stage="ClassifierAgent")
            
            # Check confidence
            confidence = self._safe_get(result2.output, "confidence", 1.0)
            if confidence < self.FAILURE_HANDLING["lowConfidence"]["threshold"]:
                self.log.append({
                    "event": "low_confidence", 
                    "confidence": confidence,
                    "action": "fallback_to_ct"
                })
                user_overrides = user_overrides or {"preset": "ct"}
                logger.info(f"Low confidence ({confidence}), falling back to CT preset")
            
            topics = self._safe_get(result2.output, "topics", ["crypto"])
            intent = self._safe_get(result2.output, "intent", "engage")
            
            # === Stage 3: MetaControllerAgent ===
            result3 = self._execute_with_retry(
                self._run_meta_controller_agent,
                topics,
                intent,
                user_overrides
            )
            results["MetaControllerAgent"] = result3
            self.execution_trace.append({
                "agent": result3.agent, 
                "success": result3.success, 
                "output": result3.output,
                "error": result3.error,
                "timestamp": result3.timestamp
            })
            
            if not result3.success:
                raise BotError(f"MetaControllerAgent failed: {result3.error}", stage="MetaControllerAgent")
            
            style_params = self._safe_get(result3.output, "style_params", {})
            
            # === Conditional: dry_run ===
            if dry_run or self.mode == Mode.DRY_RUN:
                self.log.append({"event": "dry_run_complete"})
                return {
                    "status": "dry_run",
                    "analysis": result3.output,
                    "trace": self.execution_trace,
                    "log": self.log
                }
            
            # === Stage 4: StylerAgent ===
            result4 = self._execute_with_retry(
                self._run_styler_agent,
                normalized_text,
                style_params
            )
            results["StylerAgent"] = result4
            self.execution_trace.append({
                "agent": result4.agent, 
                "success": result4.success, 
                "output": result4.output,
                "error": result4.error,
                "timestamp": result4.timestamp
            })
            
            if not result4.success:
                raise LLMError(f"StylerAgent failed: {result4.error}")
            
            styled_text = self._safe_get(result4.output, "styled_text", normalized_text)
            
            # === Stage 5: SafetyAgent ===
            result5 = self._run_safety_agent(styled_text)
            results["SafetyAgent"] = result5
            self.execution_trace.append({
                "agent": result5.agent, 
                "success": result5.success, 
                "output": result5.output,
                "error": result5.error,
                "timestamp": result5.timestamp
            })
            
            # Conditional: safety check
            passed = self._safe_get(result5.output, "passed", True)
            violations = self._safe_get(result5.output, "violations", [])
            
            if not passed:
                self.log.append({
                    "event": "safety_failed", 
                    "violations": violations
                })
                logger.warning(f"Safety check failed: {violations}")
                return {
                    "status": "blocked",
                    "reason": "safety_violation",
                    "violations": violations,
                    "trace": self.execution_trace,
                    "log": self.log
                }
            
            safe_text = self._safe_get(result5.output, "safe_text", styled_text)
            
            # === Stage 6: FormatterAgent ===
            result6 = self._run_formatter_agent(safe_text, platform)
            results["FormatterAgent"] = result6
            self.execution_trace.append({
                "agent": result6.agent, 
                "success": result6.success, 
                "output": result6.output,
                "error": result6.error,
                "timestamp": result6.timestamp
            })
            
            final_output = self._safe_get(result6.output, "final_output", safe_text)
            
            self.log.append({
                "event": "pipeline_complete", 
                "output_length": len(final_output),
                "timestamp": datetime.now().isoformat()
            })
            
            self.stats["successful"] += 1
            logger.info(f"Pipeline completed successfully, output length: {len(final_output)}")
            
            return {
                "status": "success",
                "output": final_output,
                "analysis": {
                    "topics": topics,
                    "intent": intent,
                    "style_params": style_params,
                    "violations": violations
                },
                "trace": self.execution_trace,
                "log": self.log
            }
            
        except LLMError as e:
            self.stats["failed"] += 1
            logger.error(f"LLM error: {e.message}")
            return {
                "status": "error",
                "error": e.message,
                "stage": e.stage,
                "recoverable": e.recoverable,
                "trace": self.execution_trace,
                "log": self.log
            }
        except BotError as e:
            self.stats["failed"] += 1
            logger.error(f"Bot error at {e.stage}: {e.message}")
            return {
                "status": "error",
                "error": e.message,
                "stage": e.stage,
                "recoverable": e.recoverable,
                "trace": self.execution_trace,
                "log": self.log
            }
        except Exception as e:
            self.stats["failed"] += 1
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "stage": "unknown",
                "trace": self.execution_trace,
                "log": self.log
            }
    
    # =============================
    # AGENT IMPLEMENTATIONS
    # =============================
    
    def _run_intake_agent(self, text: str) -> Dict:
        """Normalize input text and metadata."""
        # Basic cleaning
        normalized = text.strip().replace('\n\n\n', '\n\n')
        
        # Simple language detection
        hebrew_chars = sum(1 for c in text if '\u0590' <= c <= '\u05ff')
        language = "he" if hebrew_chars > 3 else "en"
        
        return {
            "normalized_text": normalized,
            "language": language,
            "metadata": {"timestamp": datetime.now().isoformat()}
        }
    
    def _run_classifier_agent(self, text: str) -> Dict:
        """Detect topic(s) and user intent."""
        if not text:
            return {"topics": ["crypto"], "intent": "engage", "confidence": 0.5}
        
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
        
        return {
            "topics": topics,
            "intent": intent,
            "confidence": confidence
        }
    
    def _run_meta_controller_agent(self, topics: List[str], intent: str,
                                   user_overrides: Dict = None) -> Dict:
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
                    return {
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
        
        return {
            "editorial_intent": intent,
            "style_params": params,
            "decision_trace": ["default_ct", f"intent:{intent}"]
        }
    
    def _call_llm(self, prompt: str, temperature: float = 0.7) -> str:
        """Call MiniMax LLM API."""
        try:
            headers = {
                "Authorization": f"Bearer {LLM_API_KEY}",
                "Content-Type": "application/json",
                "X-API-Version": "2023-01-01"
            }
            payload = {
                "model": LLM_MODEL,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500,
                "temperature": temperature
            }
            
            with httpx.post(LLM_BASE_URL, headers=headers, json=payload, timeout=30.0) as resp:
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("content", data.get("completion", ""))
                else:
                    raise LLMError(f"API error: {resp.status_code} - {resp.text[:100]}")
                    
        except httpx.HTTPError as e:
            raise LLMError(f"HTTP error: {str(e)}")
    
    def _run_styler_agent(self, text: str, params: Dict) -> Dict:
        """Execute text transformation via LLM (MiniMax-2.1)."""
        
        frag = params.get("fragmentation", 50)
        irony = params.get("irony", 50)
        agg = params.get("aggression", 50)
        meme = params.get("meme_density", 50)
        myth = params.get("myth_layer", 50)
        
        # Build style description
        style_desc = []
        if frag > 70:
            style_desc.append("fragmented, with line breaks")
        elif frag > 50:
            style_desc.append("slightly fragmented")
        
        if irony > 60:
            style_desc.append("ironic and self-aware")
        elif irony > 40:
            style_desc.append("lightly ironic")
        
        if agg > 70:
            style_desc.append("aggressive and confrontational")
        elif agg > 50:
            style_desc.append("assertive")
        else:
            style_desc.append("calm and measured")
        
        if meme > 60:
            style_desc.append("meme-heavy with crypto slang")
        elif meme > 40:
            style_desc.append("occasionally meme-flavored")
        
        if myth > 60:
            style_desc.append("prophetic and mythic")
        elif myth > 40:
            style_desc.append("narrative-driven")
        
        style_str = ", ".join(style_desc) if style_desc else "neutral"
        
        prompt = f"""Transform this text in CT (Crypto Twitter) style:

Original: "{text}"

Style requirements: {style_str}
Keep the same meaning but adapt tone and formatting.

Return ONLY the transformed text, no explanations."""

        try:
            styled = self._call_llm(prompt)
            # Fallback to original if LLM returns empty
            if not styled or len(styled) < 5:
                styled = text
            logger.info(f"LLM styled text: {styled[:50]}...")
        except LLMError as e:
            logger.warning(f"LLM failed, using fallback: {e}")
            # Fallback to original with minimal transformations
            styled = text
            if meme > 40:
                styled = f"{styled} 🔥"
        
        return {"styled_text": styled}
    
    def _run_safety_agent(self, text: str) -> Dict:
        """Enforce safety anchors and anti-cringe rules."""
        violations = []
        
        # Check for absolute claims
        absolutes = ["i know the truth", "i am certain", "this is absolute", "no doubt"]
        for abs in absolutes:
            if abs in text.lower():
                violations.append(f"absolute_claim:{abs}")
        
        # Add hyperbole marker if needed
        result = text
        if len(text) > 50 and "🔥" not in text:
            if any(w in text.lower() for w in ["will", "always", "never", "forever"]):
                result = f"{result} 🔥"
                violations.append("Added hyperbole marker")
        
        # Count actual violations (not markers)
        actual_violations = [v for v in violations if not v.startswith("Added")]
        passed = len(actual_violations) == 0
        
        return {
            "safe_text": result,
            "violations": violations,
            "passed": passed
        }
    
    def _run_formatter_agent(self, text: str, platform: str) -> Dict:
        """Adapt output to target platform."""
        result = text
        
        if platform == "twitter":
            # Short, ensure not too long
            if len(result) > 280:
                result = result[:277] + "..."
        elif platform == "thread":
            # Thread formatting (split if needed)
            pass  # Thread logic would go here
        elif platform == "markdown":
            # Markdown formatting
            pass  # Markdown logic would go here
        
        return {"final_output": result}
    
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
    
    def get_stats(self) -> Dict:
        """Return execution statistics."""
        return self.stats


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="BotController - Editorial Pipeline Orchestrator")
    parser.add_argument("--text", required=True, help="Input text")
    parser.add_argument("--preset", help="Style preset (normal, ct, shizo, v-myaso)")
    parser.add_argument("--platform", default="twitter", help="Target platform")
    parser.add_argument("--dry-run", action="store_true", help="Analyze only")
    parser.add_argument("--agents", action="store_true", help="List agents")
    parser.add_argument("--rules", action="store_true", help="Show hard rules")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    
    args = parser.parse_args()
    
    controller = BotController()
    
    if args.agents:
        print(json.dumps(controller.get_agents(), indent=2))
        return
    
    if args.rules:
        print("\n".join(controller.get_hard_rules()))
        return
    
    if args.stats:
        print(json.dumps(controller.get_stats(), indent=2))
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
