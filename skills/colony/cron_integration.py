"""
Cron Integration for Starknet Intelligence Colony
==================================================
Scheduled task automation for reports and updates.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import REPORTS, AGENTS
from shared_state import shared_state
from orchestrator import orchestrator

logger = logging.getLogger(__name__)


async def run_hourly_tasks():
    """Run all hourly tasks"""
    logger.info("Running hourly tasks...")
    
    try:
        # Generate reports
        await generate_market_report()
        await generate_whale_report()
        await generate_content_report()
        
        logger.info("Hourly tasks complete")
        
    except Exception as e:
        logger.error(f"Hourly tasks error: {e}")


async def run_daily_tasks():
    """Run daily tasks"""
    logger.info("Running daily tasks...")
    
    try:
        # Deep research
        await generate_research_report()
        
        # Clear old data
        await shared_state.clear_stale_data(max_age_hours=48)
        
        logger.info("Daily tasks complete")
        
    except Exception as e:
        logger.error(f"Daily tasks error: {e}")


async def generate_market_report():
    """Generate market intelligence report"""
    from agents.market_agent import market_agent
    summary = await market_agent.get_market_summary()
    
    report = {
        "type": "market",
        "timestamp": datetime.utcnow().isoformat(),
        "data": summary.to_dict()
    }
    
    # Save report
    timestamp = datetime.utcnow().strftime(REPORTS.DATE_FORMAT)
    report_path = REPORTS.OUTPUT_DIR / f"market_{timestamp}.json"
    
    import json
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Market report saved: {report_path}")


async def generate_whale_report():
    """Generate whale activity report"""
    from clients.whale_db_client import whale_db_client
    
    summary = await whale_db_client.get_whale_movement_summary(hours=24)
    
    report = {
        "type": "whale",
        "timestamp": datetime.utcnow().isoformat(),
        "data": summary
    }
    
    # Save report
    timestamp = datetime.utcnow().strftime(REPORTS.DATE_FORMAT)
    report_path = REPORTS.OUTPUT_DIR / f"whale_{timestamp}.json"
    
    import json
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Whale report saved: {report_path}")


async def generate_research_report():
    """Generate deep research report"""
    from agents.research_agent import research_agent
    
    # Research a topic
    topic = AGENTS.RESEARCH_TOPICS[0]
    report = await research_agent.run_research_once(topic)
    
    # Save report
    timestamp = datetime.utcnow().strftime(REPORTS.DATE_FORMAT)
    report_path = REPORTS.OUTPUT_DIR / f"research_{timestamp}.json"
    
    import json
    with open(report_path, 'w') as f:
        json.dump(report.to_dict(), f, indent=2)
    
    logger.info(f"Research report saved: {report_path}")


async def generate_content_report():
    """Generate content report"""
    from agents.content_agent import content_agent
    
    # Get recent content
    content = await shared_state.get_content(limit=50)
    
    report = {
        "type": "content",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "total_pieces": len(content),
            "by_type": {},
            "by_platform": {}
        }
    }
    
    # Count by type and platform
    for c in content:
        report["data"]["by_type"][c.type] = report["data"]["by_type"].get(c.type, 0) + 1
        report["data"]["by_platform"][c.platform] = report["data"]["by_platform"].get(c.platform, 0) + 1
    
    # Save report
    timestamp = datetime.utcnow().strftime(REPORTS.DATE_FORMAT)
    report_path = REPORTS.OUTPUT_DIR / f"content_{timestamp}.json"
    
    import json
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Content report saved: {report_path}")


async def run_scheduler():
    """Main scheduler loop"""
    logger.info("Starting scheduler...")
    
    await shared_state.load_state()
    
    try:
        while True:
            now = datetime.utcnow()
            hour = now.hour
            
            # Run hourly tasks every hour
            await run_hourly_tasks()
            
            # Run daily tasks at 8 AM UTC
            if hour == 8:
                await run_daily_tasks()
            
            # Wait 1 hour
            await asyncio.sleep(3600)
            
    except asyncio.CancelledError:
        logger.info("Scheduler cancelled")
    finally:
        await shared_state.save_state()


if __name__ == "__main__":
    print("""
    ⚙️  Starknet Colony Scheduler
    ═══════════════════════════════
    
    Running scheduled tasks...
    """)
    
    try:
        asyncio.run(run_scheduler())
    except KeyboardInterrupt:
        print("\n👋 Scheduler stopped")
