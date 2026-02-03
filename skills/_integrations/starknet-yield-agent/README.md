# Starknet Yield Agent

Real-time DeFi yields and analytics API with x402 micropayment support.

## Quick Start

```bash
pip install -r scripts/requirements.txt
python scripts/starknet_yield_agent.py
```

## Docker

```bash
docker build -t starknet-yield-agent .
docker run -p 3000:3000 starknet-yield-agent
```

## Environment

```bash
PORT=3000
STARKNET_RPC_URL=https://rpc.starknet.lava.build:443
X402_ENABLED=false
```

## API

```
GET /api/yields-summary  - FREE market overview
GET /api/top-yields    - Top yields ($0.001)
GET /api/protocol/{name} - Protocol details ($0.002)
GET /api/rwa           - RWA opportunities ($0.003)
GET /api/compare       - Yield comparison ($0.002)
GET /api/risk          - Risk analysis ($0.005)
```

## Dashboard

Open http://localhost:3000/dashboard
