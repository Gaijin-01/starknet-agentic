"""
Market Intelligence Agent for Starknet Intelligence Colony
===========================================================
Real-time market monitoring: prices, arbitrage, TVL, whale tracking.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from ..shared_state import shared_state, MarketData, ArbitrageOpportunity, WhaleMovement
from ..orchestrator import orchestrator
from ..config import AGENTS, MONITORING, API
from ..clients.coingecko_client import coingecko_client
from ..clients.ekubo_client import ekubo_client
from ..clients.whale_db_client import whale_db_client

logger = logging.getLogger(__name__)


@dataclass
class MarketSummary:
    """Quick market summary"""
    timestamp: str
    total_tvl: float
    total_volume_24h: float
    top_gainers: List[Dict]
    top_losers: List[Dict]
    arbitrage_count: int
    whale_alerts: int
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "total_tvl": self.total_tvl,
            "total_volume_24h": self.total_volume_24h,
            "top_gainers": self.top_gainers,
            "top_losers": self.top_losers,
            "arbitrage_count": self.arbitrage_count,
            "whale_alerts": self.whale_alerts
        }


class MarketAgent:
    """
    Market Intelligence Agent.
    
    Responsibilities:
    - Real-time price monitoring
    - Arbitrage opportunity detection
    - TVL and volume tracking
    - Whale movement detection
    """
    
    def __init__(self):
        self.name = "market_agent"
        self._running = False
        self._last_price_update = None
        self._last_arbitrage_check = None
        
        # Known CEX addresses for whale tracking
        self._known_cex = {
            "binance": "0x...binance...",
            "coinbase": "0x...coinbase...",
        }
    
    async def start(self):
        """Start the market agent"""
        logger.info("Market Agent starting")
        await shared_state.update_agent_status(self.name, "starting")
        self._running = True
        
        # Load whale data
        await whale_db_client.load_data()
        
        await shared_state.update_agent_status(self.name, "running")
        
        try:
            await self._run_loop()
        except asyncio.CancelledError:
            logger.info("Market Agent cancelled")
        finally:
            self._running = False
            await shared_state.update_agent_status(self.name, "stopped")
    
    async def _run_loop(self):
        """Main agent loop"""
        while self._running:
            try:
                # Fetch and process market data
                await self._update_prices()
                await self._check_arbitrage()
                await self._update_tvl()
                await self._check_whales()
                
                # Update last run time
                self._last_price_update = datetime.utcnow()
                
                # Wait for next interval
                await asyncio.sleep(AGENTS.MARKET_POLL_INTERVAL)
                
            except Exception as e:
                logger.error(f"Market Agent error: {e}")
                await shared_state.add_alert("market_agent_error", str(e), "error")
                await asyncio.sleep(10)  # Brief pause on error
    
    # =========================================================================
    # Price Updates
    # =========================================================================
    
    async def _update_prices(self):
        """Update token prices from CoinGecko"""
        try:
            # Get prices for tracked tokens
            token_ids = list(MONITORING.TOKENS.values())
            prices = await coingecko_client.get_price(token_ids)
            
            if not prices:
                logger.warning("Failed to fetch prices")
                return
            
            # Transform to market data format
            market_data = MarketData(
                timestamp=datetime.utcnow().isoformat(),
                prices={token: data.get("usd", 0) for token, data in prices.items()},
                volumes={token: data.get("usd_24h_vol", 0) for token, data in prices.items()},
                changes_24h={token: data.get("usd_24h_change", 0) for token, data in prices.items()}
            )
            
            # Update shared state
            await shared_state.update_market_data(market_data)
            
            # Check for significant price changes
            await self._check_price_alerts(market_data)
            
            logger.info(f"Price update: {len(market_data.prices)} tokens")
            
        except Exception as e:
            logger.error(f"Price update error: {e}")
    
    async def _check_price_alerts(self, data: MarketData):
        """Check for significant price movements"""
        for token, change in data.changes_24h.items():
            if abs(change) >= AGENTS.PRICE_CHANGE_ALERT:
                direction = "↑" if change > 0 else "↓"
                await shared_state.add_alert(
                    "price_alert",
                    f"{token} moved {direction} {abs(change):.2f}% in 24h",
                    "warning" if abs(change) >= 10 else "info"
                )
    
    # =========================================================================
    # Arbitrage Detection
    # =========================================================================
    
    async def _check_arbitrage(self):
        """Check for arbitrage opportunities"""
        try:
            # Get Ekubo data
            ekubo_data = await ekubo_client.get_arbitrage_dashboard()
            
            # Sample prices from other DEXs (in production, query actual APIs)
            other_dex_prices = {
                "STRK": 0.85,  # Sample price on another DEX
                "ETH": 3500,
                "USDC": 1.0
            }
            
            # Detect opportunities
            opportunities = await ekubo_client.detect_arbitrage_opportunities(
                other_dex_prices,
                min_profit=AGENTS.ARBITRAGE_MIN_PROFIT
            )
            
            for opp_data in opportunities:
                # Check if already exists
                existing = await shared_state.get_arbitrage_opportunities(
                    min_profit=0, limit=50
                )
                
                is_new = True
                for existing_opp in existing:
                    if (existing_opp.token == opp_data["token"] and
                        existing_opp.buy_dex == opp_data["buy_dex"] and
                        existing_opp.sell_dex == opp_data["sell_dex"]):
                        is_new = False
                        break
                
                if is_new:
                    opp = ArbitrageOpportunity(
                        token=opp_data["token"],
                        buy_dex=opp_data["buy_dex"],
                        sell_dex=opp_data["sell_dex"],
                        buy_price=opp_data["buy_price"],
                        sell_price=opp_data["sell_price"],
                        profit_percent=opp_data["profit_percent"],
                        volume_usd=opp_data["volume_usd"],
                        timestamp=opp_data["timestamp"]
                    )
                    await shared_state.add_arbitrage(opp)
                    
                    if opp.profit_percent >= 1.0:
                        await shared_state.add_alert(
                            "arbitrage",
                            f"⚡ {opp.token}: {opp.profit_percent:.2f}% profit on "
                            f"{opp.buy_dex} → {opp.sell_dex}",
                            "warning"
                        )
            
            self._last_arbitrage_check = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Arbitrage check error: {e}")
    
    # =========================================================================
    # TVL and Volume Tracking
    # =========================================================================
    
    async def _update_tvl(self):
        """Update TVL and volume data"""
        try:
            # Get Ekubo TVL
            ekubo_tvl = await ekubo_client.get_tvl()
            ekubo_volume = await ekubo_client.get_volume_24h()
            
            # Update shared state with TVL info
            await shared_state.update_market_data(MarketData(
                timestamp=datetime.utcnow().isoformat(),
                prices=await self._get_prices_dict(),
                volumes={"ekubo": ekubo_volume},
                changes_24h={}
            ))
            
            logger.info(f"TVL update: ${ekubo_tvl:,.0f} TVL, ${ekubo_volume:,.0f} 24h vol")
            
        except Exception as e:
            logger.error(f"TVL update error: {e}")
    
    async def _get_prices_dict(self) -> Dict[str, float]:
        """Get current prices as dict"""
        market_data = await shared_state.get_market_data()
        if market_data:
            return market_data.prices
        return {}
    
    # =========================================================================
    # Whale Tracking
    # =========================================================================
    
    async def _check_whales(self):
        """Check for whale movements"""
        try:
            # Get recent large transfers
            large_transfers = await whale_db_client.get_large_transfers(
                threshold_usd=AGENTS.WHALE_TRANSFER_THRESHOLD
            )
            
            for transfer in large_transfers:
                # Check for unusual activity
                unusual = await whale_db_client.detect_unusual_activity(
                    transfer.from_address
                )
                
                if unusual:
                    await shared_state.add_alert(
                        "whale_unusual",
                        f"🐋 Unusual: {transfer.token_symbol} "
                        f"${transfer.amount_usd:,.0f} from {transfer.from_address[:10]}...",
                        "warning"
                    )
                
                # Add to shared state
                movement = WhaleMovement(
                    tx_hash=transfer.tx_hash,
                    from_address=transfer.from_address,
                    to_address=transfer.to_address,
                    token=transfer.token_symbol,
                    amount=transfer.amount,
                    amount_usd=transfer.amount_usd,
                    timestamp=transfer.timestamp,
                    direction=await self._determine_direction(transfer)
                )
                await shared_state.add_whale_movement(movement)
            
            if large_transfers:
                logger.info(f"Whale check: {len(large_transfers)} large transfers")
                
        except Exception as e:
            logger.error(f"Whale check error: {e}")
    
    async def _determine_direction(self, tx) -> str:
        """Determine if transfer is inflow, outflow, or internal"""
        # Simplified - in production, check against known CEX addresses
        return "internal"
    
    # =========================================================================
    # Public API
    # =========================================================================
    
    async def get_market_summary(self) -> MarketSummary:
        """Get quick market summary"""
        market_data = await shared_state.get_market_data()
        arbitrage = await shared_state.get_arbitrage_opportunities()
        whales = await whale_db_client.get_large_transfers()
        
        # Calculate gainers/losers
        if market_data:
            sorted_tokens = sorted(
                market_data.changes_24h.items(),
                key=lambda x: x[1],
                reverse=True
            )
            top_gainers = [
                {"token": t, "change": c} 
                for t, c in sorted_tokens[:3] if c > 0
            ]
            top_losers = [
                {"token": t, "change": c}
                for t, c in sorted_tokens[-3:] if c < 0
            ]
        else:
            top_gainers = []
            top_losers = []
        
        return MarketSummary(
            timestamp=datetime.utcnow().isoformat(),
            total_tvl=await ekubo_client.get_tvl(),
            total_volume_24h=await ekubo_client.get_volume_24h(),
            top_gainers=top_gainers,
            top_losers=top_losers,
            arbitrage_count=len(arbitrage),
            whale_alerts=len(whales)
        )
    
    async def get_arbitrage_report(self) -> List[Dict]:
        """Get arbitrage opportunities report"""
        opportunities = await shared_state.get_arbitrage_opportunities(min_profit=0.5)
        return [opp.to_dict() for opp in opportunities]
    
    async def run_once(self):
        """Run market update once (for testing)"""
        await self._update_prices()
        await self._check_arbitrage()
        await self._update_tvl()
        await self._check_whales()
        return await self.get_market_summary()


# Create agent instance
market_agent = MarketAgent()
