# Starknet Intelligence Colony

A powerful autonomous multi-agent system that monitors Starknet DeFi, discovers opportunities, and generates intelligent reports.

## 🧠 What is the Colony?

The Colony is a network of specialized AI agents working together:

- **Market Agent** - Real-time price monitoring, arbitrage detection, TVL tracking
- **Research Agent** - Deep protocol analysis, security audits, competitive research
- **Content Agent** - Generates reports, Twitter threads, analysis articles

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r skills/colony/requirements.txt

# Run the colony
python3 skills/colony/main.py

# Run dashboard only
python3 skills/colony/dashboard/app.py

# Run scheduled reports
python3 skills/colony/cron_integration.py
```

## 📁 Structure

```
skills/colony/
├── main.py              # Entry point
├── orchestrator.py      # Agent coordination
├── shared_state.py      # Inter-agent communication
├── config.py            # Configuration
├── agents/
│   ├── market_agent.py   # Market intelligence
│   ├── research_agent.py # Deep research
│   └── content_agent.py  # Content generation
├── clients/
│   ├── coingecko_client.py  # CoinGecko API
│   ├── ekubo_client.py      # Ekubo DEX API
│   └── whale_db_client.py   # Whale tracking
├── dashboard/           # Web dashboard
├── reports/             # Generated reports
└── tests/               # Tests
```

## 🔧 Configuration

Edit `config.py` to customize:
- API keys (CoinGecko, etc.)
- Monitoring intervals
- Report schedules
- Alert thresholds

## 📊 Features

### Market Intelligence
- Real-time Starknet token prices
- Arbitrage opportunity detection (Ekubo, JediSwap, mySwap)
- TVL and volume tracking across protocols
- Large whale movement detection

### Research Capabilities
- Protocol deep-dive analysis
- Security audit reviews
- Competitive landscape mapping
- Investment thesis generation

### Content Generation
- Hourly intelligence briefs
- Twitter-ready thread generation
- Multi-platform formatting
- Sentiment analysis integration

## 🛠️ Available Reports

| Report | Schedule | Description |
|--------|----------|-------------|
| Market Intelligence | Hourly | Prices, arbitrage, TVL |
| Whale Activity | Hourly | Large transfers |
| Research Brief | Daily | Deep protocol analysis |
| Content Pack | Hourly | Twitter threads, posts |

## 🔒 Security

- All API keys stored in environment variables
- Rate limiting on all external APIs
- Input validation on all data
- Error handling and graceful degradation

## 📝 License

MIT License - Built with ❤️ for the Starknet community
