# Starknet Yield Agent (TypeScript)

Autonomous agent for finding and executing DeFi yield opportunities on Starknet.

## Overview

This agent monitors Starknet DeFi protocols (Ekubo, Jediswap, 10k, zkLend, Nostra) to find optimal yield opportunities and can optionally execute strategies.

## Features

- Real-time yield monitoring across protocols
- Risk-adjusted opportunity scoring
- Automated strategy execution (optional)
- Performance tracking and reporting

## Usage

```typescript
import { YieldAgent } from './src/agent';

const agent = new YieldAgent({
  rpcUrl: process.env.STARKNET_RPC_URL,
  privateKey: process.env.PRIVATE_KEY,
  riskTolerance: 'medium',
  autoExecute: false,
});

await agent.scan({
  protocols: ['ekubo', 'jediswap', 'zkLend'],
  minAPY: 5,
  maxTVL: 1000000,
});

const opportunities = agent.getOpportunities();
console.table(opportunities);
```

## Scripts

```bash
# Scan for opportunities
npm run scan

# Execute best strategy
npm run execute -- --strategy best-apy

# Report performance
npm run report -- --days 30
```

## Dependencies

- starknet.js ^6.0.0
- axios
- @avnu/avnu-sdk

## Configuration

```bash
# Environment variables
STARKNET_RPC_URL=https://rpc.starknet.lava.build
PRIVATE_KEY=your_private_key
RISK_TOLERANCE=low|medium|high
AUTO_EXECUTE=false
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No opportunities found | Check RPC connectivity, increase `minAPY` threshold |
| Transaction failed | Verify wallet balance, check gas settings |
| Low yield display | Ensure pool data is fresh, try different protocols |

## Version

**v1.0.0** (2026-02-01) - Initial TypeScript implementation

## License

MIT
