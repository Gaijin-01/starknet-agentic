#!/usr/bin/env python3
"""
Multi-Layer Style Processor
Implements 5-layer architecture for authentic Sefirot-style content generation.
"""

import json
import re
import argparse
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


class Topic(Enum):
    CRYPTO = "crypto"
    GEOPOLITICS = "geopolitics"
    RELIGION = "religion"
    CT_DRAMA = "ct-drama"
    PHILOSOPHY = "philosophy"
    PERSONAL = "personal"
    MEME = "meme"


class Intent(Enum):
    ENGAGE = "engage"        # Hook, viral
    ATTACK = "attack"        # Mock, put down
    SIGNAL = "signal"        # Show knowledge
    MYTH_BUILDING = "myth-building"  # Create narrative
    PROCESS = "process"      # Think out loud


@dataclass
class SchizoParams:
    """Level 3: Schizo Filter Parameters (0-100)"""
    fragmentation: int = 50
    irony: int = 50
    aggression: int = 50
    myth_layer: int = 50
    meme_density: int = 50
    
    def to_dict(self) -> Dict:
        return {
            "fragmentation": self.fragmentation,
            "irony": self.irony,
            "aggression": self.aggression,
            "myth_layer": self.myth_layer,
            "meme_density": self.meme_density
        }


PRESETS = {
    "normal": SchizoParams(fragmentation=20, irony=70, aggression=20, myth_layer=30, meme_density=30),
    "ct": SchizoParams(fragmentation=40, irony=50, aggression=30, myth_layer=40, meme_density=50),
    "shizo": SchizoParams(fragmentation=70, irony=60, aggression=50, myth_layer=60, meme_density=60),
    "v-myaso": SchizoParams(fragmentation=90, irony=30, aggression=80, myth_layer=80, meme_density=40),
    "attack": SchizoParams(fragmentation=50, irony=70, aggression=90, myth_layer=20, meme_density=70),
    "meme": SchizoParams(fragmentation=60, irony=40, aggression=40, myth_layer=30, meme_density=90),
}


class MultiLayerStyleProcessor:
    """Core processor implementing 5-layer architecture."""
    
    # Topic keywords for classification
    TOPIC_KEYWORDS = {
        Topic.CRYPTO: ["starknet", "zk", "crypto", "defi", "l2", "token", "rollup", "eth", "btc", "strk"],
        Topic.GEOPOLITICS: ["war", "government", "state", "iran", "israel", "usa", "china", "trump"],
        Topic.RELIGION: ["god", "jewish", "israel", "zion", "torah", "bible", "faith"],
        Topic.CT_DRAMA: ["twitter", "x", "ct", "crypto twitter", "drama", "beef", "reply"],
        Topic.PHILOSOPHY: ["meaning", "purpose", "reality", "truth", "system", "meta", "think"],
        Topic.PERSONAL: ["tired", "gm", "shalom", "feeling", "day", "sleep", "family"],
        Topic.MEME: ["lmao", "rofl", "funny", "joke", "meme", "schizodio", "lobster", "lfg"],
    }
    
    # Intent patterns
    INTENT_PATTERNS = {
        Intent.ENGAGE: ["explode", "viral", "everyone", "watch", "listen"],
        Intent.ATTACK: ["suck", "stupid", "wrong", "actually", "you're not", "imagine"],
        Intent.SIGNAL: ["know", "understand", "obviously", "clearly", "as i said"],
        Intent.MYTH_BUILDING: ["future", "ready", "they don't", "we will", "history"],
        Intent.PROCESS: ["thinking", "wonder", "question", "not sure", "trying to"],
    }
    
    # Safety anchor patterns
    SAFETY_VIOLATIONS = [
        r"i know the truth",
        r"i am certain",
        r"this is absolute",
        r"no doubt",
    ]
    
    SAFETY_MARKERS = [
        "🔥", "obvious", "maybe", "perhaps", "possibly",
        "probably", "seems", "looks like", "feel like",
    ]
    
    def __init__(self):
        pass
    
    def classify_topic(self, text: str) -> List[Topic]:
        """Level 1: Topic Classification"""
        text_lower = text.lower()
        topics = []
        
        for topic, keywords in self.TOPIC_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                topics.append(topic)
        
        return topics if topics else [Topic.CRYPTO]  # Default fallback
    
    def detect_intent(self, text: str) -> Intent:
        """Level 2: Intent Detection"""
        text_lower = text.lower()
        
        scores = {}
        for intent, patterns in self.INTENT_PATTERNS.items():
            score = sum(1 for p in patterns if p in text_lower)
            scores[intent] = score
        
        # Return highest scoring intent
        best = max(scores.items(), key=lambda x: x[1])
        return best[0] if best[1] > 0 else Intent.ENGAGE  # Default
    
    def apply_schizo_filter(self, text: str, params: SchizoParams) -> str:
        """Level 3: Apply Schizo Filter"""
        # This is a simplified transformation
        # In production, this would use the params to guide LLM generation
        
        result = text
        
        # Fragmentation
        if params.fragmentation > 60:
            # Add breaks
            words = result.split()
            break_points = []
            for i, w in enumerate(words):
                if len(w) < 4 and i > 0 and i < len(words) - 1:
                    if params.fragmentation > 80 and i % 3 == 0:
                        break_points.append(i)
                    elif params.fragmentation > 60 and i % 5 == 0:
                        break_points.append(i)
            
            if break_points:
                new_words = []
                last = 0
                for bp in break_points:
                    new_words.extend(words[last:bp])
                    new_words.append("\n")
                    last = bp
                new_words.extend(words[last:])
                result = " ".join(new_words)
        
        # Add irony markers if high irony
        if params.irony > 70:
            if not any(m in result.lower() for m in self.SAFETY_MARKERS[:4]):
                if params.aggression > 50:
                    result = f"obviously... {result}" if "obviously" not in result.lower() else result
        
        # Meme density
        if params.meme_density > 50:
            memes = []
            if Topic.MEME in self.classify_topic(text):
                memes = ["lfg", "gm", "schizodio", "🐺", "🔥"]
            for meme in memes:
                if meme.lower() not in result.lower() and params.meme_density > 70:
                    result = f"{result} {meme}"
        
        return result
    
    def safety_check(self, text: str) -> Dict[str, Any]:
        """Level 4: Safety & Reality Anchors"""
        violations = []
        markers_found = []
        
        # Check for violations
        for pattern in self.SAFETY_VIOLATIONS:
            if re.search(pattern, text.lower()):
                violations.append(f"Possible absolute claim: {pattern}")
        
        # Check for safety markers
        for marker in self.SAFETY_MARKERS:
            if marker in text.lower():
                markers_found.append(marker)
        
        passed = len(violations) == 0
        
        return {
            "passed": passed,
            "violations": violations,
            "safety_markers": markers_found,
            "recommendations": [] if passed else [
                "Add hyperbole markers (🔥, obviously, etc.)",
                "Add irony indicators",
                "Avoid absolute truth claims"
            ]
        }
    
    def format_output(self, text: str, platform: str, topic: Topic, intent: Intent) -> str:
        """Level 5: Output Formatter"""
        if platform == "twitter":
            # Short, rhythmic, line breaks
            lines = text.split("\n") if "\n" in text else text.split(". ")
            # Limit length
            result = ". ".join([l.strip() for l in lines if l.strip()])
            if len(result) > 280:
                result = result[:277] + "..."
            return result
        
        elif platform == "thread":
            # Escalation curve
            return f"🧵 {text}"
        
        elif platform == "longpost":
            # Hook first, meaning second
            return f"📝 {text}"
        
        elif platform == "reply":
            # Dominance or cold shutdown
            if intent == Intent.ATTACK:
                return f"💀 {text}"
            else:
                return text
        
        return text
    
    def process(self, text: str, topic: Topic, intent: Intent, 
                schizo: SchizoParams, platform: str = "twitter") -> Dict[str, Any]:
        """Full 5-layer processing pipeline."""
        
        # Level 1 & 2 already done in init
        topic_tags = self.classify_topic(text)
        
        # Level 3: Apply schizo filter
        filtered = self.apply_schizo_filter(text, schizo)
        
        # Level 4: Safety check
        safety = self.safety_check(filtered)
        
        # Level 5: Format
        output = self.format_output(filtered, platform, topic, intent)
        
        return {
            "input": text,
            "topic_tags": [t.value for t in topic_tags],
            "intent": intent.value,
            "schizo_params": schizo.to_dict(),
            "safety": safety,
            "output": output
        }


class StyleProcessorError(Exception):
    """Base exception for style processor errors."""
    pass


class TopicClassificationError(StyleProcessorError):
    """Raised when topic classification fails."""
    pass


class IntentDetectionError(StyleProcessorError):
    """Raised when intent detection fails."""
    pass


class SafetyCheckError(StyleProcessorError):
    """Raised when safety check fails."""
    pass


def main():
    try:
        parser = argparse.ArgumentParser(description="Multi-Layer Style Processor")
        parser.add_argument("--text", help="Input text")
        parser.add_argument("--topic", choices=[t.value for t in Topic], default="crypto")
        parser.add_argument("--intent", choices=[i.value for i in Intent], default="engage")
        parser.add_argument("--schizo", type=int, default=50, help="Schizo level 0-100")
        parser.add_argument("--preset", choices=list(PRESETS.keys()), help="Use preset")
        parser.add_argument("--fragmentation", type=int, help="Fragmentation 0-100")
        parser.add_argument("--irony", type=int, help="Irony 0-100")
        parser.add_argument("--aggression", type=int, help="Aggression 0-100")
        parser.add_argument("--myth", type=int, help="Myth layer 0-100")
        parser.add_argument("--meme", type=int, help="Meme density 0-100")
        parser.add_argument("--platform", default="twitter", choices=["twitter", "thread", "longpost", "reply"])
        parser.add_argument("--safety-check", help="Text to check safety")
        parser.add_argument("--auto-topic", action="store_true", help="Auto detect topic")
        
        args = parser.parse_args()
        
        processor = MultiLayerStyleProcessor()
        
        if args.safety_check:
            try:
                result = processor.safety_check(args.safety_check)
                print(json.dumps(result, indent=2))
            except Exception as e:
                raise SafetyCheckError(f"Safety check failed: {e}")
            return
        
        if not args.text:
            print("Error: --text required")
            return
        
        # Get schizo params
        try:
            if args.preset and args.preset in PRESETS:
                schizo = PRESETS[args.preset]
            else:
                schizo = SchizoParams(
                    fragmentation=args.fragmentation or args.schizo,
                    irony=args.irony or args.schizo,
                    aggression=args.aggression or args.schizo,
                    myth_layer=args.myth or args.schizo,
                    meme_density=args.meme or args.schizo
                )
        except Exception as e:
            raise StyleProcessorError(f"Failed to create schizo params: {e}")
        
        # Auto-detect topic
        try:
            if args.auto_topic:
                topics = processor.classify_topic(args.text)
                topic = topics[0] if topics else Topic.CRYPTO
            else:
                topic = Topic(args.topic)
        except Exception as e:
            raise TopicClassificationError(f"Topic classification failed: {e}")
        
        # Auto-detect intent
        try:
            intent = processor.detect_intent(args.text)
        except Exception as e:
            raise IntentDetectionError(f"Intent detection failed: {e}")
        
        # Process
        try:
            result = processor.process(args.text, topic, intent, schizo, args.platform)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except Exception as e:
            raise StyleProcessorError(f"Processing failed: {e}")
            
    except StyleProcessorError as e:
        print(f"Style Processor Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    import sys
    main()
