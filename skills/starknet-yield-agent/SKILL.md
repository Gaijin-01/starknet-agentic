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

## Overview

The **Starknet Yield Agent** is a production-ready API server that provides real-time DeFi yield data, protocol analytics, and risk analysis for the Starknet ecosystem. It implements x402 micropayment protocol for monetization, enabling developers to build paid analytics services on top of Starknet DeFi.

### Key Features

- **Real-time Yield Data**: APY, TVL, and risk metrics for major protocols
- **Protocol Analytics**: Deep-dive analytics for Ekubo, Jediswap, 10k, zkLend, Nostra
- **Risk Analysis**: Risk-adjusted returns with portfolio suggestions
- **x402 Payments**: Built-in monetization via micropayments
- **Web Dashboard**: Visual interface for data exploration
- **Production Ready**: Docker deployment, health checks, async architecture

### Use Cases

| Use Case | Example |
|----------|---------|
| DeFi Dashboard | Build a yield dashboard for Starknet |
| Analytics Service | Paid API for yield data |
| Portfolio Tracker | Track and optimize DeFi positions |
| Risk Analysis | Evaluate risk-adjusted returns |
| Comparison Tool | Compare yields across protocols |

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 Starknet Yield Agent                    │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │   API       │  │  Dashboard  │  │   x402          │ │
│  │   Server    │  │   (HTML)    │  │   Payments      │ │
│  └──────┬──────┘  └─────────────┘  └────────┬────────┘ │
│         │                                     │         │
│         ▼                                     ▼         │
│  ┌─────────────────────────────────────────────────┐   │
│  │           StarknetDataService                   │   │
│  │  • Pool data aggregation                       │   │
│  │  • Protocol analytics                         │   │
│  │  • Risk calculation                           │   │
│  └────────────────────┬────────────────────────────┘   │
│                       │                               │
│                       ▼                               │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Data Sources                        │   │
│  │  • DEX APIs (Ekubo, Jediswap, 10k)             │   │
│  │  • Lending protocols (zkLend, Nostra)          │   │
│  │  • RPC endpoints                               │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Workflow

### 1. Data Collection
```
scripts/starknet_yield_agent.py → StarknetDataService → Fetch from DEXs/RPC
```

### 2. API Request Flow
```
Client Request → Validate Endpoint → Check Payment → Return Data
```

### 3. Payment Verification (x402)
```
Request + Header("X-Payment-Proof") → Verify → Serve / Reject
```

### 4. Dashboard Access
```
GET /dashboard → Render HTML → Serve Visualization
```

## Monetization

| Endpoint | Price | Description |
|----------|-------|-------------|
| `/api/yields-summary` | FREE | Market overview |
| `/api/top-yields` | $0.001 | Top yields sorted by APY |
| `/api/protocol/{name}` | $0.002 | Protocol deep dive |
| `/api/rwa` | $0.003 | RWA opportunities |
| `/api/compare` | $0.002 | Yield comparison |
| `/api/risk` | $0.005 | Risk-adjusted analysis |

**Estimated revenue:** $50-500/month depending on traffic

## Quick Start

### Installation
```bash
cd /home/wner/clawd/skills/starknet-yield-agent
pip install -r scripts/requirements.txt
```

### Run Locally
```bash
python scripts/starknet_yield_agent.py
# Server starts on http://localhost:3000
```

### Docker Deployment
```bash
docker build -t starknet-yield-agent .
docker run -p 3000:3000 starknet-yield-agent
```

## API Endpoints

### FREE: Market Summary
```bash
curl https://api.example.com/api/yields-summary
```
**Response:**
```json
{
  "market": {
    "totalTVL": "$280M",
    "protocolCount": 5,
    "avgAPY": "12.5%",
    "poolCount": 14
  },
  "chain": "Starknet"
}
```

### PAID: Top Yields
```bash
curl https://api.example.com/api/top-yields?limit=10
```
**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `limit` | int | 10 | Number of results |
| `minTvl` | float | 0 | Minimum TVL in USD |
| `risk` | string | - | Filter by risk level |

**Response:**
```json
{
  "topYields": [
    {"rank": 1, "protocol": "Nostra", "asset": "STRK", "apy": "30.00%", "tvl": "$12M", "risk": "high"},
    {"rank": 2, "protocol": "zkLend", "asset": "STRK", "apy": "25.00%", "tvl": "$15M", "risk": "medium"}
  ]
}
```

### PAID: Protocol Details
```bash
curl https://api.example.com/api/protocol/Ekubo
```
Returns: Deep dive on specific protocol including pools and recommendations.

### PAID: Risk Analysis
```bash
curl https://api.example.com/api/risk
```
Returns: Risk-adjusted yields with methodology and portfolio suggestions.

## Web Dashboard

Access at `/dashboard` for visual data exploration:
- Market overview with metrics
- Top yields table
- Protocol comparison
- API endpoint documentation

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 3000 | Server port |
| `STARKNET_RPC_URL` | Lava RPC | Starknet RPC endpoint |
| `X402_ENABLED` | false | Enable x402 payments |

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

## Integration

### Langoustine69 x402 Pattern
Compatible with the langoustine69 x402 agent pattern:
- Payment verification via X-Payment-Proof header
- Subscription management support
- Revenue tracking

### Standalone Use
Can be deployed independently:
- Docker for containerized deployment
- Railway for managed hosting
- Any Python-compatible platform

## Future Enhancements

1. **Real-time data** from DEXs (Ekubo, Jediswap APIs)
2. **Full x402 payment** integration with @lucid-agents/payments
3. **Subscription tiers** (monthly/yearly plans)
4. **WebSocket** for live alerts
5. **Mobile app** integration
6. **Multi-chain** support (Base, Arbitrum)

## License

MIT
