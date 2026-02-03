"""
Basic tests for Starknet Intelligence Colony
"""

import asyncio
import pytest
from pathlib import Path
import sys

# Add colony to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestSharedState:
    """Tests for shared state"""
    
    @pytest.fixture
    def state(self):
        """Create fresh shared state for testing"""
        from shared_state import SharedState
        return SharedState()
    
    @pytest.mark.asyncio
    async def test_market_data_update(self, state):
        """Test market data update"""
        from shared_state import MarketData
        
        data = MarketData(
            timestamp="2024-01-01T00:00:00",
            prices={"ETH": 3500, "STRK": 0.85},
            volumes={"ETH": 1000000},
            changes_24h={"ETH": 2.5}
        )
        
        await state.update_market_data(data)
        result = await state.get_market_data()
        
        assert result is not None
        assert result.prices["ETH"] == 3500
        assert result.changes_24h["ETH"] == 2.5
    
    @pytest.mark.asyncio
    async def test_arbitrage_add_and_get(self, state):
        """Test arbitrage opportunity management"""
        from shared_state import ArbitrageOpportunity
        
        opp = ArbitrageOpportunity(
            token="ETH",
            buy_dex="ekubo",
            sell_dex="jediswap",
            buy_price=3500,
            sell_price=3520,
            profit_percent=0.57,
            volume_usd=100000
        )
        
        await state.add_arbitrage(opp)
        opportunities = await state.get_arbitrage_opportunities(min_profit=0.5)
        
        assert len(opportunities) == 1
        assert opportunities[0].token == "ETH"
        assert opportunities[0].profit_percent == 0.57
    
    @pytest.mark.asyncio
    async def test_whale_movements(self, state):
        """Test whale movement tracking"""
        from shared_state import WhaleMovement
        
        movement = WhaleMovement(
            tx_hash="0x123",
            from_address="0xabc",
            to_address="0xdef",
            token="ETH",
            amount=100,
            amount_usd=350000,
            timestamp="2024-01-01T00:00:00"
        )
        
        await state.add_whale_movement(movement)
        movements = await state.get_whale_movements(since_hours=24)
        
        assert len(movements) == 1
        assert movements[0].amount_usd == 350000
    
    @pytest.mark.asyncio
    async def test_research_reports(self, state):
        """Test research report storage"""
        from shared_state import ResearchReport
        
        report = ResearchReport(
            id="test-123",
            topic="Starknet DeFi",
            title="Test Report",
            summary="Test summary",
            findings=["Finding 1", "Finding 2"],
            risks=["Risk 1"],
            opportunities=["Opp 1"],
            sources=[{"url": "https://example.com"}]
        )
        
        await state.add_research_report(report)
        reports = await state.get_research_reports()
        
        assert len(reports) == 1
        assert reports[0].topic == "Starknet DeFi"
    
    @pytest.mark.asyncio
    async def test_content_pieces(self, state):
        """Test content piece storage"""
        from shared_state import ContentPiece
        
        content = ContentPiece(
            id="content-123",
            type="tweet",
            platform="twitter",
            title="Test Thread",
            content="Test tweet content"
        )
        
        await state.add_content(content)
        content_list = await state.get_content()
        
        assert len(content_list) == 1
        assert content_list[0].type == "tweet"
    
    @pytest.mark.asyncio
    async def test_alerts(self, state):
        """Test alert system"""
        await state.add_alert("test_alert", "Test message", "info")
        alerts = await state.get_alerts()
        
        assert len(alerts) == 1
        assert alerts[0]["message"] == "Test message"
        assert alerts[0]["severity"] == "info"


class TestConfig:
    """Tests for configuration"""
    
    def test_config_loading(self):
        """Test configuration loads correctly"""
        from config import API, AGENTS, MONITORING, DASHBOARD
        
        assert API.COINGECKO_BASE_URL is not None
        assert AGENTS.MARKET_POLL_INTERVAL > 0
        assert DASHBOARD.PORT == 5000
    
    def test_token_mapping(self):
        """Test token ID mapping"""
        from config import get_token_id
        
        assert get_token_id("ETH") == "ethereum"
        assert get_token_id("STRK") == "starknet"
        assert get_token_id("unknown") is None
    
    def test_whale_threshold(self):
        """Test whale transfer threshold"""
        from config import is_whale_transfer
        
        assert is_whale_transfer(150000) is True
        assert is_whale_transfer(50000) is False


class TestCoinGeckoClient:
    """Tests for CoinGecko client"""
    
    @pytest.fixture
    def client(self):
        from clients.coingecko_client import CoinGeckoClient
        return CoinGeckoClient()
    
    @pytest.mark.asyncio
    async def test_client_initialization(self, client):
        """Test client creates properly"""
        assert client.base_url is not None
        assert client.api_key == ""
    
    @pytest.mark.asyncio
    async def test_price_fetch(self, client):
        """Test price fetching (may fail without API)"""
        prices = await client.get_price(["ethereum", "starknet"])
        
        # May return None if API fails
        if prices:
            assert "ethereum" in prices or "starknet" in prices


class TestEkuboClient:
    """Tests for Ekubo client"""
    
    @pytest.fixture
    def client(self):
        from clients.ekubo_client import EkuboClient
        return EkuboClient()
    
    @pytest.mark.asyncio
    async def test_get_pools(self, client):
        """Test pool data retrieval"""
        pools = await client.get_pools()
        
        assert len(pools) > 0
        for pool in pools:
            assert pool.tvl >= 0
            assert pool.token0_symbol is not None
    
    @pytest.mark.asyncio
    async def test_tvl_calculation(self, client):
        """Test TVL calculation"""
        tvl = await client.get_tvl()
        
        assert tvl >= 0
        assert isinstance(tvl, float)


class TestWhaleDBClient:
    """Tests for whale database client"""
    
    @pytest.fixture
    def client(self):
        from clients.whale_db_client import WhaleDBClient
        return WhaleDBClient()
    
    @pytest.mark.asyncio
    async def test_sample_transactions(self, client):
        """Test sample transaction generation"""
        txs = await client.get_sample_transactions(limit=5)
        
        assert len(txs) > 0
        for tx in txs:
            assert tx.amount_usd > 0
    
    @pytest.mark.asyncio
    async def test_movement_summary(self, client):
        """Test whale movement summary"""
        summary = await client.get_whale_movement_summary(hours=24)
        
        assert "total_volume_usd" in summary
        assert "transaction_count" in summary
        assert summary["period_hours"] == 24


class TestMarketAgent:
    """Tests for market agent"""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test agent creates properly"""
        from agents.market_agent import MarketAgent
        agent = MarketAgent()
        
        assert agent.name == "market_agent"
        assert agent._running is False
    
    @pytest.mark.asyncio
    async def test_market_summary(self):
        """Test market summary generation"""
        from agents.market_agent import MarketAgent
        agent = MarketAgent()
        
        summary = await agent.get_market_summary()
        
        assert summary.timestamp is not None
        assert isinstance(summary.total_tvl, float)


class TestContentAgent:
    """Tests for content agent"""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test agent creates properly"""
        from agents.content_agent import ContentAgent
        agent = ContentAgent()
        
        assert agent.name == "content_agent"
    
    @pytest.mark.asyncio
    async def test_tweet_truncation(self):
        """Test tweet length truncation"""
        from agents.content_agent import ContentAgent
        agent = ContentAgent()
        
        long_content = "A" * 300
        truncated = agent.truncate_for_tweet(long_content)
        
        assert len(truncated) <= 280


class TestOrchestrator:
    """Tests for orchestrator"""
    
    @pytest.fixture
    def orch(self):
        from orchestrator import Orchestrator
        return Orchestrator()
    
    def test_orchestrator_initialization(self, orch):
        """Test orchestrator creates properly"""
        assert orch._running is False
        assert len(orch._agents) == 0
    
    @pytest.mark.asyncio
    async def test_agent_registration(self, orch):
        """Test agent registration"""
        class DummyAgent:
            async def run(self):
                pass
        
        agent = DummyAgent()
        orch.register_agent("test_agent", agent)
        
        assert "test_agent" in orch._agents
        status = orch.get_agent_status("test_agent")
        assert status is not None
    
    @pytest.mark.asyncio
    async def test_agent_lifecycle(self, orch):
        """Test agent start/stop lifecycle"""
        class DummyAgent:
            def __init__(self):
                self.running = False
            async def run(self):
                self.running = True
                while True:
                    await asyncio.sleep(0.1)
        
        agent = DummyAgent()
        orch.register_agent("lifecycle_agent", agent)
        
        # Start agent
        result = await orch.start_agent("lifecycle_agent")
        assert result is True
        
        # Stop agent
        result = await orch.stop_agent("lifecycle_agent")
        assert result is True


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
