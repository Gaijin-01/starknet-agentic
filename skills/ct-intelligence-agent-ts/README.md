# 🐦 CT Intelligence Agent

x402-compatible API for Crypto Twitter intelligence - trends, sentiment, influencer tracking.

## Monetization

| Endpoint | Price | Description |
|----------|-------|-------------|
| `/api/overview` | FREE | Market overview |
| `/api/trending` | $0.001 | Hashtag trends |
| `/api/influencers` | $0.002 | Influencer analysis |
| `/api/sentiment` | $0.002 | Sentiment analysis |
| `/api/narratives` | $0.003 | CT narratives |
| `/api/alpha` | $0.005 | Alpha opportunities |
| `/api/full-report` | $0.01 | Complete report |

**Estimated revenue:** $200-2000/month

## Quick Start

```bash
bun install
bun run dev
```

## Deploy

```bash
vercel --prod
```

## Project Structure

```
ct-intelligence-agent-ts/
├── package.json
├── tsconfig.json
├── vercel.json
└── src/
    ├── index.ts       # Main agent
    └── data/
        └── ct-data.json
```

## Based on langoustine69 Pattern

[Portfolio](https://langoustine69.github.io) | [API](https://langoustine69.dev)
