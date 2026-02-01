# 🚀 Production Deployment Guide

## Overview

Two x402-enabled API agents ready for Vercel deployment:
1. **starknet-yield-agent** - DeFi yields and protocol analytics
2. **ct-intelligence-agent** - Crypto Twitter intelligence

Both use HTTP 402 payment protocol with free tiers.

---

## Quick Deploy (5 minutes)

### Prerequisites
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login
```

### Deploy Agent 1: Starknet Yield
```bash
cd skills/starknet-yield-agent-ts
npm install
vercel --prod
```

### Deploy Agent 2: CT Intelligence
```bash
cd skills/ct-intelligence-agent-ts
npm install
vercel --prod
```

---

## API Endpoints

### Starknet Yield Agent

| Endpoint | Price | Description |
|----------|-------|-------------|
| `GET /api/market-summary` | FREE | Market overview, TVL, avg APY |
| `GET /api/top-yields` | $0.001 | Top pools sorted by APY |
| `GET /api/protocol/:name` | $0.002 | Protocol deep dive |
| `GET /api/rwa` | $0.003 | RWA opportunities |
| `GET /api/compare/:asset` | $0.002 | Cross-protocol yield compare |
| `GET /api/risk-analysis` | $0.005 | Risk-adjusted analysis |
| `GET /.well-known/agent.json` | FREE | Agent manifest |

### CT Intelligence Agent

| Endpoint | Price | Description |
|----------|-------|-------------|
| `GET /api/overview` | FREE | Sentiment + top hashtags |
| `GET /api/trending` | $0.001 | Full trending hashtags |
| `GET /api/influencers` | $0.002 | Top influencer analysis |
| `GET /api/sentiment` | $0.002 | Deep sentiment analysis |
| `GET /api/narratives` | $0.003 | Active narratives |
| `GET /api/alpha` | $0.005 | Smart money alpha |
| `GET /api/full-report` | $0.01 | Complete intelligence report |
| `GET /.well-known/agent.json` | FREE | Agent manifest |

---

## Payment Integration (x402)

### How Payments Work

1. Client requests paid endpoint without payment
2. Server returns HTTP 402 with payment details:
```json
{
  "error": "Payment Required",
  "x402": {
    "version": "1",
    "accepts": [{
      "scheme": "exact",
      "network": "base-sepolia",
      "maxAmountRequired": "1000",
      "payTo": "0xAc7a6258252c29A7c127f98d530DBc244bB7D495",
      "facilitator": "https://x402.org/facilitator"
    }]
  }
}
```

3. Client pays via facilitator
4. Client retries with `x-payment` header
5. Server verifies and returns data

### Current Config (Testnet)
- **Network:** base-sepolia
- **Address:** 0xAc7a6258252c29A7c127f98d530DBc244bB7D495
- **Facilitator:** https://x402.org/facilitator

### Production Config (Mainnet)
Update `vercel.json` env vars:
```json
{
  "env": {
    "NETWORK": "base",
    "PAYMENTS_RECEIVABLE_ADDRESS": "YOUR_MAINNET_ADDRESS",
    "FACILITATOR_URL": "https://x402.org/facilitator"
  }
}
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PAYMENTS_RECEIVABLE_ADDRESS` | Your wallet address | Set in vercel.json |
| `NETWORK` | Payment network | base-sepolia |
| `FACILITATOR_URL` | x402 facilitator | https://x402.org/facilitator |

---

## Testing

### Local Development
```bash
cd skills/starknet-yield-agent-ts
npm install
npx vercel dev
```

### Test Endpoints
```bash
# Free endpoint
curl http://localhost:3000/api/market-summary

# Paid endpoint (will return 402)
curl http://localhost:3000/api/top-yields

# Agent manifest
curl http://localhost:3000/.well-known/agent.json
```

---

## Revenue Projections

| Scenario | Calls/Month | Revenue |
|----------|-------------|---------|
| Conservative | 2,000 | $250 |
| Moderate | 20,000 | $2,500 |
| Aggressive | 200,000 | $25,000 |

---

## Production Checklist

- [ ] Deploy to Vercel
- [ ] Update to mainnet payment address
- [ ] Set up monitoring (Vercel Analytics)
- [ ] Register on x402 agent directory
- [ ] Promote on CT (@sefirotwatch)
- [ ] Add real-time data APIs (DeFiLlama, CoinGecko)

---

## Monitoring

After deployment, monitor at:
- Vercel Dashboard: https://vercel.com/dashboard
- x402 Facilitator: https://x402.org/dashboard (if available)

---

## Support

- Agent Docs: `SKILL.md` in each project
- x402 Protocol: https://x402.org
- Lucid Agents: https://github.com/daydreamsai/lucid-agents
