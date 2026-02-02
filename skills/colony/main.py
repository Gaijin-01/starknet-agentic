"""
Main Entry Point for Starknet Intelligence Colony
==================================================

A multi-agent system that monitors, analyzes, and reports on the
Starknet DeFi ecosystem through three specialized agents:

1. Market Intelligence Agent - Real-time market monitoring
2. Research Agent - Deep protocol analysis
3. Content Agent - Automated report generation

Usage:
    python3 main.py                    # Run all agents
    python3 main.py --market           # Market agent only
    python3 main.py --research         # Research agent only
    python3 main.py --content          # Content agent only

Requirements:
    - Python 3.10+
    - Dependencies from requirements.txt
    - API keys in .env (CoinGecko, etc.)
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import LOGGING, BASE_DIR
from orchestrator import orchestrator
from shared_state import shared_state

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOGGING.LEVEL),
    format=LOGGING.FORMAT
)

logger = logging.getLogger(__name__)


async def main():
    """Main entry point"""
    print("""
    🧠 Starknet Intelligence Colony
    ═══════════════════════════════════
    
    Multi-Agent DeFi Intelligence System
    
    Starting agents...
    """)
    
    # Import agents
    from agents.market_agent import market_agent
    from agents.research_agent import research_agent
    from agents.content_agent import content_agent
    from agents.security_agent import security_agent  # NEW
    
    # Register agents with orchestrator
    orchestrator.register_agent("market", market_agent)
    orchestrator.register_agent("research", research_agent)
    orchestrator.register_agent("content", content_agent)
    orchestrator.register_agent("security", security_agent)  # NEW
    
    logger.info("All agents registered")
    
    try:
        # Run orchestrator (runs forever until shutdown)
        await orchestrator.run(run_forever=True)
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await orchestrator.shutdown()
        await shared_state.save_state()
        print("\n👋 Colony shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
