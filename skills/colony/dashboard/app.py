"""
Web Dashboard for Starknet Intelligence Colony
===============================================
Flask-based web interface for real-time monitoring.
"""

import asyncio
import json
import logging
from datetime import datetime
from flask import Flask, jsonify, render_template

from ..shared_state import shared_state
from ..config import DASHBOARD

logger = logging.getLogger(__name__)


async def get_security_data():
    """Get security data for dashboard"""
    try:
        from ..agents.security_agent import security_agent
        return await security_agent.get_security_dashboard()
    except ImportError:
        return {
            "error": "Security agent not available",
            "protocols_monitored": 0,
            "average_score": 0
        }


def create_app():
    """Create Flask application"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = DASHBOARD.SECRET_KEY
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    
    # Event loop for async operations
    _loop = None
    
    def get_loop():
        nonlocal _loop
        if _loop is None or _loop.is_closed():
            _loop = asyncio.new_event_loop()
            _loop.run_until_complete(shared_state.load_state())
        return _loop
    
    @app.route('/')
    def index():
        """Render dashboard"""
        return render_template('index.html')
    
    @app.route('/api/status')
    async def api_status():
        """Get full colony status"""
        try:
            # Get market summary from market agent if available
            market_data = await shared_state.get_market_data()
            arbitrage = await shared_state.get_arbitrage_opportunities()
            whales = await shared_state.get_whale_movements()
            research = await shared_state.get_research_reports(limit=5)
            content = await shared_state.get_content(limit=10)
            alerts = await shared_state.get_alerts(limit=10)
            
            # Get security data
            security_data = await get_security_data()
            
            return jsonify({
                "market_data": {
                    "total_tvl": 15000000,  # Sample data
                    "total_volume_24h": 2300000,
                    "arbitrage_count": len(arbitrage),
                    "whale_count": len(whales),
            
            # Get agent status
            agent_status = await shared_state.get_agent_status()
            
            return jsonify({
                "market_data": {
                    "total_tvl": 15000000,  # Sample data
                    "total_volume_24h": 2300000,
                    "arbitrage_count": len(arbitrage),
                    "whale_count": len(whales),
                    "prices": market_data.to_dict() if market_data else {},
                },
                "arbitrage": [a.to_dict() for a in arbitrage[:10]],
                "whales": [w.to_dict() for w in whales[:20]],
                "research": [r.to_dict() for r in research],
                "content": [c.to_dict() for c in content],
                "alerts": alerts,
                "agents": agent_status,
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error(f"Status API error: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/market')
    async def api_market():
        """Get market data only"""
        try:
            market_data = await shared_state.get_market_data()
            arbitrage = await shared_state.get_arbitrage_opportunities()
            
            return jsonify({
                "prices": market_data.to_dict() if market_data else {},
                "arbitrage": [a.to_dict() for a in arbitrage[:10]],
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/whales')
    async def api_whales():
        """Get whale activity"""
        try:
            whales = await shared_state.get_whale_movements(limit=50)
            return jsonify({
                "movements": [w.to_dict() for w in whales],
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/research')
    async def api_research():
        """Get research reports"""
        try:
            reports = await shared_state.get_research_reports(limit=10)
            return jsonify({
                "reports": [r.to_dict() for r in reports],
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/content')
    async def api_content():
        """Get generated content"""
        try:
            content = await shared_state.get_content(limit=20)
            return jsonify({
                "content": [c.to_dict() for c in content],
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/security')
    async def api_security():
        """Get security dashboard data"""
        try:
            data = await get_security_data()
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/security/<protocol>')
    async def api_protocol_security(protocol: str):
        """Get security report for specific protocol"""
        try:
            from ..agents.security_agent import security_agent
            report = await security_agent.scan_protocol(protocol)
            return jsonify(report.to_dict())
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/alerts')
    async def api_alerts():
        """Get recent alerts"""
        try:
            alerts = await shared_state.get_alerts(limit=20)
            return jsonify({
                "alerts": alerts,
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/trigger/<action>', methods=['POST'])
    async def api_trigger(action):
        """Trigger an action"""
        try:
            if action == "refresh":
                await shared_state.save_state()
                return jsonify({"success": True, "message": "State saved"})
            elif action == "clear":
                await shared_state.clear_stale_data()
                return jsonify({"success": True, "message": "Stale data cleared"})
            else:
                return jsonify({"error": "Unknown action"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return app


# Create app instance
app = create_app()


if __name__ == '__main__':
    print("Starting Starknet Colony Dashboard...")
    print(f"Open http://{DASHBOARD.HOST}:{DASHBOARD.PORT}")
    app.run(
        host=DASHBOARD.HOST,
        port=DASHBOARD.PORT,
        debug=DASHBOARD.DEBUG
    )
