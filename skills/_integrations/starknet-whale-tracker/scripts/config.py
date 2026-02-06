"""
Starknet Whale Tracker - Configuration
"""
import os
from dataclasses import dataclass
from typing import List, Optional

# Get Alchemy key from environment
ALCHEMY_KEY = os.getenv("STARKNET_ALCHEMY_KEY", os.getenv("ALCHEMY_API_KEY", ""))
ALCHEMY_URL = f"https://starknet-mainnet.g.alchemy.com/v2/{ALCHEMY_KEY}" if ALCHEMY_KEY else ""


@dataclass
class StarknetConfig:
    rpc_url: str
    indexer_url: str = "https://api.starknet.io/v1"


@dataclass
class WhaleConfig:
    alert_threshold: int = 1000  # STRK
    default_tags: List[str] = None


@dataclass
class MempoolConfig:
    enabled: bool = True
    min_value_strk: int = 100
    max_block_wait: int = 5


@dataclass
class ArbitrageConfig:
    enabled: bool = True
    min_profit_percent: float = 0.5
    dexes: List[str] = None


@dataclass
class TelegramConfig:
    enabled: bool = False
    bot_token: str = ""
    chat_id: str = ""


@dataclass
class WebhookConfig:
    enabled: bool = False
    url: str = ""


@dataclass
class Config:
    starknet: StarknetConfig
    whales: WhaleConfig
    mempool: MempoolConfig
    arbitrage: ArbitrageConfig
    telegram: TelegramConfig
    webhook: WebhookConfig

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            starknet=StarknetConfig(
                rpc_url=os.getenv("STARKNET_RPC_URL", ""),
                indexer_url=os.getenv("STARKNET_INDEXER_URL", "https://api.starknet.io/v1")
            ),
            whales=WhaleConfig(
                alert_threshold=int(os.getenv("WHALE_ALERT_THRESHOLD", "1000")),
                default_tags=["whale"]
            ),
            mempool=MempoolConfig(
                enabled=os.getenv("MEMPOOL_ENABLED", "true").lower() == "true",
                min_value_strk=int(os.getenv("MEMPOOL_MIN_VALUE", "100")),
                max_block_wait=int(os.getenv("MEMPOOL_MAX_BLOCK_WAIT", "5"))
            ),
            arbitrage=ArbitrageConfig(
                enabled=os.getenv("ARBITRAGE_ENABLED", "true").lower() == "true",
                min_profit_percent=float(os.getenv("ARBITRAGE_MIN_PROFIT", "0.5")),
                dexes=["jediswap", "ekubo", "10k"]
            ),
            telegram=TelegramConfig(
                enabled=os.getenv("TELEGRAM_ENABLED", "false").lower() == "true",
                bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
                chat_id=os.getenv("TELEGRAM_CHAT_ID", "")
            ),
            webhook=WebhookConfig(
                enabled=os.getenv("WEBHOOK_ENABLED", "false").lower() == "true",
                url=os.getenv("WEBHOOK_URL", "")
            )
        )


# Default config for development
DEFAULT_CONFIG = Config(
    starknet=StarknetConfig(
        rpc_url=ALCHEMY_URL if ALCHEMY_URL else os.getenv("STARKNET_RPC_URL", "https://rpc.starknet.lava.build:443"),
        indexer_url="https://api.starknet.io/v1"
    ),
    whales=WhaleConfig(
        alert_threshold=1000,
        default_tags=["whale", "deployer", "large_holder"]
    ),
    mempool=MempoolConfig(
        enabled=True,
        min_value_strk=100,
        max_block_wait=5
    ),
    arbitrage=ArbitrageConfig(
        enabled=True,
        min_profit_percent=0.5,
        dexes=["jediswap", "ekubo", "10k"]
    ),
    telegram=TelegramConfig(
        enabled=False,
        bot_token="",
        chat_id=""
    ),
    webhook=WebhookConfig(
        enabled=False,
        url=""
    )
)
