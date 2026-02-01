# Arbitrage Signal Skill

Signal-based arbitrage scanner for Starknet DEXs. Scans for price differences and alerts you — you decide whether to trade.

## Overview

A lightweight arbitrage scanner that:
- Monitors prices across Ekubo, Jediswap, and 10k
- Detects cross-DEX price differences
- Sends Telegram alerts with opportunity details
- **You execute trades manually** — no autonomous trading

## When to Use

- When you want arbitrage signals without giving bot trading access
- When you prefer manual approval for each trade
- When testing strategies before scaling

## Features

### Price Monitoring
- Real-time price fetching from CoinGecko + simulated DEX spreads
- Multi-pair tracking: ETH, STRK, USDC, USDT, WBTC, LINK
- 15-minute scanning interval

### Signal Generation
- Calculates profit potential for each opportunity
- Shows gas costs and net profit
- Confidence scoring for each signal

### Telegram Alerts
- Rich format with emoji indicators
- Shows profit in USD and percentage
- Includes trade path and DEX comparison

## Files

```
arbitrage-signal/
├── SKILL.md           # This file
├── scripts/
│   ├── arbitrage_signal.py   # Main scanner
│   ├── config.py             # Configuration
│   └── crontab.sh            # Cron setup
└── requirements.txt
```

## Quick Start

### Installation
```bash
cd /home/wner/clawd/skills/arbitrage-signal
pip install -r requirements.txt
```

### Configuration
Edit `.env`:
```bash
# Telegram
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Thresholds
ARBITRAGE_MIN_PROFIT=0.3  # Minimum profit %
ARBITRAGE_MIN_USD=1.0     # Minimum profit in USD
```

### Run Manually
```bash
python scripts/arbitrage_signal.py
```

### Setup Cron (auto-scan every 15 min)
```bash
./scripts/crontab.sh
```

## Signal Format

Example Telegram alert:

```
💰 ARBITRAGE SIGNAL
━━━━━━━━━━━━━━━━━━━━
📈 PROFIT: $2.50 (0.35%)
📊 CONFIDENCE: 78%
💸 Gas Est.: $0.15

🔄 PATH
Ekubo: ETH/USDC = $2522.30
Jediswap: ETH/USDC = $2520.50
Spread: 0.07%

🎯 ACTION
Buy 0.01 ETH on Jediswap
Sell 0.01 ETH on Ekubo
Net: +$2.35
```

## How It Works

```
1. Fetch prices from CoinGecko (base prices)
2. Apply simulated DEX spreads
3. Compare prices across DEXs
4. Calculate arbitrage profit
5. Filter by min profit threshold
6. Send Telegram alert if opportunity found
```

## Trading Strategy

### Step 1: Receive Alert
Telegram notification with opportunity details

### Step 2: Verify
- Check prices manually on DEXs
- Ensure spread is still available
- Estimate actual gas costs

### Step 3: Execute
1. Approve tokens on source DEX
2. Swap on source DEX
3. Approve on target DEX
4. Swap on target DEX
5. Calculate net profit

### Step 4: Report Back
Send result to bot for tracking (optional)

## Pairs Tracked

| Pair | DEXes |
|------|-------|
| ETH/USDC | Ekubo, Jediswap, 10k |
| STRK/ETH | Ekubo, Jediswap, 10k |
| STRK/USDC | Ekubo, Jediswap, 10k |
| ETH/USDT | Ekubo, Jediswap, 10k |
| WBTC/ETH | Ekubo, Jediswap, 10k |
| LINK/ETH | Ekubo, Jediswap, 10k |

## Limitations

1. **Simulated spreads** — Uses CoinGecko + small spread simulation
2. **No real contract reads** — Would require starknet.py for live data
3. **No execution** — Signals only, manual trading required
4. **Timing risk** — Prices change between signal and execution

## Future Enhancements

- Direct RPC price fetching from DEX contracts
- Real-time spread calculation
- Historical profitability tracking
- Multiple chain support (Arbitrum, Base)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No alerts | Check TELEGRAM_CHAT_ID |
| Stale prices | Verify CoinGecko API |
| False signals | Increase ARBITRAGE_MIN_PROFIT |

## License

MIT — See LICENSE file

---

**Version:** 1.0.0  
**Last Updated:** 2026-02-01  
**Author:** Clawd / Sefirot
