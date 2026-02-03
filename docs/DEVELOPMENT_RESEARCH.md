# Skills Development Research

Research findings for setting up real integrations for the 5 core skills.

## 1. Starknet DEX APIs

### Ekubo Protocol
- **Website**: https://app.ekubo.org/
- **Type**: Uniswap V3-style concentrated liquidity AMM on Starknet
- **API**: REST API for swaps, positions, and liquidity data
- **Features**: 
  - Swap API with real-time pricing
  - Position management
  - Liquidity pool statistics
  - ERC-4626 vault support
- **Documentation**: https://docs.ekubo.org/

### Jediswap
- **Website**: https://jediswap.xyz/
- **Type**: AMM DEX on Starknet
- **API**: GraphQL and REST endpoints
- **Features**:
  - Swap functionality
  - Pool reserves
  - Token pair data
- **Note**: One of the earliest and most established DEXs on Starknet

### 10kSwap
- **Website**: https://10kswap.com/
- **Type**: AMM DEX working in tandem with Ethereum
- **Features**:
  - Cross-chain capabilities
  - Standard swap and liquidity operations
- **Status**: One of top 5 DEXs by TVL on Starknet

### AVNU
- **Website**: https://app.avnu.fi/
- **Type**: DEX aggregator on Starknet
- **Features**:
  - Multi-route swaps for best rates
  - Integration with multiple DEXs
  - Real-time quote API

### Recommendation
For whale tracking and arbitrage:
- **Primary**: Ekubo (most active, Uniswap V3 model)
- **Secondary**: AVNU (aggregator for best prices)
- **Data sources**: Jediswap, 10kSwap for cross-validation

---

## 2. Price Feed APIs

### CoinGecko API (Recommended for general crypto)
- **Website**: https://www.coingecko.com/en/api
- **Pricing**: Free tier available, paid plans from $100+/month
- **Key Features**:
  - RESTful JSON endpoints
  - WebSocket API for real-time streaming (paid plans)
  - 250+ blockchain networks
  - 1,700+ DEXes, 15M+ tokens
  - Historical data, OHLCV, trades
- **Endpoints**:
  - `/simple/price` - Live prices
  - `/coins/markets` - Market data
  - `/coins/{id}/market_chart` - Historical data
- **Rate Limits**: 10-50 calls/minute (free tier)

### Chainlink Price Feeds
- **Website**: https://docs.chain.link/data-feeds/price-feeds
- **Type**: Decentralized oracle network
- **Key Features**:
  - Aggregated from multiple data sources
  - Independent node operators
  - Enterprise-grade reliability (99.9% uptime)
  - On-chain data feeds (smart contract integration)
- **Use Case**: Best for DeFi protocols needing on-chain verified prices
- **Assets**: Major crypto pairs, commodities, forex

### Pyth Network
- **Website**: https://pyth.network/
- **Type**: Low-latency price oracle
- **Key Features**:
  - Sub-second price updates
  - Institutional-grade data sources
  - High-frequency trading support
  - 50+ blockchain networks
- **Use Case**: Trading applications requiring real-time prices

### Recommendation
- **Primary**: CoinGecko (comprehensive, easy to use)
- **On-chain verification**: Chainlink or Pyth
- **Free tier**: CoinGecko sufficient for development

---

## 3. Web Search APIs

### Brave Search API
- **Website**: https://brave.com/search/api/
- **Pricing**: 2,000 queries/month free, paid plans available
- **Key Features**:
  - Independent index (not Google/Bing dependent)
  - Privacy-first (no user tracking)
  - Comprehensive coverage (billions of pages)
  - Web, news, images, videos search
  - 99.9% uptime, low latency
- **API Docs**: https://api-dashboard.search.brave.com/app/documentation
- **Rate Limits**: 20 queries/second (paid)

### Tavily
- **Website**: https://www.tavily.com/
- **Pricing**: 1,000 credits/month free
- **Key Features**:
  - Specialized for AI/LLM applications
  - Search + extraction in single API
  - Content relevance optimization
  - Real-time search and crawling
- **Use Case**: AI agents needing targeted, relevant results
- **Docs**: https://docs.tavily.com/

### Serper (Google/SerpAPI alternative)
- **Website**: https://serper.dev/
- **Pricing**: Pay-as-you-go
- **Key Features**:
  - Google Search API access
  - Fast responses
  - Easy integration
- **Note**: Dependent on Google's index

### Recommendation
- **Primary**: Brave Search (independent index, privacy-focused)
- **AI-optimized**: Tavily (better content extraction)
- **Backup**: Serper (Google results when needed)

---

## 4. Multi-Agent Collaboration Frameworks

### LangGraph
- **Website**: https://langchain-ai.github.io/langgraph/
- **Type**: Graph-based workflow orchestration
- **Best For**: Complex, stateful multi-step processes
- **Key Features**:
  - State graph architecture
  - Cycle support (iterative reasoning)
  - LangChain integration
  - Strict output format enforcement
  - DAG support
- **Pros**:
  - Excellent state management
  - Seamless LangChain ecosystem integration
  - Strong tooling support
- **Cons**: Steeper learning curve, verbose code
- **Use Case**: Complex agent workflows with cycles

### CrewAI
- **Website**: https://crewai.com/
- **Type**: Role-based agent orchestration
- **Best For**: Structured team collaboration with defined roles
- **Key Features**:
  - "Crews" and "Flows" architecture
  - Role-based agent definitions
  - Built-in memory management
  - Easy setup and quick startup
- **Pros**:
  - Simple to start
  - Clear agent role definitions
  - Good memory concepts
- **Cons**: Poor logging/debugging, harder to scale
- **Use Case**: Simple multi-agent tasks with clear roles

### AutoGen
- **Website**: https://microsoft.github.io/autogen/
- **Type**: Conversational agent framework
- **Best For**: Flexible, conversational interactions
- **Key Features**:
  - Conversational collaboration
  - Highly extensible
  - Strong tooling support
  - No built-in DAG (procedural orchestration)
- **Pros**:
  - Great flexibility and control
  - Excellent for complex custom workflows
  - Strong model support
- **Cons**: Manual orchestration required, code complexity grows
- **Use Case**: Dynamic conversations between agents

### Comparison Summary

| Feature | LangGraph | CrewAI | AutoGen |
|---------|-----------|--------|---------|
| **Architecture** | Graph-based | Role-based | Conversational |
| **State Management** | Excellent | Good | Manual |
| **Learning Curve** | Medium | Easy | Medium-Hard |
| **LangChain Integration** | Native | Via LangChain | Via LangChain |
| **Logging/Debugging** | Good | Poor | Good |
| **Scalability** | High | Medium | High |
| **Best For** | Complex workflows | Simple teams | Dynamic conversations |

### Recommendation for This Project
- **Primary**: LangGraph (best for structured, iterative workflows)
- **Alternative**: CrewAI (if simpler role-based approach needed)
- **Integration**: Moltbot's sub-agent system can work alongside any framework

---

## 5. Skill Architecture Best Practices

### Core Principles
1. **Single Responsibility**: Each skill does one thing well
2. **Clear Interfaces**: Defined inputs/outputs for each skill
3. **Error Handling**: Graceful degradation on API failures
4. **Configuration over Code**: Environment variables for API keys
5. **Observability**: Logging, metrics, and alerts

### Recommended Structure

```
skills/
  {skill-name}/
    SKILL.md          # Skill definition
    config.yaml       # Configuration
    main.py           # Entry point
    api/              # API integrations
      client.py       # API client
    tools/            # Tool definitions
    tests/            # Unit tests
    scripts/          # CLI tools
    requirements.txt  # Dependencies
```

### Integration Patterns

**For DEX/Price APIs:**
```python
class PriceClient:
    def __init__(self, api_key: str):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.headers = {"x-cg-api-key": api_key}
    
    async def get_price(self, token_id: str) -> float:
        # Implement with retry logic
```

**For Search APIs:**
```python
class SearchClient:
    async def search(self, query: str, num_results: int = 10) -> list:
        # Implement with rate limiting
```

**For Agent Collaboration:**
```python
class AgentOrchestrator:
    async def run_workflow(self, task: dict) -> dict:
        # Coordinate sub-agents
```

---

## 6. Implementation Checklist

### starknet-whale-tracker
- [ ] Integrate Ekubo API for swap/position tracking
- [ ] Add AVNU for aggregator data
- [ ] Implement whale detection heuristics
- [ ] Set up alerts for large transactions

### arbitrage-signal
- [ ] Connect to CoinGecko for price feeds
- [ ] Add Ekubo/AVNU for DEX pricing
- [ ] Implement arbitrage detection algorithm
- [ ] Add risk scoring

### prices
- [ ] Primary: CoinGecko API client
- [ ] Fallback: Chainlink/Pyth for on-chain verification
- [ ] Caching layer for rate limit management
- [ ] Historical data support

### research
- [ ] Brave Search API integration
- [ ] Tavily for content extraction
- [ ] Summarization pipeline
- [ ] Knowledge base storage

### post-generator
- [ ] Persona-aware generation prompts
- [ ] Integration with research outputs
- [ ] Quality scoring
- [ ] Auto-post scheduling

---

## 7. Environment Variables Needed

```bash
# DEX APIs
EKUBO_API_KEY=your_ekubo_key
JEDISWAP_API_KEY=your_jediswap_key
AVNU_API_KEY=your_avnu_key

# Price Feeds
COINGECKO_API_KEY=your_coingecko_key
CHAINLINK_NODE_URL=your_chainlink_rpc

# Search APIs
BRAVE_SEARCH_API_KEY=your_brave_key
TAVILY_API_KEY=your_tavily_key

# Monitoring
ALERT_WEBHOOK_URL=your_webhook_url
```

---

*Generated: 2026-02-01*
*For: Skills Development Environment Setup*
