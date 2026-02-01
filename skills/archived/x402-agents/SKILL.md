# x402 Agents

x402 payment protocol integration for Starknet agents.

## Overview

x402 is a micropayment standard for API access and agent services. This skill enables agents to:
- Pay for API access using x402
- Monetize agent capabilities via x402
- Handle subscription models

## Features

- x402 payment verification
- Subscription management
- Rate limiting based on payments
- Revenue tracking

## Usage

```typescript
import { x402Client, x402Server } from './src/x402';

// Client: Pay for API access
const client = new x402Client({
  payer: account.address,
  policy: { callsPerMinute: 100 },
});

const response = await client.request('https://api.example.com/data', {
  payment: { amount: '0.001', token: 'STRK' },
});

// Server: Monetize agent API
const server = new x402Server({
  pricePerCall: '0.0001',
  acceptedTokens: ['STRK', 'ETH'],
});

await server.start(3000);
```

## Scripts

```bash
# Start payment server
npm run server

# Test client payments
npm run test-payments

# Revenue dashboard
npm run dashboard
```

## Dependencies

- starknet.js ^6.0.0
- express
- @x402/sdk

## Configuration

```bash
# Environment variables
X402_PORT=3000
PRICE_PER_CALL=0.0001
ACCEPTED_TOKENS=STRK,ETH
PAYMENT_VERIFIER=starknet
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Payment not verified | Check payment proof format, verify signature |
| Rate limiting triggered | Upgrade subscription or wait |
| Token not accepted | Add token to `ACCEPTED_TOKENS` |

## Version

**v1.0.0** (2026-02-01) - Initial x402 payment gateway

## License

MIT
