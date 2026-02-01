---
name: starknet-yield-agent
description: |
  x402 Paid API for Starknet DeFi yields, protocol analytics, and risk analysis.
  Based on langoustine69's x402 agent pattern.
  
  Monetization model:
  - Free endpoint: Market overview
  - Paid endpoints: Detailed data ($0.001-$0.01 per call)
  - x402 micropayments via Lightning/USDC/ETH
---

# Starknet Yield Agent (x402 Paid API)

x402-compatible API for Starknet DeFi yields and analytics.

## Monetization

| Endpoint | Price | Revenue potential |
|----------|-------|-----------------|
| `/api/yields-summary` | FREE | Traffic driver |
| `/api/top-yields` | $0.001/call | Medium |
| `/api/protocol/{name}` | $0.002/call | High (detailed) |
| `/api/rwa` | $0.003/call | Niche |
| `/api/compare` | $0.002/call | Medium |
| `/api/risk` | $0.005/call | Premium |

**Estimated revenue:** $50-500/month depending on traffic

## Quick Start

```bash
pip install aiohttp
python scripts/starknet_yield_agent.py
```

## API Endpoints

### FREE: Market Summary
```bash
curl https://api.example.com/api/yields-summary
```
Returns: Total TVL, protocol count, average APY

### PAID: Top Yields
```bash
curl https://api.example.com/api/top-yields?limit=10
curl -H "X-Payment-Proof: <proof>"  # x402 header
```
Returns: Top yielding pools sorted by APY

### PAID: Protocol Details
```bash
curl https://api.example.com/api/protocol/Ekubo
```
Returns: Deep dive on specific protocol

### PAID: Risk Analysis
```bash
curl https://api.example.com/api/risk
```
Returns: Risk-adjusted yields, portfolio suggestions

## Web Dashboard

```bash
curl https://api.example.com/dashboard
```

## Deployment

### Docker
```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "scripts/starknet_yield_agent.py"]
```

### Railway
1. Connect GitHub repo
2. Set PORT environment variable
3. Deploy

### x402 Integration

For full x402 payment support, integrate with:
- [Lucid Agents SDK](https://github.com/langoustine69/lucid-agents)
- x402 protocol for micropayments
- Lightning Network or USDC payments

## Pricing Strategy

| Tier | Calls/month | Revenue |
|------|-------------|---------|
| Casual | 1,000 | ~$10 |
| Active | 10,000 | ~$100 |
| Pro | 100,000 | ~$1,000 |

## Files

```
starknet-yield-agent/
├── SKILL.md              # This file
├── README.md             # User guide
├── Dockerfile           # Container
├── requirements.txt     # Python deps
└── scripts/
    ├── starknet_yield_agent.py  # Main server
    └── x402_integration.py      # Payment integration
```

## Comparison with langoustine69 Agents

| Feature | This Agent | Langoustine69 |
|---------|-----------|--------------|
| Network | Starknet | Multi-chain |
| Runtime | Python | TypeScript/Bun |
| Payments | Mock x402 | Full x402 |
| DeFi Data | Mock | Real-time |

## Future Enhancements

1. Real-time data from DEXs
2. Full x402 payment integration
3. Subscription tiers
4. WebSocket for live alerts
5. Mobile app integration
