# 🦞 Starknet Yield Agent v2.0

x402-compatible API for Starknet DeFi yields with **real-time data from AVNU**.

## Data Sources

- **AVNU API** - Swap quotes, DCA orders, market data
- **CoinGecko** - Token prices (ETH, STRK, USDC, USDT)
- **DEX APIs** - Pool TVL and APR data

## API Endpoints

| Endpoint | Price | Description |
|----------|-------|-------------|
| `/api/market-summary` | FREE | TVL, APY, prices |
| `/api/top-yields` | $0.001 | Top pools by APY |
| `/api/protocol/:name` | $0.002 | Protocol deep dive |
| `/api/risk-analysis` | $0.005 | Risk-adjusted yields |

## Deployment

```bash
# Deploy to Vercel (with AVNU integration)
cd skills/starknet-yield-agent-ts
vercel --prod
```

## Configuration

Optional environment variables:
- `AVNU_API_KEY` - For higher rate limits (get at https://portal.avnu.fi)
- `PAYMENTS_RECEIVABLE_ADDRESS` - Your wallet for x402 payments

## Data Coverage

**7 Protocols Tracked:**
- Ekubo (AMM) - $97M TVL
- zkLend (Lending) - $107M TVL
- Nostra (Lending) - $125M TVL
- Jediswap (AMM) - $56M TVL
- 10k (AMM) - $40M TVL
- SithSwap (AMM) - $46M TVL
- Fibrous (AMM) - $48M TVL

**Total TVL:** ~$519M

## Payment Address

`0xAc7a6258252c29A7c127f98d530DBc244bB7D495`

## Based on

- [langoustine69/x402-pattern](https://github.com/langoustine69)
- [AVNU API](https://docs.avnu.fi)
- [Lucid Agents SDK](https://github.com/langoustine69/lucid-agents)
