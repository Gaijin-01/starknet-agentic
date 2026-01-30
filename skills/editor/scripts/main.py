#!/usr/bin/env python3
"""
EDITOR — Autonomous Text Style Engine
Meta-controller for autonomous text processing.

Pipeline:
1. Input Intake → 2. Topic+Intent Classifier → 3. MetaController →
4. Styler Engine → 5. Safety & Anchors → 6. Output Formatter

Style presets: normal, ct, shizo, v-myaso, attack, meme, sefirot
Dual-key failover for LLM calls (2026-01-30)
"""

import json
import re
import argparse
import httpx
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime

# LLM Configuration with Dual Key Failover
LLM_BASE_URL = "https://api.minimax.io/anthropic/v1/messages"
LLM_MODEL = "MiniMax-M2.1"

# Dual keys from Gateway config
LLM_KEYS = {
    "primary": "sk-cp-Y6dI0qnh9jWg_dY6wdNMoLyQyEeT8forPrE701R9dd35YG2liv2bvbEq1H4tEmD6JJk0tZh3b0pEW2UN1ECjlwXPowePAKuVoHReh6v_S4zQqrQvtvik8Zs",
    "secondary": "sk-api-3ktqRHdx04SqZxt1ViooHTwmqscojyphek6W9JyelPlJox3wghXs4EZMGmpcH2ZTl44MHPsqWA9n1nupo1h2NURq6mFygLeaILRrvSobqRb7np8YqGnVzNc"
}

# Track active key for failover
_active_key = {"name": "primary", "failures": 0}


class Topic(Enum):
    CRYPTO = "crypto"
    GEOPOLITICS = "geopolitics"
    CT_DRAMA = "ct-drama"
    PHILOSOPHY = "philosophy"
    PERSONAL = "personal"
    MEME = "meme"


class Intent(Enum):
    ENGAGE = "engage"
    ATTACK = "attack"
    SIGNAL = "signal"
    MYTH_BUILDING = "myth-building"
    PROCESS = "process"


@dataclass
class StyleParams:
    """Style parameters (0-100 scale)."""
    fragmentation: int = 50
    irony: int = 50
    aggression: int = 50
    meme_density: int = 50
    myth_layer: int = 50
    
    def to_dict(self) -> Dict:
        return {
            "fragmentation": self.fragmentation,
            "irony": self.irony,
            "aggression": self.aggression,
            "meme_density": self.meme_density,
            "myth_layer": self.myth_layer
        }


@dataclass
class PipelineResult:
    """Result from full pipeline execution."""
    input_text: str
    topics: List[str]
    intent: str
    style_params: Dict
    styled_text: str
    safety_result: Dict
    output_text: str
    explanations: List[str] = field(default_factory=list)


PRESETS = {
    "normal": StyleParams(30, 30, 20, 10, 5),
    "ct": StyleParams(55, 40, 45, 30, 25),
    "shizo": StyleParams(70, 60, 50, 45, 40),
    "v-myaso": StyleParams(85, 70, 70, 70, 60),
    "attack": StyleParams(50, 50, 80, 40, 30),
    "meme": StyleParams(60, 40, 30, 90, 20),
    "sefirot": StyleParams(45, 50, 15, 25, 40),  # Minimal, confident, supportive (low aggression for ecosystem)
}


class Editor:
    """EDITOR - Meta-controller for autonomous text processing."""
    
    # Topic keywords
    TOPIC_KEYWORDS = {
        Topic.CRYPTO: ["starknet", "zk", "crypto", "defi", "l2", "token", "rollup", "eth", "btc", "strk"],
        Topic.GEOPOLITICS: ["war", "government", "state", "iran", "israel", "usa", "china", "trump"],
        Topic.CT_DRAMA: ["twitter", "x", "ct", "crypto twitter", "drama", "beef", "reply"],
        Topic.PHILOSOPHY: ["meaning", "purpose", "reality", "truth", "system", "meta", "think"],
        Topic.PERSONAL: ["tired", "gm", "shalom", "feeling", "day", "sleep", "family"],
        Topic.MEME: ["lmao", "rofl", "funny", "joke", "meme", "schizodio", "lobster", "lfg"],
    }
    
    INTENT_PATTERNS = {
        Intent.ENGAGE: ["explode", "viral", "everyone", "watch", "listen", "gm", "lfg"],
        Intent.ATTACK: ["suck", "stupid", "wrong", "actually", "you're not", "imagine", "💀"],
        Intent.SIGNAL: ["know", "understand", "obviously", "clearly", "as i said"],
        Intent.MYTH_BUILDING: ["future", "ready", "they don't", "we will", "history", "coming"],
        Intent.PROCESS: ["thinking", "wonder", "question", "not sure", "trying", "maybe"],
    }
    
    SAFETY_VIOLATIONS = [
        r"i know the truth",
        r"i am certain",
        r"this is absolute",
        r"no doubt",
        r"definitely",
    ]
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path
    
    # ============ STAGE 1: INPUT INTAKE ============
    def stage1_intake(self, text: str, metadata: Dict = None) -> str:
        """Normalize basic formatting."""
        if not text:
            return ""
        
        # Basic normalization
        result = text.strip()
        result = re.sub(r'\s+', ' ', result)  # Multiple spaces to single
        result = re.sub(r'\n{3,}', '\n\n', result)  # Max 2 newlines
        
        return result
    
    # ============ STAGE 2: TOPIC + INTENT CLASSIFIER ============
    def stage2_classify(self, text: str) -> tuple:
        """Multi-label topic detection + intent hierarchy."""
        text_lower = text.lower()
        
        # Detect topics
        topics = []
        for topic, keywords in self.TOPIC_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                topics.append(topic.value)
        
        if not topics:
            topics = [Topic.CRYPTO.value]  # Default
        
        # Detect intent
        scores = {}
        for intent, patterns in self.INTENT_PATTERNS.items():
            score = sum(1 for p in patterns if p in text_lower)
            scores[intent] = score
        
        # Best intent
        best_intent = max(scores.items(), key=lambda x: x[1])
        intent = best_intent[0].value if best_intent[1] > 0 else Intent.ENGAGE.value
        
        return topics, intent
    
    # ============ STAGE 3: METACONTROLLER ============
    def stage3_meta_controller(self, topics: List[str], intent: str, 
                               preset: str = None, custom_params: Dict = None) -> StyleParams:
        """Map topic + intent → style parameters."""
        
        # User override
        if preset and preset in PRESETS:
            return PRESETS[preset]
        
        if custom_params:
            return StyleParams(
                fragmentation=custom_params.get("fragmentation", 50),
                irony=custom_params.get("irony", 50),
                aggression=custom_params.get("aggression", 50),
                meme_density=custom_params.get("meme_density", 50),
                myth_layer=custom_params.get("myth_layer", 50),
            )
        
        # Auto-detect based on topic + intent
        # Default CT behavior
        params = StyleParams(50, 50, 30, 40, 30)
        
        if "crypto" in topics or "ct-drama" in topics:
            params = StyleParams(55, 40, 45, 30, 25)  # CT preset
        
        if intent == Intent.ATTACK.value:
            params.aggression = 80
            params.irony = 60
        elif intent == Intent.MYTH_BUILDING.value:
            params.myth_layer = 70
            params.fragmentation = 60
        elif intent == Intent.PROCESS.value:
            params.fragmentation = 20
            params.myth_layer = 30
        
        return params
    
    def explain_params(self, topics: List[str], intent: str, params: StyleParams) -> List[str]:
        """Explain why certain params were chosen."""
        explanations = []
        
        if "crypto" in topics or "ct-drama" in topics:
            explanations.append("CT/Crypto topic detected → CT preset baseline")
        
        if intent == Intent.ATTACK.value:
            explanations.append(f"Attack intent → aggression={params.aggression}")
        
        if intent == Intent.MYTH_BUILDING.value:
            explanations.append(f"Myth-building intent → myth_layer={params.myth_layer}")
        
        if params.fragmentation > 60:
            explanations.append(f"High fragmentation ({params.fragmentation}) for rhythm")
        
        if params.meme_density > 60:
            explanations.append(f"High meme_density ({params.meme_density}) for engagement")
        
        return explanations
    
    # ============ LLM CLIENT WITH DUAL KEY FAILOVER ============
    def _call_llm(self, prompt: str, max_tokens: int = 300) -> Optional[str]:
        """
        Call LLM with dual key failover.
        Tries primary key first, falls back to secondary on failure.
        """
        global _active_key
        
        for attempt in range(2):
            key_name = _active_key["name"]
            api_key = LLM_KEYS[key_name]
            
            try:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": LLM_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                }
                
                with httpx.post(LLM_BASE_URL, headers=headers, json=payload, timeout=30.0) as resp:
                    if resp.status_code == 200:
                        data = resp.json()
                        content = data.get("content") or data.get("completion", "")
                        if content:
                            # Success - reset failure count
                            _active_key["failures"] = 0
                            return content
            
            except Exception as e:
                pass
            
            # Key failed - switch to other key
            _active_key["name"] = "secondary" if key_name == "primary" else "primary"
            _active_key["failures"] += 1
        
        return None
    
    # ============ STAGE 4: STYLER ENGINE ============
    def stage4_styler(self, text: str, params: StyleParams) -> str:
        """
        Transform text using rule-based + LLM-assisted style params.
        Uses LLM for significant transformations (schizo level > 50).
        """
        result = text
        
        # For low transformation levels, use simple rules
        transformation_level = (
            (params.fragmentation - 50) + 
            (params.irony - 50) + 
            (params.aggression - 50) + 
            (params.meme_density - 50) + 
            (params.myth_layer - 50)
        ) / 5
        
        # Use LLM for significant transformations
        if transformation_level > 20:
            style_desc = []
            if params.fragmentation > 60:
                style_desc.append("fragmented with short phrases and line breaks")
            if params.irony > 60:
                style_desc.append("ironic and self-aware")
            elif params.irony > 40:
                style_desc.append("lightly ironic")
            if params.aggression > 70:
                style_desc.append("aggressive and confrontational")
            elif params.aggression > 50:
                style_desc.append("assertive and direct")
            if params.meme_density > 60:
                style_desc.append("meme-heavy with crypto slang (lfg, gm, 🔥, 🐺)")
            if params.myth_layer > 60:
                style_desc.append("prophetic and mythic tone")
            
            style_str = ", ".join(style_desc) if style_desc else "neutral CT style"
            
            prompt = f"""Transform this text in CT (Crypto Twitter) style:

Original: "{text}"

Style requirements: {style_str}
Keep the same meaning but adapt tone.
Keep it short (under 280 chars).
Return ONLY the transformed text, no quotes or explanations."""

            llm_result = self._call_llm(prompt, max_tokens=200)
            if llm_result and len(llm_result) > 5:
                result = llm_result
        
        # Rule-based transformations (fallback + enhancements)
        # Fragmentation
        if params.fragmentation > 70:
            words = result.split()
            lines = [" ".join(words[i:i+4]) for i in range(0, len(words), 4)]
            result = "\n".join(lines)
        elif params.fragmentation > 50:
            result = result.replace(", ", ",\n")

        # Meme density
        if params.meme_density > 60:
            if not any(m in result for m in ["🔥", "🐺", "lfg", "gm"]):
                result = f"{result} 🔥 lfg 🐺"
        elif params.meme_density > 40:
            if not any(m in result for m in ["🔥", "lfg"]):
                result = f"{result} 🔥"

        # Aggression emphasis
        if params.aggression > 70 and len(result) < 100:
            result = result.upper()
        elif params.aggression > 50:
            result = "obviously... " + result if "obviously" not in result.lower() else result

        # Irony markers
        if params.irony > 60:
            if "obviously" not in result.lower():
                result = f"obviously... {result}"

        # Myth layer
        if params.myth_layer > 70:
            result = f"the future already happened.\n{result}"
        elif params.myth_layer > 50:
            result = f"they don't understand yet.\n{result}"

        return result
    
    # ============ STAGE 5: SAFETY & ANCHORS ============
    def stage5_safety(self, text: str) -> Dict:
        """Add hyperbole markers, ensure no absolute truth claims."""
        violations = []
        markers_added = []
        
        # Check violations
        for pattern in self.SAFETY_VIOLATIONS:
            if re.search(pattern, text.lower()):
                violations.append(f"Potential absolute claim: {pattern}")
        
        # Add markers if needed
        result = text
        if "🔥" not in result and len(text) > 50:
            # Add marker for longer texts
            if any(w in result.lower() for w in ["will", "always", "never", "definitely"]):
                result = f"{result} 🔥"
                markers_added.append("Added 🔥 for potential hyperbole")
        
        return {
            "text": result,
            "violations": violations,
            "markers_added": markers_added,
            "passed": len(violations) == 0
        }
    
    # ============ STAGE 6: OUTPUT FORMATTER ============
    def stage6_formatter(self, text: str, platform: str, intent: str) -> str:
        """Adapt to platform format."""
        if platform == "twitter":
            # Short, rhythmic, line breaks
            if "\n" in text:
                # Already has breaks, ensure not too long
                lines = [l.strip() for l in text.split("\n") if l.strip()]
                text = " ".join(lines)
            if len(text) > 280:
                text = text[:277] + "..."
            return text
        
        elif platform == "thread":
            return f"🧵 {text}"
        
        elif platform == "longpost":
            return f"📝 {text}"
        
        elif platform == "reply":
            if Intent.ATTACK.value in intent:
                return f"💀 {text}"
            return text
        
        return text
    
    # ============ FULL PIPELINE ============
    def process(self, text: str, preset: str = None, custom_params: Dict = None,
                platform: str = "twitter", metadata: Dict = None,
                explain: bool = False) -> PipelineResult:
        """Execute full EDITOR pipeline."""
        
        # Stage 1: Intake
        clean_text = self.stage1_intake(text, metadata)
        
        # Stage 2: Classify
        topics, intent = self.stage2_classify(clean_text)
        
        # Stage 3: MetaController
        params = self.stage3_meta_controller(topics, intent, preset, custom_params)
        explanations = self.explain_params(topics, intent, params) if explain else []
        
        # Stage 4: Styler
        styled = self.stage4_styler(clean_text, params)
        
        # Stage 5: Safety
        safety = self.stage5_safety(styled)
        
        # Stage 6: Formatter
        output = self.stage6_formatter(safety["text"], platform, intent)
        
        return PipelineResult(
            input_text=text,
            topics=topics,
            intent=intent,
            style_params=params.to_dict(),
            styled_text=styled,
            safety_result=safety,
            output_text=output,
            explanations=explanations
        )
    
    def safety_check(self, text: str) -> Dict:
        """Standalone safety check."""
        return self.stage5_safety(text)


def main():
    parser = argparse.ArgumentParser(description="EDITOR - Autonomous Text Style Engine")
    parser.add_argument("--text", help="Input text to process")
    parser.add_argument("--preset", choices=list(PRESETS.keys()), help="Style preset")
    parser.add_argument("--fragmentation", type=int, help="Fragmentation 0-100")
    parser.add_argument("--irony", type=int, help="Irony 0-100")
    parser.add_argument("--aggression", type=int, help="Aggression 0-100")
    parser.add_argument("--meme", type=int, help="Meme density 0-100")
    parser.add_argument("--myth", type=int, help="Myth layer 0-100")
    parser.add_argument("--platform", default="twitter", choices=["twitter", "thread", "longpost", "reply"])
    parser.add_argument("--explain", action="store_true", help="explain parameter choices")
    parser.add_argument("--safety-check", help="Safety check only")
    
    args = parser.parse_args()
    
    editor = Editor()
    
    if args.safety_check:
        result = editor.safety_check(args.safety_check)
        print(json.dumps(result, indent=2))
        return
    
    if not args.text:
        print("Error: --text required")
        return
    
    # Custom params
    custom_params = None
    if any([args.fragmentation, args.irony, args.aggression, args.meme, args.myth]):
        custom_params = {
            "fragmentation": args.fragmentation or 50,
            "irony": args.irony or 50,
            "aggression": args.aggression or 50,
            "meme_density": args.meme or 50,
            "myth_layer": args.myth or 50,
        }
    
    # Process
    result = editor.process(
        text=args.text,
        preset=args.preset,
        custom_params=custom_params,
        platform=args.platform,
        explain=args.explain
    )
    
    print(json.dumps({
        "input": result.input_text,
        "topics": result.topics,
        "intent": result.intent,
        "style_params": result.style_params,
        "output": result.output_text,
        "safety": result.safety_result,
        "explanations": result.explanations
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
