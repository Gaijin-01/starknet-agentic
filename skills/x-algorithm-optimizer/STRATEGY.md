# X Algorithm Optimizer

## Overview
Стратегии оптимизации контента на основе открытого алгоритма X (xai-org/x-algorithm).

## Algorithm Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FOR YOU FEED RANKING                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [1. CANDIDATE SOURCES]                                      │
│  ├── Thunder (In-Network) ← accounts you follow              │
│  └── Phoenix Retrieval (Out-of-Network) ← ML discovery       │
│                                                              │
│  [2. PHOENIX SCORER] Grok-based Transformer                  │
│  Predicts probabilities for EACH action type                 │
│                                                              │
│  [3. WEIGHTED SCORER]                                        │
│  Final Score = Σ (weight_i × P(action_i))                    │
│                                                              │
│  [4. AUTHOR DIVERSITY]                                       │
│  Attenuates repeated same-author scores                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Scoring Weights (inferred from code)

### POSITIVE (maximize these)

| Action | Estimated Weight | Strategy |
|--------|-----------------|----------|
| `reply` | HIGH (~30x like) | Провоцируй дискуссию, задавай вопросы |
| `quote` | HIGH (~25x like) | Создавай quotable контент с инсайтами |
| `repost` | MEDIUM (~10x like) | Делай контент shareworthy |
| `favorite` | BASE (1x) | Минимум - лайки |
| `follow_author` | VERY HIGH | Новый фолловер = большой сигнал |
| `dwell` | MEDIUM | Длинный контент = больше времени чтения |
| `video_view` | MEDIUM | Видео > текст по engagement |
| `click` | LOW | Клики по ссылкам |

### NEGATIVE (avoid triggering)

| Action | Impact | Avoid |
|--------|--------|-------|
| `block_author` | SEVERE | Спам, агрессия, оффтоп |
| `mute_author` | HIGH | Слишком частые посты |
| `report` | SEVERE | Нарушения ToS |
| `not_interested` | MEDIUM | Нерелевантный контент |

## Optimization Strategies

### 1. Content Type Priority

```python
CONTENT_PRIORITY = {
    "thread": 1.5,      # Threads get more dwell time
    "quote": 1.3,       # Quotes trigger conversations  
    "reply": 1.2,       # Replies to big accounts
    "video": 1.2,       # Video views weighted
    "image": 1.1,       # Images increase engagement
    "text": 1.0,        # Base text post
    "link": 0.9,        # External links = users leave
}
```

### 2. Reply Strategy (highest ROI)

```python
REPLY_TARGETS = {
    "high_follower_accounts": True,    # Visibility boost
    "trending_topics": True,           # Discovery
    "early_to_viral": True,           # First replies get seen
    "controversial_takes": False,      # Risk of block/mute
}

# Optimal reply timing
REPLY_TIMING = {
    "seconds_after_post": [30, 300],   # Early but not instant
    "avoid_instant": True,             # Looks botty
}
```

### 3. Thread Optimization

```python
THREAD_RULES = {
    "optimal_length": [3, 7],          # 3-7 tweets
    "hook_first_tweet": True,          # Strong opener
    "cta_last_tweet": True,            # Call to action
    "numbered": True,                  # 1/, 2/, 3/ format
    "self_reply_chain": True,          # Reply to own tweet
}
```

### 4. Author Diversity Awareness

Алгоритм штрафует повторные посты от одного автора в фиде.

```python
DIVERSITY_RULES = {
    "max_posts_per_hour": 3,           # Don't flood
    "min_gap_minutes": 20,             # Space between posts
    "vary_content_types": True,        # Mix text/image/video
    "engage_with_others": True,        # Don't just post
}
```

### 5. Negative Signal Avoidance

```python
AVOID_PATTERNS = [
    # Content that triggers mute/block
    "repetitive_phrases",              # Same text = spam
    "aggressive_language",             # Triggers reports
    "off_topic_replies",               # Irrelevant = not_interested
    "excessive_hashtags",              # >3 hashtags = spammy
    "follow_for_follow",               # Obvious growth hacking
    "dm_me",                           # Scam signal
    "giveaway_spam",                   # Fake engagement
    
    # Timing patterns
    "posting_every_minute",            # Obvious bot
    "identical_reply_times",           # Automation detection
    "24_7_activity",                   # No human does this
]
```

## Phoenix Retrieval (Out-of-Network Discovery)

Как попасть в For You людей, которые тебя НЕ фолловят:

### Two-Tower Model

```
User Tower: encodes user features + engagement history → user_embedding
Candidate Tower: encodes post features → post_embedding

Similarity = dot_product(user_embedding, post_embedding)
```

### Optimization for Out-of-Network Reach

1. **Topic Alignment**: Пиши о темах, которые интересуют твою target audience
2. **Engagement Velocity**: Быстрые лайки/реплаи в первые минуты = сигнал качества
3. **Social Graph**: Engagement от accounts с большим overlap = boost
4. **Fresh Content**: Новые посты приоритетнее старых

## Implementation for Style-Learner

### Updated Scoring

```python
def calculate_post_score(post_metrics):
    """
    Approximate X algorithm scoring
    Based on xai-org/x-algorithm analysis
    """
    weights = {
        'reply': 30.0,
        'quote': 25.0,
        'repost': 10.0,
        'favorite': 1.0,
        'follow': 50.0,
        'dwell_time_sec': 0.1,
        'video_watch_pct': 0.5,
        'block': -100.0,
        'mute': -50.0,
        'report': -200.0,
        'not_interested': -10.0,
    }
    
    score = 0.0
    for action, weight in weights.items():
        if action in post_metrics:
            score += weight * post_metrics[action]
    
    return score

def optimize_content_strategy(style_profile):
    """
    Optimize posting strategy based on algorithm knowledge
    """
    strategy = {
        # Content mix (per day)
        'threads': 1,           # High dwell time
        'quote_tweets': 3,      # High engagement weight
        'replies': 10,          # Highest ROI
        'original_posts': 2,    # Brand building
        
        # Timing
        'peak_hours': style_profile.timing.peak_hours,
        'min_gap_minutes': 20,
        
        # Targets
        'reply_to_followers_of': [
            '@StarkWareLtd',
            '@Starknet',
            '@ethereum',
        ],
        
        # Avoid
        'max_hashtags': 2,
        'no_repetitive_text': True,
        'human_delays': True,
    }
    
    return strategy
```

### Rate Limits (Anti-Detection + Algorithm Friendly)

```python
SAFE_LIMITS = {
    'posts_per_hour': 3,        # Below spam threshold
    'replies_per_hour': 10,     # Engagement heavy
    'likes_per_hour': 20,       # Casual interaction
    'quotes_per_hour': 3,       # Quality over quantity
    
    # Daily caps
    'posts_per_day': 15,
    'replies_per_day': 50,
    'total_actions_per_day': 200,
}
```

## Key Takeaways

1. **Replies > Quotes > Reposts > Likes** — weight hierarchy
2. **Avoid negative signals** — blocks/mutes destroy reach permanently
3. **Early engagement matters** — first minutes are critical for Phoenix retrieval
4. **Author diversity** — don't spam, space out content
5. **Dwell time** — threads and detailed content rank higher
6. **Social graph overlap** — engage with accounts your target follows

## References

- [xai-org/x-algorithm](https://github.com/xai-org/x-algorithm) — Full source code
- Phoenix: Grok-based transformer for ranking
- Thunder: In-network content store
- Candidate Pipeline: Orchestration framework
