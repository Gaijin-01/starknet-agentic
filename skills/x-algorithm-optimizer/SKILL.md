# X Algorithm Optimizer

Content optimization based on X's open-source algorithm (xai-org/x-algorithm).

## Overview

Scores content and strategies using X algorithm weights. Helps maximize reach and engagement on X/Twitter.

## Usage

```bash
# Score content
python algorithm_scorer.py --score "your content here" --type text --words 50 --hashtags 1

# Score reply to big account
python algorithm_scorer.py --score "Great point!" --is-reply --target-followers 100000

# Show optimal daily strategy
python algorithm_scorer.py --strategy

# Compare content types
python algorithm_scorer.py --compare
```

### CLI Options
| Option | Description |
|--------|-------------|
| `--score` | Content to score |
| `--type` | text/image/video/thread/quote |
| `--words` | Word count |
| `--hashtags` | Number of hashtags (avoid >2) |
| `--is-reply` | Is this a reply? |
| `--target-followers` | Follower count of account you're replying to |
| `--strategy` | Show optimal posting strategy |
| `--compare` | Compare all content types |

## Python API

```python
from algorithm_scorer import AlgorithmScorer, ContentFeatures, StrategyOptimizer

# Score content
scorer = AlgorithmScorer()
features = ContentFeatures(content_type="text", word_count=50, hashtag_count=1)
result = scorer.score_content(features)

# Optimize daily strategy
optimizer = StrategyOptimizer()
daily_mix = optimizer.get_optimal_daily_mix()

# Compare strategies
strategies = [
    {"name": "Thread", "features": {"content_type": "thread", "word_count": 300}},
    {"name": "Quote", "features": {"content_type": "quote", "word_count": 50}},
]
results = scorer.compare_strategies(strategies)
```

## Example Output

### Strategy Comparison
```
Strategy                        Score
------------------------------------------
Reply to 100k account           45.30
Thread (5 tweets)               38.50
Quote tweet                     32.20
Text + image                    18.40
Plain text                      15.00
Spammy (5 hashtags)              8.50
```

### Content Scoring
```
CONTENT SCORE: 15.00

Engagement Predictions
  p_reply: 0.0200
  p_quote: 0.0050
  ...

Score Breakdown
  reply_contribution: 0.60
  quote_contribution: 0.12
  ...

Recommendations
  • Add image/video for +20-30% engagement
  • Replies to high-follower accounts have highest visibility ROI
```

## Scoring Formula

```
Final Score = Σ (weight × P(action))
```

### Engagement Weights
| Action | Weight |
|--------|--------|
| Report | -10.0 |
| Quote | 3.5 |
| Reply | 3.0 |
| Share | 2.5 |
| Repost | 2.0 |
| Follow | 1.5 |
| Favorite | 1.0 |

### Negative Signals
| Action | Weight |
|--------|--------|
| Report | -10.0 |
| Block | -3.0 |
| Mute | -2.0 |
| Not Interested | -5.0 |

## Strategy Tips

1. **Quotes > Reposts** (3.5x vs 2.0x)
2. **Replies within 5 min** get 30x visibility
3. **Author diversity** — don't flood, space out
4. **Avoid negative triggers** — spam words reduce score
5. **Optimal length** — 50-150 chars

## Troubleshooting

```bash
# Debug mode
python algorithm_scorer.py --debug

# Validate weights
python algorithm_scorer.py --compare
```

