# 🐋 Starknet Whale Tracker

Real-time whale monitoring and arbitrage detection for Starknet.

## Features

- **Whale Tracking**: Monitor 12+ known whale addresses
- **Mempool Monitoring**: Real-time pending transaction detection
- **Arbitrage Detection**: Cross-DEX price comparison
- **Telegram Alerts**: Instant notifications

## Quick Start with Docker

### 1. Setup
```bash
cd starknet-whale-tracker
cp .env.example .env
# Edit .env with your settings
```

### 2. Build & Run
```bash
# Build image
docker-compose build

# Run API server
docker-compose up -d whale-tracker

# Run enhanced tracker
docker-compose up -d whale-tracker-enhanced

# Run cron (every 15 min)
docker-compose up -d whale-cron
```

### 3. Check Status
```bash
docker logs starknet-whale-tracker
docker-compose ps
```

## Without Docker

```bash
pip install -r requirements.txt
python scripts/check.py
python scripts/api.py --port 8080
```

## Commands

```bash
# List whales
python scripts/whales_real.py

# Quick check
python scripts/check.py

# API server
python scripts/api.py --port 8080

# Enhanced tracker
python scripts/tracker_enhanced.py
```

## Files

```
starknet-whale-tracker/
├── Dockerfile              # Docker image
├── docker-compose.yml      # Docker services
├── .env.example            # Environment template
├── requirements.txt        # Python deps
├── SKILL.md               # Skill documentation
├── data/                  # Database storage
└── scripts/
    ├── whales_real.py     # Whale database (12+ addresses)
    ├── mempool_ws.py      # Mempool monitoring
    ├── dex_prices.py      # Direct DEX price fetcher
    ├── arbitrage.py       # Arbitrage detection
    ├── tracker_enhanced.py # Enhanced tracker
    ├── check.py           # Quick check script
    ├── api.py             # REST API
    └── cli.py             # CLI interface
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `STARKNET_RPC_URL` | Yes | RPC endpoint (Lava is free) |
| `TELEGRAM_BOT_TOKEN` | No | Telegram bot token |
| `TELEGRAM_CHAT_ID` | No | Telegram chat ID |
| `AVNU_API_KEY` | No | AVNU API key for DeFi features |

## Architecture

```
┌─────────────────────────────────────┐
│         Whale Tracker               │
├─────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐        │
│  │  Whales  │  │ Mempool  │        │
│  │ Database │  │ Monitor  │        │
│  └──────────┘  └──────────┘        │
│         │              │            │
│         ▼              ▼            │
│  ┌─────────────────────────────────┤
│  │     Arbitrage Scanner           │
│  │  (DEX price comparison)         │
│  └─────────────────────────────────┤
│                   │                 │
│                   ▼                 │
│  ┌─────────────────────────────────┐
│  │     Telegram Alerts / API       │
│  └─────────────────────────────────┘
└─────────────────────────────────────┘
```

## Rate Limits

- **Lava RPC**: Free tier available
- **AVNU API**: 300 req/5min (public)
- **CoinGecko**: ~333 req/min (free tier)

## Whales Tracked

| Category | Count | Examples |
|----------|-------|----------|
| Foundation | 3 | Starknet Foundation, STRK Token |
| Protocols | 6 | Ekubo, Jediswap, 10k |
| Smart Money | 1 | CT-tracked traders |
| Exchange | 1 | CEX hot wallets |

## License

MIT
