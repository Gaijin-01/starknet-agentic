"""
Starknet Whale Tracker
Real-time monitoring of whale wallets, mempool, and arbitrage opportunities on Starknet
"""

__version__ = "1.0.0"
__author__ = "Clawd / Sefirot"

from tracker import StarknetWhaleTracker, create_tracker
from config import Config, DEFAULT_CONFIG
from whale_db import WhaleDatabase, WhaleWallet, WhaleActivity
from mempool_monitor import MempoolMonitor, MempoolEvent, EventType
from arbitrage import ArbitrageScanner, ArbitrageOpportunity

__all__ = [
    "StarknetWhaleTracker",
    "create_tracker",
    "Config",
    "DEFAULT_CONFIG",
    "WhaleDatabase",
    "WhaleWallet",
    "WhaleActivity",
    "MempoolMonitor",
    "MempoolEvent",
    "EventType",
    "ArbitrageScanner",
    "ArbitrageOpportunity",
]
