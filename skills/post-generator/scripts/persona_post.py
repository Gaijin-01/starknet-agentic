#!/usr/bin/env python3
"""
Post Generator with Persona Vocabulary
Generates posts using learned vocabulary and tone.
Includes comprehensive error handling.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(message)s'
)
logger = logging.getLogger("persona_post")

# Persona profile with safe access patterns
DEFAULT_PROFILE = {
    "tone": ["minimal", "cryptic", "confident"],
    "persona": {
        "name": "SefirotWatch"
    },
    "vocabulary": {
        "frequent": ["higher", "execution", "patience"],
        "signature_phrases": []
    },
    "emoji_usage": {"🐺": 3, "🔥": 2},
    "avg_word_count": 10
}


class ProfileError(Exception):
    """Error accessing or using persona profile."""
    pass


def load_profile(profile_path: str = None) -> Dict:
    """
    Load persona profile from file or return default.
    
    Args:
        profile_path: Optional path to profile JSON file
        
    Returns:
        Persona profile dict
    """
    if profile_path and Path(profile_path).exists():
        try:
            with open(profile_path, 'r') as f:
                profile = json.load(f)
            logger.info(f"Loaded profile from {profile_path}")
            return profile
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load profile: {e}, using default")
    
    return DEFAULT_PROFILE


def safe_get_profile_value(profile: Dict, key_path: str, default: Any = None) -> Any:
    """
    Safely get a nested value from profile.
    
    Args:
        profile: Profile dict
        key_path: Dot-separated path (e.g., "persona.name")
        default: Default value if not found
        
    Returns:
        Value or default
    """
    try:
        keys = key_path.split(".")
        value = profile
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
        return value if value is not None else default
    except (AttributeError, TypeError):
        return default


def get_persona_name(profile: Dict) -> str:
    """Safely get persona name from profile."""
    return safe_get_profile_value(profile, "persona.name", "SefirotWatch")


def get_tone(profile: Dict) -> List[str]:
    """Safely get tone from profile."""
    tone = safe_get_profile_value(profile, "tone", [])
    return tone if tone else DEFAULT_PROFILE["tone"]


def get_vocabulary(profile: Dict) -> List[str]:
    """Safely get vocabulary from profile."""
    vocab = safe_get_profile_value(profile, "vocabulary.frequent", [])
    return vocab if vocab else DEFAULT_PROFILE["vocabulary"]["frequent"]


def get_emojis(profile: Dict) -> List[str]:
    """Safely get emoji list from profile."""
    emoji_usage = safe_get_profile_value(profile, "emoji_usage", {})
    if isinstance(emoji_usage, dict):
        return list(emoji_usage.keys())
    return list(DEFAULT_PROFILE["emoji_usage"].keys())


def generate_post(tweet_content: str, post_type: str = "quote", 
                  profile: Dict = None) -> str:
    """
    Generate post in persona style using learned vocabulary.
    
    Args:
        tweet_content: Content to respond to
        post_type: Type of post (quote, timeline)
        profile: Optional persona profile
        
    Returns:
        Generated post text
    """
    try:
        profile = profile or DEFAULT_PROFILE
        
        # Extract key info from tweet (basic keyword extraction)
        keywords = ["Loot Survivor", "PVP", "Starkware", "Community"]
        
        # Use learned vocabulary with safe access
        words = get_vocabulary(profile)
        emojis = get_emojis(profile)
        
        if not words:
            words = DEFAULT_PROFILE["vocabulary"]["frequent"]
        if not emojis:
            emojis = list(DEFAULT_PROFILE["emoji_usage"].keys())
        
        # Select words (ensure we have enough)
        while len(words) < 3:
            words.extend(DEFAULT_PROFILE["vocabulary"]["frequent"])
        words = words[:3]
        
        # Select emojis (ensure we have enough)
        while len(emojis) < 2:
            emojis.extend(list(DEFAULT_PROFILE["emoji_usage"].keys()))
        emojis = emojis[:2]
        
        if post_type == "quote":
            # Quote style: short, add value
            templates = [
                f"{words[0].capitalize()} {words[1]}. {emojis[1]}",
                f"Execution {words[2]}. {emojis[0]}",
                f"New development. Thoughts? {emojis[0]}",
                f"{words[0].capitalize()} soon. {emojis[1]}",
            ]
        else:
            # Timeline post style
            templates = [
                f"just in: new development. thoughts? {emojis[0]}",
                f"{words[0].capitalize()} vibes only. {emojis[1]} {emojis[0]}",
                f"Building in silence. {words[1]} {words[2]}. {emojis[0]}",
            ]
        
        # Select template based on content
        selected_template = templates[0]
        
        if "gm" in tweet_content.lower():
            selected_template = f"{words[0].capitalize()} {words[1]}. {emojis[1]}"
        elif "?" in tweet_content:
            selected_template = f"New development. Thoughts? {emojis[0]}"
        
        logger.info(f"Generated {post_type} post: {selected_template[:50]}...")
        return selected_template
        
    except Exception as e:
        logger.error(f"Error generating post: {e}")
        # Fallback to safe default
        return "gm 🐺"


def generate_batch(tweets: List[str], post_type: str = "quote",
                   profile: Dict = None) -> List[Dict]:
    """
    Generate posts for multiple tweets.
    
    Args:
        tweets: List of tweet contents
        post_type: Type of post
        profile: Optional persona profile
        
    Returns:
        List of result dicts
    """
    profile = profile or load_profile()
    results = []
    
    for i, tweet in enumerate(tweets):
        try:
            content = generate_post(tweet, post_type, profile)
            results.append({
                "index": i,
                "original_tweet": tweet,
                "content": content,
                "persona": get_persona_name(profile),
                "success": True
            })
        except Exception as e:
            logger.error(f"Failed to generate post for tweet {i}: {e}")
            results.append({
                "index": i,
                "original_tweet": tweet,
                "error": str(e),
                "success": False
            })
    
    return results


def main():
    """CLI entry point."""
    import sys
    
    # Parse arguments
    tweet = sys.argv[1] if len(sys.argv) > 1 else "Starknet update"
    post_type = sys.argv[2] if len(sys.argv) > 2 else "quote"
    profile_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    try:
        # Load profile
        profile = load_profile(profile_path)
        persona_name = get_persona_name(profile)
        
        # Generate post
        post = generate_post(tweet, post_type, profile)
        
        # Output for queue
        result = {
            "type": post_type,
            "original_tweet": tweet,
            "content": post,
            "persona_used": persona_name,
            "success": True
        }
        
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        # Safe fallback output
        result = {
            "type": post_type,
            "original_tweet": tweet,
            "content": "gm 🐺",
            "persona_used": "SefirotWatch",
            "success": False,
            "error": str(e)
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
