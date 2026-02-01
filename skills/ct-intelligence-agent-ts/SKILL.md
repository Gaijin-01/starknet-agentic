# CT Intelligence Agent (TypeScript)

Crypto Twitter intelligence agent for tracking trends, sentiment, and alpha.

## Overview

Specialized agent for monitoring Crypto Twitter (CT), detecting trends, and identifying trading opportunities through social media analysis.

## Features

- Twitter/X API integration
- Sentiment analysis
- Trending token detection
- Whale mention tracking
- Alpha signal generation

## Usage

```typescript
import { CTIntelligenceAgent } from './src/agent';

const agent = new CTIntelligenceAgent({
  twitterApi: { ... },
  sentimentModel: 'openai',
  alertChannels: ['telegram'],
});

await agent.start({
  track: ['$STRK', '$SLAY', 'Starknet'],
  keywords: ['bullish', 'alpha', 'gm'],
  minEngagement: 1000,
});
```

## Scripts

```bash
# Run agent
npm run start

# Analyze specific account
npm run analyze -- --account 0x...

# Export report
npm run report -- --days 7 --output report.json
```

## Dependencies

- twitter-api-v2
- @anthropic-ai/sdk
- sentiment

## Configuration

```bash
# Environment variables
TWITTER_BEARER_TOKEN=your_token
ANTHROPIC_API_KEY=your_key
SENTIMENT_THRESHOLD=0.6
ALERT_TELEGRAM_BOT_TOKEN=bot_token
ALERT_TELEGRAM_CHAT_ID=chat_id
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No tweets retrieved | Check Twitter API rate limits, verify credentials |
| Sentiment always neutral | Increase sample size, adjust threshold |
| Alerts not sent | Verify Telegram bot token and chat ID |

## Version

**v1.0.0** (2026-02-01) - Initial CT intelligence agent

## License

MIT
