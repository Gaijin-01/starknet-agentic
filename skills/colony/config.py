"""
Starknet Intelligence Colony Configuration
==========================================
Central configuration for all agents and clients.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import timedelta


# ============================================================================
# Paths
# ============================================================================
BASE_DIR = Path(__file__).parent
REPORTS_DIR = BASE_DIR / "reports"
TESTS_DIR = BASE_DIR / "tests"
DASHBOARD_DIR = BASE_DIR / "dashboard"

# Ensure directories exist
REPORTS_DIR.mkdir(exist_ok=True)
TESTS_DIR.mkdir(exist_ok=True)


# ============================================================================
# API Configuration
# ============================================================================
@dataclass
class APIConfig:
    """API endpoints and keys"""
    
    # CoinGecko - Token Prices
    COINGECKO_BASE_URL: str = "https://api.coingecko.com/api/v3"
    COINGECKO_API_KEY: str = os.getenv("COINGECKO_API_KEY", "")
    
    # Ekubo - DEX Data
    EKUBO_API_URL: str = "https://api.ekubo.org/v1"
    EKUBO_SUBGRAPH_URL: str = "https://api.thegraph.com/subgraphs/name/ekubo/exchange"
    
    # Starkscan - On-chain Data
    STARKSCAN_API_URL: str = "https://api.starkscan.co/api/v0.2"
    STARKSCAN_API_KEY: str = os.getenv("STARKSCAN_API_KEY", "")
    
    # Web Search (Brave)
    BRAVE_API_KEY: str = os.getenv("BRAVE_API_KEY", "")


# ============================================================================
# Agent Configuration
# ============================================================================
@dataclass
class AgentConfig:
    """Agent-specific settings"""
    
    # Market Agent
    MARKET_POLL_INTERVAL: int = 60  # seconds
    ARBITRAGE_MIN_PROFIT: float = 0.5  # minimum profit % to report
    WHALE_TRANSFER_THRESHOLD: int = 100_000  # USD threshold
    PRICE_CHANGE_ALERT: float = 5.0  # % change to alert
    
    # Research Agent
    RESEARCH_TOPICS: List[str] = field(default_factory=lambda: [
        "Starknet DeFi protocols",
        "Starknet TVL growth",
        "Starknet ecosystem updates",
        "DeFi on Starknet 2024"
    ])
    MAX_RESEARCH_DEPTH: int = 3  # links to follow
    
    # Content Agent
    CONTENT_LANGUAGES: List[str] = field(default_factory=lambda: ["en"])
    TWITTER_THREAD_LENGTH: int = 10  # max tweets per thread
    REPORT_INTERVAL: int = 3600  # seconds (1 hour)


# ============================================================================
# Monitoring Configuration
# ============================================================================
@dataclass
class MonitoringConfig:
    """What to monitor"""
    
    # Tokens to track (symbol -> coingecko id)
    TOKENS: Dict[str, str] = field(default_factory=lambda: {
        "ETH": "ethereum",
        "STRK": "starknet",
        "USDC": "usd-coin",
        "USDT": "tether",
        "BTC": "bitcoin",
    })
    
    # DEXes to monitor
    DEXES: List[str] = field(default_factory=lambda: [
        "ekubo",
        "jediswap",
        "myswap",
        "avnu",
        "10k"
    ])
    
    # Protocols for TVL tracking
    PROTOCOLS: List[str] = field(default_factory=lambda: [
        "ekubo",
        "jediswap",
        "myswap",
        "starkswap",
        "nostra"
    ])


# ============================================================================
# Dashboard Configuration
# ============================================================================
@dataclass
class DashboardConfig:
    """Web dashboard settings"""
    
    HOST: str = "0.0.0.0"
    PORT: int = 5000
    DEBUG: bool = False
    SECRET_KEY: str = os.getenv("DASHBOARD_SECRET", "dev-secret-change-in-prod")
    REFRESH_INTERVAL: int = 30  # seconds
    THEME: str = "dark"


# ============================================================================
# Report Configuration
# ============================================================================
@dataclass
class ReportConfig:
    """Report generation settings"""
    
    OUTPUT_DIR: Path = REPORTS_DIR
    DATE_FORMAT: str = "%Y%m%d_%H%M"
    INCLUDE_MARKET_DATA: bool = True
    INCLUDE_WHALE_ACTIVITY: bool = True
    INCLUDE_RESEARCH: bool = True
    
    # Content templates
    TWITTER_MAX_CHARS: int = 280
    THREAD_MAX_TWEETS: int = 10


# ============================================================================
# Logging Configuration
# ============================================================================
@dataclass
class LoggingConfig:
    """Logging settings"""
    
    LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    FILE: Optional[str] = str(BASE_DIR / "colony.log")
    MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    BACKUP_COUNT: int = 5


# ============================================================================
# Export All Configurations
# ============================================================================
API = APIConfig()
AGENTS = AgentConfig()
MONITORING = MonitoringConfig()
DASHBOARD = DashboardConfig()
REPORTS = ReportConfig()
LOGGING = LoggingConfig()


# ============================================================================
# Utility Functions
# ============================================================================
def get_token_id(symbol: str) -> Optional[str]:
    """Get CoinGecko ID for a token symbol"""
    return MONITORING.TOKENS.get(symbol.lower())


def is_whale_transfer(amount_usd: float) -> bool:
    """Check if transfer amount qualifies as whale activity"""
    return amount_usd >= AGENTS.WHALE_TRANSFER_THRESHOLD


def format_timestamp(ts) -> str:
    """Format timestamp for reports"""
    from datetime import datetime
    if isinstance(ts, (int, float)):
        dt = datetime.fromtimestamp(ts)
    elif isinstance(ts, str):
        dt = datetime.fromisoformat(ts)
    else:
        dt = ts
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


# Starknet-specific contract addresses (sample)
STARKNET_CONTRACTS = {
    "ETH": "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004d7",
    "USDC": "0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a",
    "STRK": "0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938",
    "WBTC": "0x12d5398c66024acf409e8b5ad9e24c93d5386a4cf59fa2a9b00003bf9df6bf7",
}
