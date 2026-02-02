"""
Content Agent for Starknet Intelligence Colony
===============================================
Automated content generation: reports, Twitter threads, articles.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import uuid
import re

from ..shared_state import shared_state, ContentPiece, ResearchReport
from ..orchestrator import orchestrator
from ..config import AGENTS, REPORTS

logger = logging.getLogger(__name__)


@dataclass
class Tweet:
    """A single tweet"""
    content: str
    thread_position: int
    thread_id: str


class ContentAgent:
    """
    Content Agent for automated content generation.
    
    Responsibilities:
    - Generate hourly intelligence reports
    - Create Twitter-ready threads
    - Write analysis articles
    - Format for multiple platforms
    """
    
    def __init__(self):
        self.name = "content_agent"
        self._running = False
        self._last_content = None
        self._content_queue: List[Dict] = []
    
    async def start(self):
        """Start the content agent"""
        logger.info("Content Agent starting")
        await shared_state.update_agent_status(self.name, "starting")
        self._running = True
        await shared_state.update_agent_status(self.name, "running")
        
        try:
            await self._run_loop()
        except asyncio.CancelledError:
            logger.info("Content Agent cancelled")
        finally:
            self._running = False
            await shared_state.update_agent_status(self.name, "stopped")
    
    async def _run_loop(self):
        """Main agent loop"""
        while self._running:
            try:
                # Generate content
                await self._generate_hourly_content()
                
                # Wait for next cycle
                await asyncio.sleep(AGENTS.REPORT_INTERVAL)
                
            except Exception as e:
                logger.error(f"Content Agent error: {e}")
                await shared_state.add_alert("content_agent_error", str(e), "error")
                await asyncio.sleep(3600)
    
    # =========================================================================
    # Content Generation
    # =========================================================================
    
    async def _generate_hourly_content(self):
        """Generate all hourly content"""
        logger.info("Generating hourly content")
        
        # Get data for content
        market_summary = await self._get_market_summary()
        recent_research = await shared_state.get_research_reports(limit=1)
        arbitrage = await shared_state.get_arbitrage_opportunities(limit=5)
        
        # Generate content pieces
        await self._generate_market_brief(market_summary)
        await self._generate_twitter_thread(market_summary, arbitrage)
        await self._generate_analysis_article(market_summary, recent_research)
        await self._generate_daily_digest()
        
        self._last_content = datetime.utcnow()
    
    async def _get_market_summary(self) -> Dict[str, Any]:
        """Get market data for content generation"""
        market_data = await shared_state.get_market_data()
        arbitrage = await shared_state.get_arbitrage_opportunities()
        whales = await shared_state.get_whale_movements()
        
        return {
            "prices": market_data.to_dict() if market_data else {},
            "arbitrage_count": len(arbitrage),
            "whale_count": len(whales),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # =========================================================================
    # Market Brief Generation
    # =========================================================================
    
    async def _generate_market_brief(self, data: Dict) -> ContentPiece:
        """Generate hourly market intelligence brief"""
        
        content = self._format_market_brief(data)
        
        brief = ContentPiece(
            id=str(uuid.uuid4())[:8],
            type="report",
            platform="telegram",
            title=f"Market Intelligence Brief - {datetime.utcnow().strftime('%H:%M UTC')}",
            content=content,
            tags=["market", "intelligence", "starknet", "defi"]
        )
        
        await shared_state.add_content(brief)
        logger.info(f"Generated market brief")
        return brief
    
    def _format_market_brief(self, data: Dict) -> str:
        """Format market brief content"""
        content = "📊 **Starknet Market Intelligence**\n\n"
        content += f"🕐 {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        
        # Prices
        prices = data.get("prices", {})
        if prices and prices.get("prices"):
            content += "**Prices**\n"
            for token, price in list(prices["prices"].items())[:5]:
                change = prices.get("changes_24h", {}).get(token, 0)
                emoji = "🟢" if change > 0 else "🔴"
                content += f"{token}: ${price:,.2f} {emoji} {change:+.2f}%\n"
            content += "\n"
        
        # Arbitrage
        arb_count = data.get("arbitrage_count", 0)
        content += f"⚡ Arbitrage: {arb_count} opportunities\n"
        
        # Whales
        whale_count = data.get("whale_count", 0)
        content += f"🐋 Whale Activity: {whale_count} large transfers\n"
        
        content += "\n_Generated by Starknet Intelligence Colony_"
        return content
    
    # =========================================================================
    # Twitter Thread Generation
    # =========================================================================
    
    async def _generate_twitter_thread(self, 
                                        data: Dict,
                                        arbitrage: List) -> ContentPiece:
        """Generate Twitter-ready thread"""
        
        thread_id = str(uuid.uuid4())[:8]
        tweets = []
        
        # Tweet 1: Hook
        tweets.append(Tweet(
            content="🧵 Starknet DeFi Weekly Update\n\n"
                    "Here's what's happening on Starknet this week 👇",
            thread_position=0,
            thread_id=thread_id
        ))
        
        # Tweet 2: Market overview
        prices = data.get("prices", {})
        price_text = ", ".join([
            f"${k}: ${v:,.2f}" 
            for k, v in list(prices.get("prices", {}).items())[:3]
        ])
        tweets.append(Tweet(
            content=f"📈 Market Overview\n\n"
                    f"Key prices:\n{price_text}\n\n"
                    f"#Starknet #DeFi",
            thread_position=1,
            thread_id=thread_id
        ))
        
        # Tweet 3: Arbitrage opportunities
        if arbitrage:
            best_arb = max(arbitrage, key=lambda x: x.profit_percent)
            tweets.append(Tweet(
                content=f"⚡ Arbitrage Alert\n\n"
                        f"Detected {len(arbitrage)} opportunities.\n"
                        f"Best: {best_arb.token} @ {best_arb.profit_percent:.2f}% profit\n\n"
                        f"⚠️ Always DYOR before trading",
            thread_position=2,
            thread_id=thread_id
        ))
        
        # Tweet 4: Whale activity
        whale_count = data.get("whale_count", 0)
        tweets.append(Tweet(
            content=f"🐋 Whale Watch\n\n"
                    f"{whale_count} large transfers detected.\n"
                    f"Smart money is {'accumulating 📈' if whale_count > 5 else 'quiet 🔇'}\n\n"
                    f"Track with @StarknetColony",
            thread_position=3,
            thread_id=thread_id
        ))
        
        # Tweet 5: CTA
        tweets.append(Tweet(
            content=f"💡 Want more insights?\n\n"
                    f"Follow @StarknetColony for real-time\n"
                    f"Starknet DeFi intelligence.\n\n"
                    f"🧠 Powered by AI agents",
            thread_position=4,
            thread_id=thread_id
        ))
        
        # Create content piece
        thread_content = "\n\n---\n\n".join([
            f"Tweet {t.thread_position + 1}: {t.content}" 
            for t in tweets
        ])
        
        thread = ContentPiece(
            id=thread_id,
            type="thread",
            platform="twitter",
            title=f"Twitter Thread - {datetime.utcnow().strftime('%Y-%m-%d')}",
            content=thread_content,
            tags=["starknet", "defi", "thread", "crypto"]
        )
        
        await shared_state.add_content(thread)
        logger.info(f"Generated Twitter thread with {len(tweets)} tweets")
        return thread
    
    # =========================================================================
    # Article Generation
    # =========================================================================
    
    async def _generate_analysis_article(self, 
                                          data: Dict,
                                          research: List[ResearchReport]) -> ContentPiece:
        """Generate in-depth analysis article"""
        
        article = self._format_analysis_article(data, research)
        
        piece = ContentPiece(
            id=str(uuid.uuid4())[:8],
            type="article",
            platform="blog",
            title=f"Deep Dive: Starknet DeFi Analysis - {datetime.utcnow().strftime('%B %d, %Y')}",
            content=article,
            tags=["analysis", "starknet", "defi", "deep-dive"]
        )
        
        await shared_state.add_content(piece)
        logger.info("Generated analysis article")
        return piece
    
    def _format_analysis_article(self, 
                                  data: Dict,
                                  research: List[ResearchReport]) -> str:
        """Format full article content"""
        
        article = f"""# Starknet DeFi Analysis Report

**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
**By:** Starknet Intelligence Colony

---

## Executive Summary

The Starknet ecosystem continues to show strong momentum with significant activity across DEXes, lending protocols, and yield strategies.

## Market Overview

### Token Prices

| Token | Price | 24h Change |
|-------|-------|------------|
"""
        
        prices = data.get("prices", {}).get("prices", {})
        changes = data.get("prices", {}).get("changes_24h", {})
        
        for token, price in prices.items():
            change = changes.get(token, 0)
            article += f"| {token} | ${price:,.2f} | {change:+.2f}% |\n"
        
        article += f"""
### Arbitrage Landscape

Currently monitoring {data.get("arbitrage_count", 0)} arbitrage opportunities.

### Risk Assessment

- Smart contract risk remains present
- Impermanent loss for liquidity providers
- Oracle dependency risks
- Market volatility

## Conclusion

Starknet DeFi ecosystem shows continued growth potential. Monitor TVL and protocol launches for opportunities.
"""
        return article
    
    async def _generate_daily_digest(self):
        """Generate daily digest content"""
        # Get all recent data
        arbitrage = await shared_state.get_arbitrage_opportunities(limit=10)
        whales = await shared_state.get_whale_movements(limit=20)
        research = await shared_state.get_research_reports(limit=5)
        
        digest = f"""# Daily Digest - {datetime.utcnow().strftime('%Y-%m-%d')}

## Summary
- Arbitrage opportunities: {len(arbitrage)}
- Whale movements: {len(whales)}
- Research reports: {len(research)}

## Top Arbitrage
"""
        
        for arb in arbitrage[:5]:
            digest += f"- {arb.token}: {arb.profit_percent:.2f}% ({arb.buy_dex} → {arb.sell_dex})\n"
        
        digest += "\n## Recent Research\n"
        for r in research:
            digest += f"- {r.title}: {r.summary[:100]}...\n"
        
        piece = ContentPiece(
            id=str(uuid.uuid4())[:8],
            type="digest",
            platform="all",
            title=f"Daily Digest - {datetime.utcnow().strftime('%Y-%m-%d')}",
            content=digest,
            tags=["digest", "daily", "starknet"]
        )
        
        await shared_state.add_content(piece)
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    async def generate_custom_content(self, 
                                      content_type: str,
                                      topic: str,
                                      platform: str = "all") -> ContentPiece:
        """Generate custom content on demand"""
        
        content_map = {
            "alert": f"🚨 ALERT: {topic}",
            "update": f"📢 Update: {topic}",
            "analysis": f"📊 Analysis: {topic}",
            "thread": f"🧵 Thread about {topic}",
        }
        
        content = content_map.get(content_type, f"Content: {topic}")
        
        piece = ContentPiece(
            id=str(uuid.uuid4())[:8],
            type=content_type,
            platform=platform,
            title=f"{content_type.title()} - {topic}",
            content=content,
            tags=[content_type, topic.lower().replace(" ", "-")]
        )
        
        await shared_state.add_content(piece)
        return piece
    
    async def format_for_platform(self, 
                                   content: str,
                                   platform: str) -> str:
        """Format content for specific platform"""
        if platform == "twitter":
            # Twitter formatting
            content = content[:280]
            content = re.sub(r'\[(.*?)\]', r'\1', content)  # Remove markdown
        elif platform == "telegram":
            # Telegram formatting
            content = content.replace('**', '*')
        elif platform == "discord":
            # Discord formatting
            content = content.replace('**', '**')
        
        return content
    
    def truncate_for_tweet(self, content: str, max_length: int = 280) -> str:
        """Truncate content to tweet length"""
        if len(content) <= max_length:
            return content
        
        return content[:max_length - 3] + "..."


# Create agent instance
content_agent = ContentAgent()
