# Starknet Intelligence Colony v1.0.2

**Version:** 1.0.2 | **Last Updated:** 2026-01-28

## Overview

## Overview

Starknet Intelligence Colony is an autonomous multi-agent system designed to monitor, analyze, and report on the Starknet DeFi ecosystem. It combines real-time market data, deep research capabilities, and automated content generation.

## Agents

### Market Intelligence Agent
Monitors real-time market conditions:
- Token prices from CoinGecko API
- Arbitrage opportunities across DEXs
- Total Value Locked (TVL) tracking
- Whale movement detection

### Research Agent
Conducts deep protocol analysis:
- Protocol security audits
- Token metrics and fundamentals
- Competitive analysis
- Investment opportunity identification

### Content Agent
Generates automated content:
- Hourly intelligence reports
- Twitter-ready threads
- Analysis articles
- Multi-platform formatting

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Orchestrator                             │
│              (manages agent lifecycle)                      │
└─────────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│   Market      │ │   Research    │ │   Content     │
│   Agent       │ │   Agent       │ │   Agent       │
└───────────────┘ └───────────────┘ └───────────────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          ▼
              ┌───────────────────────┐
              │    Shared State       │
              │  (inter-agent comms)  │
              └───────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │      Dashboard        │
              │   (web interface)     │
              └───────────────────────┘
```

## Usage

### Basic Run
```bash
python3 skills/colony/main.py
```

### Run Dashboard Only
```bash
python3 skills/colony/dashboard/app.py
```

### Run Scheduled Reports
```bash
python3 skills/colony/cron_integration.py
```

## Configuration

All configuration is in `config.py`:
- API keys and endpoints
- Monitoring intervals
- Report schedules
- Alert thresholds
- Dashboard settings

## Reports

Reports are generated in `skills/colony/reports/`:
- `market_YYYYMMDD_HHMM.json` - Market data
- `whale_YYYYMMDD_HHMM.json` - Whale activity
- `research_YYYYMMDD_HHMM.json` - Deep research
- `content_YYYYMMDD_HHMM.json` - Generated content

## API Integrations

- **CoinGecko**: Token prices and market data
- **Ekubo**: DEX data and liquidity
- **Starkscan**: On-chain data
- **Web Search**: Research and news

## Features

✅ Real-time market monitoring  
✅ Arbitrage detection  
✅ TVL tracking  
✅ Whale movement alerts  
✅ Protocol research  
✅ Automated content generation  
✅ Web dashboard  
✅ Dark mode UI  
✅ Mobile-friendly  

## Development

### Adding New Agents
1. Create agent in `agents/`
2. Register in `orchestrator.py`
3. Add tests in `tests/`

### Adding New Data Sources
1. Create client in `clients/`
2. Update `shared_state.py` schema
3. Add to relevant agent

## Dependencies

See `requirements.txt` for full list:
- aiohttp - Async HTTP
- aiofiles - Async file I/O
- Flask - Web dashboard
- python-dotenv - Config management

## Troubleshooting

### Common Issues

**API Rate Limits**
- CoinGecko has rate limits (~10-50 calls/min for free tier)
- Reduce `api_request_delay` in config.py for slower but more reliable requests
- Consider upgrading to paid API plan for production use

**Dashboard Not Loading**
- Check if Flask is running: `ps aux | grep flask`
- Verify port 5000 is not in use: `lsof -i :5000`
- Check logs in `dashboard/app.log` for errors

**No Market Data**
- Verify API keys in `.env` are valid
- Check internet connectivity: `curl -s https://api.coingecko.com/ping`
- Review `config.py` for correct endpoint URLs

**Memory Issues with Long Runs**
- Clear reports directory periodically: `rm skills/colony/reports/*.json`
- Restart agents every 24h via cron for long-term operation

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-23 | Initial release with Market, Research, Content agents |
| 1.0.1 | 2026-01-25 | Added dashboard, improved whale tracking |
| 1.0.2 | 2026-01-28 | Enhanced arbitrage detection, added cron integration |

## License

MIT
