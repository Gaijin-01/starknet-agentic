#!/usr/bin/env python3
"""
Styler Engine v2 — объединённый подход
MiniMax + corpus statistics + EDITOR params + safety
"""

import json
import random
import re
import os
from typing import Dict, List, Optional
from collections import Counter
import requests


# ================================
# MiniMax API Client
# ================================
class MiniMaxClient:
    """MiniMax API client with OpenAI-compatible API."""

    def __init__(self):
        self.api_key = os.getenv("MINIMAX_API_KEY")
        self.base_url = "https://api.minimax.io/v1/chat/completions"

    def generate(self, prompt: str, hints: List[str] = None, style_params: Dict = None) -> str:
        """Generate text using MiniMax OpenAI-compatible API."""
        if not self.api_key:
            return self._fallback(prompt)

        hints_text = "\n".join(hints[:20]) if hints else ""
        style_desc = ""
        if style_params:
            style_desc = f"\n\nСтиль: fragmentation={style_params.get('fragmentation', 30)}, irony={style_params.get('irony', 30)}, aggression={style_params.get('aggression', 15)}"

        system_prompt = f"""Ты — Sefirot.

Стиль: минималистичный, криптографичный, уверенный. Редкие стратегические эмодзи (🐺🔥🦞🕶️🦅). Бимодальная длина. Темы: Starknet/L2, крипто, философия. Build-focused, поддержка экосистемы. Низкая агрессия для своих.

Контекст из твоих твитов:
{hints_text}{style_desc}

Пиши в ТВОЁМ стиле. Готовый текст для Twitter. Максимум 280 символов."""

        try:
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "MiniMax-M2.1",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 280
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception as e:
            print(f"[MiniMax] Error: {e}")
            return self._fallback(prompt)

    def _fallback(self, prompt: str) -> str:
        return f"[MiniMax unavailable] {prompt[:100]}"


# ================================
# Corpus Manager
# ================================
class CorpusManager:
    """Load corpus and build statistics."""

    def __init__(self, path: str = "assets/corpus.json"):
        self.path = path
        self.api_key = os.getenv("MINIMAX_API_KEY")
        self.corpus: List[str] = []
        self.bigrams: Dict[tuple, int] = {}
        self.trigrams: Dict[tuple, int] = {}
        self.unigrams: Counter = Counter()
        self.emoji_freq: Counter = Counter()
        self.keywords: Counter = Counter()
        self.n_tweets: int = 0
        self.avg_length: float = 0

    def load(self) -> bool:
        """Load corpus and build stats."""
        if not os.path.exists(self.path):
            print(f"[Corpus] File not found: {self.path}")
            return False

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.corpus = data if isinstance(data, list) else data.get("tweets", [])
        except Exception as e:
            print(f"[Corpus] Load error: {e}")
            return False

        self._build_stats()
        print(f"[Corpus] Loaded {self.n_tweets} tweets, avg len {self.avg_length:.0f}")
        return True

    def _build_stats(self):
        """Build n-gram and frequency statistics."""
        if not self.corpus:
            return

        all_text = " ".join(self.corpus)
        words = all_text.split()

        # N-grams
        self.bigrams = {}
        for i in range(len(words) - 1):
            pair = (words[i], words[i + 1])
            self.bigrams[pair] = self.bigrams.get(pair, 0) + 1

        self.trigrams = {}
        for i in range(len(words) - 2):
            triple = (words[i], words[i + 1], words[i + 2])
            self.trigrams[triple] = self.trigrams.get(triple, 0) + 1

        self.unigrams = Counter(words)

        # Emoji
        emojis = re.findall(r'[🔹🕶️🦅🦞🐺🔥💀🚀🎮📈👀🎯🤔😂👍]', all_text)
        self.emoji_freq = Counter(emojis)

        # Keywords (3+ occurrences, len > 3)
        self.keywords = Counter(w for w, c in self.unigrams.items() if c >= 3 and len(w) > 3)

        self.n_tweets = len(self.corpus)
        self.avg_length = sum(len(t) for t in self.corpus) / self.n_tweets

    def get_top_bigrams(self, n: int = 20) -> List[str]:
        """Get top n bigrams as hints."""
        sorted_bigrams = sorted(self.bigrams.items(), key=lambda x: -x[1])
        return [f"{w1} {w2}" for (w1, w2), _ in sorted_bigrams[:n]]

    def get_context_summary(self) -> str:
        """Human-readable summary for prompt."""
        if not self.corpus:
            return "Стиль: прямой, build-focused."

        summary = f"Проанализировано {self.n_tweets} твитов. "
        summary += f"Средняя длина: {self.avg_length:.0f} символов. "

        if self.keywords:
            top_k = list(self.keywords.most_common(10))
            summary += f"Ключевые слова: {', '.join([k[0] for k in top_k])}. "

        if self.emoji_freq:
            top_e = list(self.emoji_freq.most_common(5))
            summary += f"Топ эмодзи: {', '.join([e[0] for e in top_e])}."

        return summary


# ================================
# Safety Checker
# ================================
FORBIDDEN_PATTERNS = [
    r"i know the truth",
    r"i am certain",
    r"this is absolute",
    r"no doubt",
    r"definitely",
    r"i know for sure",
    r"without a doubt"
]

def safety_check(text: str) -> List[str]:
    """Check for forbidden patterns."""
    violations = []
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            violations.append(pattern)
    return violations


# ================================
# EDITOR Params Application
# ================================
def apply_editor_params(text: str, params: Dict) -> str:
    """
    Apply fragmentation, irony, meme_density, myth_layer.
    Based on combined approach (simple + strategic).
    """
    frag = params.get("fragmentation", 30)
    irony = params.get("irony", 30)
    meme = params.get("meme_density", 10)
    myth = params.get("myth_layer", 5)
    agg = params.get("aggression", 15)

    # Fragmentation: break long sentences
    if frag > 50:
        # Replace period + space with period + newline for rhythm
        text = re.sub(r"(\.|!|\?)\s+", r"\1\n", text)
        # Clean up multiple newlines
        text = re.sub(r"\n{3,}", "\n\n", text)

    # Irony: strategic markers
    if irony > 60:
        if "obviously" not in text.lower():
            text = f"{text} 🤔"
        if "starknet" in text.lower() and irony > 70:
            # Light irony, not harsh
            if "🤔" not in text:
                text = text.replace("starknet", "starknet 🤔")

    # Meme density: strategic emoji insertion
    if meme > 30:
        emoji_pool = ['🐺', '🔥', '🦞', '🕶️', '🦅']
        words = text.split()
        if words:
            # Add emoji every N words based on density
            step = max(1, 10 - meme // 10)
            for i in range(0, len(words), step):
                if not any(e in words[i] for e in emoji_pool):
                    words[i] = f"{words[i]} {random.choice(emoji_pool)}"
            text = " ".join(words)

    # Myth layer: hype prefix/suffix
    if myth > 50:
        text = f"⚡ {text} ⚡"
    elif myth > 30:
        text = f"🚀 {text}"

    # Aggression: only for non-ecosystem (agg > 50)
    if agg > 50 and "💀" not in text:
        text = f"💀 {text}"

    return text


# ================================
# Main Entry Point
# ================================
def style_text(input_text: str, style_params: Dict,
               corpus_path: str = "assets/corpus.json") -> Dict:
    """
    Main styler function.

    Args:
        input_text: Topic or tweet to respond to
        style_params: {fragmentation, irony, aggression, meme_density, myth_layer}
        corpus_path: Path to corpus.json

    Returns:
        {styled_text, violations, used_minimax, corpus_size}
    """
    # Load corpus
    corpus_manager = CorpusManager(corpus_path)
    has_corpus = corpus_manager.load()

    # Generate with MiniMax
    used_minimax = False
    if has_corpus and corpus_manager.api_key:
        hints = corpus_manager.get_top_bigrams(20)
        client = MiniMaxClient()
        output = client.generate(input_text, hints, style_params)
        used_minimax = True
    elif has_corpus:
        # Fallback: construct from corpus patterns
        hints = corpus_manager.get_top_bigrams(10)
        client = MiniMaxClient()
        output = client.generate(input_text, hints, style_params)
        used_minimax = False
    else:
        output = input_text  # Pass through

    # Apply EDITOR params
    styled = apply_editor_params(output, style_params)

    # Safety check
    violations = safety_check(styled)
    safe_text = styled if not violations else f"[BLOCKED] {styled}"

    return {
        "styled_text": safe_text,
        "violations": violations,
        "used_minimax": used_minimax,
        "corpus_size": corpus_manager.n_tweets,
        "style_params": style_params
    }


# ================================
# CLI Test
# ================================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Styler Engine v2")
    parser.add_argument("--text", required=True, help="Input text/topic")
    parser.add_argument("--corpus", default="assets/corpus.json")
    parser.add_argument("--fragmentation", type=int, default=45)
    parser.add_argument("--irony", type=int, default=50)
    parser.add_argument("--aggression", type=int, default=15)
    parser.add_argument("--meme", type=int, default=25)
    parser.add_argument("--myth", type=int, default=40)

    args = parser.parse_args()

    params = {
        "fragmentation": args.fragmentation,
        "irony": args.irony,
        "aggression": args.aggression,
        "meme_density": args.meme,
        "myth_layer": args.myth
    }

    result = style_text(args.text, params, args.corpus)

    print("\n--- RESULT ---")
    print(result["styled_text"])
    print(f"\nMeta: MiniMax={result['used_minimax']}, Corpus={result['corpus_size']}, Violations={result['violations']}")
