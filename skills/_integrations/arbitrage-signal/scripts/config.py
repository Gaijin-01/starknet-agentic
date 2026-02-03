"""
Arbitrage Signal - Configuration
"""
import os
from dataclasses import dataclass
from typing import List


@dataclass
class Config:
    telegram_enabled: bool
    bot_token: str
    chat_id: str
    min_profit_percent: float
    min_profit_usd: float
    scan_interval: int
    
    @classmethod
    def load(cls) -> "Config":
        return cls(
            telegram_enabled=os.getenv("TELEGRAM_ENABLED", "false").lower() == "true",
            bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
            min_profit_percent=float(os.getenv("ARBITRAGE_MIN_PROFIT", "0.3")),
            min_profit_usd=float(os.getenv("ARBITRAGE_MIN_USD", "1.0")),
            scan_interval=int(os.getenv("SCAN_INTERVAL", "900"))
        )


# Default config
DEFAULT_CONFIG = Config(
    telegram_enabled=False,
    bot_token="",
    chat_id="",
    min_profit_percent=0.3,
    min_profit_usd=1.0,
    scan_interval=900
)
