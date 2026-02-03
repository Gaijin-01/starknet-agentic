#!/usr/bin/env python3
"""
executor.py - Tool Execution Bridge for MiniMax LLM

This module executes tools defined in tools.py and returns structured results.
It bridges the LLM tool calls to actual skill functions.

IMPORTANT: This is a READ-ONLY execution layer. It calls existing skill functions
and returns their results. It does NOT modify system state.
"""

import asyncio
import importlib.util
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Add skills paths
SKILLS_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SKILLS_ROOT / "_system"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger('tool-executor')


class ToolExecutor:
    """
    Execute tools and return structured results to LLM.
    
    This class bridges LLM tool calls to actual skill functions.
    """
    
    def __init__(self, skills_root: str = None):
        self.skills_root = Path(skills_root) if skills_root else Path(__file__).parent.parent.parent
        self._initialized = False
    
    def _ensure_initialized(self):
        """Initialize skill modules lazily."""
        if self._initialized:
            return
        
        try:
            # Import price service
            from prices.scripts.prices import PriceService
            self._price_service_class = PriceService
            
            # Import research module
            from research.scripts.research import research
            self._research_func = research
            
            # Import whale tracker (optional - with fallback for Python 3.14)
            try:
                from starknet_whale_tracker.scripts.whales_real import get_stats as _get_stats
                self._whale_stats_func = _get_stats
            except ImportError:
                # Fallback: use whales_real directly without starknet.py
                try:
                    import importlib.util
                    scripts_dir = Path(__file__).parent.parent.parent / "_integrations" / "starknet-whale-tracker" / "scripts"
                    spec = importlib.util.spec_from_file_location("whales_real", scripts_dir / "whales_real.py")
                    whales_mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(whales_mod)
                    self._whale_stats_func = whales_mod.get_stats
                except Exception:
                    self._whale_stats_func = None
                    logger.warning("Whale tracker not available (Python 3.14 compatibility)")
            
            self._initialized = True
            logger.info("Tool executor initialized successfully")
            
        except ImportError as e:
            logger.error(f"Failed to initialize skill modules: {e}")
            # Don't raise - allow partial functionality
            self._initialized = True
    
    async def execute(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool by name with given arguments.
        
        Args:
            tool_name: Name of the tool (from TOOL_DEFINITIONS)
            args: Arguments dict from LLM
            
        Returns:
            Dict with result or error
        """
        self._ensure_initialized()
        
        try:
            if tool_name == "get_crypto_price":
                return await self._get_crypto_price(args)
            elif tool_name == "get_crypto_prices":
                return await self._get_crypto_prices(args)
            elif tool_name == "get_top_coins":
                return await self._get_top_coins(args)
            elif tool_name == "web_search":
                return await self._web_search(args)
            elif tool_name == "web_fetch":
                return self._web_fetch(args)
            elif tool_name == "get_whale_stats":
                return await self._get_whale_stats(args)
            elif tool_name == "get_whale_activity":
                return await self._get_whale_activity(args)
            elif tool_name == "find_arbitrage":
                return await self._find_arbitrage(args)
            elif tool_name == "get_defi_yields":
                return await self._get_defi_yields(args)
            elif tool_name == "get_market_summary":
                return await self._get_market_summary(args)
            elif tool_name == "get_market_metrics":
                return await self._get_market_metrics(args)
            elif tool_name == "generate_post":
                return self._generate_post(args)
            elif tool_name == "analyze_style":
                return self._analyze_style(args)
            elif tool_name == "analyze_image":
                return self._analyze_image(args)
            elif tool_name == "get_weather":
                return self._get_weather(args)
            else:
                return {"error": f"Unknown tool: {tool_name}", "tool": tool_name}
        
        except Exception as e:
            logger.error(f"Tool execution error ({tool_name}): {e}")
            return {"error": str(e), "tool": tool_name}
    
    # --- PRICE TOOLS ---
    
    async def _get_crypto_price(self, args: Dict) -> Dict:
        """Get single cryptocurrency price."""
        token_id = args.get("token_id")
        if not token_id:
            return {"error": "token_id required"}
        
        async with self._price_service_class() as service:
            result = await service.get_price(token_id)
            
            if result:
                return {
                    "success": True,
                    "data": result
                }
            else:
                return {
                    "success": False,
                    "error": f"Price not found for {token_id}"
                }
    
    async def _get_crypto_prices(self, args: Dict) -> Dict:
        """Get multiple cryptocurrency prices."""
        token_ids = args.get("token_ids", [])
        if not token_ids:
            return {"error": "token_ids required"}
        
        async with self._price_service_class() as service:
            prices = await service.get_prices(token_ids)
            
            results = []
            for token_id, data in prices.items():
                results.append({
                    "token_id": token_id,
                    "price": data.get("usd"),
                    "change_24h": data.get("usd_24h_change"),
                    "market_cap": data.get("usd_market_cap"),
                    "provider": "coingecko",
                    "timestamp": datetime.now().isoformat()
                })
            
            return {
                "success": True,
                "count": len(results),
                "data": results
            }
    
    async def _get_top_coins(self, args: Dict) -> Dict:
        """Get top coins by market cap."""
        limit = args.get("limit", 10)
        
        async with self._price_service_class() as service:
            coins = await service.get_top_coins(limit=limit)
            
            return {
                "success": True,
                "count": len(coins),
                "data": coins
            }
    
    # --- RESEARCH TOOLS ---
    
    async def _web_search(self, args: Dict) -> Dict:
        """Search the web."""
        query = args.get("query")
        count = args.get("count", 5)
        
        if not query:
            return {"error": "query required"}
        
        try:
            result = self._research_func(
                query=query,
                count=count
            )
            
            # Convert to dict format
            data = []
            if hasattr(result, 'results') and result.results:
                for r in result.results[:count]:
                    data.append({
                        "title": r.title if hasattr(r, 'title') else str(r),
                        "url": r.url if hasattr(r, 'url') else '',
                        "snippet": r.snippet if hasattr(r, 'snippet') else ''
                    })
            
            return {
                "success": True,
                "query": query,
                "count": len(data),
                "data": data
            }
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return {"error": str(e)}
    
    def _web_fetch(self, args: Dict) -> Dict:
        """Fetch URL content."""
        url = args.get("url")
        max_chars = args.get("max_chars", 5000)
        
        if not url:
            return {"error": "url required"}
        
        try:
            from web_fetch import fetch_content
            content = fetch_content(url, max_chars=max_chars)
            
            return {
                "success": True,
                "url": url,
                "content_length": len(content) if content else 0,
                "data": content[:max_chars] if content else None
            }
        except Exception as e:
            return {"error": str(e)}
    
    # --- WHALE TRACKING TOOLS ---
    
    async def _get_whale_stats(self, args: Dict) -> Dict:
        """Get whale database statistics."""
        if not self._whale_stats_func:
            return {"error": "Whale tracker not available"}
        
        try:
            stats = self._whale_stats_func()
            return {
                "success": True,
                "data": stats
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_whale_activity(self, args: Dict) -> Dict:
        """Get recent whale activity."""
        # This would require more complex implementation
        # For now, return stats with note
        return {
            "success": True,
            "message": "Whale activity tracking requires full database access",
            "note": "Implement detailed activity retrieval in whales_real.py"
        }
    
    async def _find_arbitrage(self, args: Dict) -> Dict:
        """Find arbitrage opportunities."""
        # Placeholder - full implementation would scan DEXs
        return {
            "success": True,
            "message": "Arbitrage detection running via cron",
            "note": "Check logs/whale_check.log for latest results"
        }
    
    # --- DEFI YIELD TOOLS ---
    
    def _get_yield_service(self):
        """Get or create yield service instance."""
        if not hasattr(self, '_yield_service'):
            try:
                # Try to import the yield agent
                scripts_dir = Path(__file__).parent.parent.parent / "_integrations" / "starknet-yield-agent" / "scripts"
                spec = importlib.util.spec_from_file_location("starknet_yield_agent", scripts_dir / "starknet_yield_agent.py")
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self._yield_service = module.StarknetDataService()
            except Exception as e:
                logger.warning(f"Yield service not available: {e}")
                self._yield_service = None
        return self._yield_service
    
    async def _get_defi_yields(self, args: Dict) -> Dict:
        """Get DeFi yields on Starknet."""
        service = self._get_yield_service()
        if not service:
            return {"error": "Yield service not available", "note": "Install starknet-yield-agent"}
        
        try:
            limit = args.get("limit", 5)
            protocol = args.get("protocol")
            min_tvl = args.get("min_tvl")
            risk_level = args.get("risk_level")
            
            # Get all yields
            yields = service.get_top_yields(limit=20)
            
            # Filter
            if protocol:
                yields = [y for y in yields if y["protocol"].lower() == protocol.lower()]
            if risk_level:
                yields = [y for y in yields if y["risk"].lower() == risk_level.lower()]
            if min_tvl:
                yields = [y for y in yields if float(y["tvl"].replace("$", "").replace("M", "")) * 1e6 >= min_tvl]
            
            return {
                "success": True,
                "count": len(yields[:limit]),
                "yields": yields[:limit]
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_market_summary(self, args: Dict) -> Dict:
        """Get Starknet DeFi market overview."""
        service = self._get_yield_service()
        if not service:
            return {"error": "Yield service not available"}
        
        try:
            summary = service.get_market_summary()
            return {
                "success": True,
                "data": summary
            }
        except Exception as e:
            return {"error": str(e)}
    
    # --- TRADING TOOLS ---
    
    async def _get_market_metrics(self, args: Dict) -> Dict:
        """Get on-chain market metrics."""
        token_id = args.get("token_id")
        days = args.get("days", 7)
        
        if not token_id:
            return {"error": "token_id required"}
        
        async with self._price_service_class() as service:
            # Get price data
            price = await service.get_price(token_id)
            
            # Get OHLCV
            ohlcv = await service.get_ohlcv(token_id, days=str(days))
            
            return {
                "success": True,
                "token_id": token_id,
                "period_days": days,
                "price": price,
                "ohlcv_count": len(ohlcv) if ohlcv else 0
            }
    
    # --- CONTENT TOOLS ---
    
    def _generate_post(self, args: Dict) -> Dict:
        """Generate social media post."""
        topic = args.get("topic")
        style = args.get("style", "standard")
        platform = args.get("platform", "twitter")
        max_length = args.get("max_length", 280)
        
        if not topic:
            return {"error": "topic required"}
        
        # Placeholder - would use post-generator skill
        return {
            "success": True,
            "message": "Post generation requires post-generator skill",
            "input": {
                "topic": topic,
                "style": style,
                "platform": platform
            }
        }
    
    def _analyze_style(self, args: Dict) -> Dict:
        """Analyze writing style."""
        texts = args.get("texts", [])
        
        if not texts:
            return {"error": "texts required"}
        
        # Placeholder - would use style-learner
        return {
            "success": True,
            "message": "Style analysis requires style-learner skill",
            "texts_count": len(texts)
        }
    
    # --- UTILITY TOOLS ---
    
    def _analyze_image(self, args: Dict) -> Dict:
        """Analyze image."""
        image_path = args.get("image_path")
        prompt = args.get("prompt", "Describe this image")
        
        if not image_path:
            return {"error": "image_path required"}
        
        return {
            "success": True,
            "message": "Image analysis would use configured image model",
            "image_path": image_path,
            "prompt": prompt
        }
    
    def _get_weather(self, args: Dict) -> Dict:
        """Get weather."""
        location = args.get("location")
        
        if not location:
            return {"error": "location required"}
        
        return {
            "success": True,
            "message": "Weather tool available via weather skill",
            "location": location
        }


# ============================================
# CONVENIENCE FUNCTIONS
# ============================================

async def execute_tool(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool by name (convenience function)."""
    executor = ToolExecutor()
    return await executor.execute(tool_name, args)


def execute_tool_sync(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool synchronously."""
    return asyncio.run(execute_tool(tool_name, args))


# ============================================
# MAIN (for testing)
# ============================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Tool executor for testing")
    parser.add_argument("tool", help="Tool name")
    parser.add_argument("--args", help="JSON arguments")
    
    args = parser.parse_args()
    
    tool_args = json.loads(args.args) if args.args else {}
    result = asyncio.run(execute_tool(args.tool, tool_args))
    
    print(json.dumps(result, indent=2, default=str))
