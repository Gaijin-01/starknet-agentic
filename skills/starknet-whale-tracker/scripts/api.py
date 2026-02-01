#!/usr/bin/env python3
"""
Starknet Whale Tracker - REST API Server
"""
import asyncio
import json
from aiohttp import web
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from tracker import StarknetWhaleTracker, create_tracker
from config import DEFAULT_CONFIG


class API:
    """REST API for whale tracker"""

    def __init__(self, tracker: StarknetWhaleTracker, host: str = "0.0.0.0", port: int = 8080):
        self.tracker = tracker
        self.host = host
        self.port = port
        self.app = web.Application()

        # Routes
        self.app.router.add_get("/whales", self.get_whales)
        self.app.router.add_post("/whales", self.add_whale)
        self.app.router.add_delete("/whales/{address}", self.remove_whale)
        self.app.router.add_get("/activity", self.get_activity)
        self.app.router.add_get("/arbitrage", self.get_arbitrage)
        self.app.router.add_get("/stats", self.get_stats)
        self.app.router.add_post("/webhook", self.webhook)
        self.app.router.add_get("/health", self.health)

    async def get_whales(self, request):
        """List tracked whales"""
        tag = request.query.get("tag")
        whales = self.tracker.get_whales(tag=tag)

        return web.json_response([
            {
                "address": w.address,
                "tags": w.tags,
                "notes": w.notes,
                "last_seen": w.last_seen
            }
            for w in whales
        ])

    async def add_whale(self, request):
        """Add a new whale"""
        data = await request.json()

        await self.tracker.track_wallet(
            address=data["address"],
            tags=data.get("tags", ["whale"]),
            alert_on=data.get("alert_on", ["large_transfer", "new_position"])
        )

        return web.json_response({"status": "added", "address": data["address"]})

    async def remove_whale(self, request):
        """Remove a whale"""
        address = request.match_info["address"]
        deleted = self.tracker.remove_whale(address)

        return web.json_response({"status": "deleted" if deleted else "not_found"})

    async def get_activity(self, request):
        """Get recent activity"""
        hours = int(request.query.get("hours", 24))
        address = request.query.get("address")

        activities = await self.tracker.get_activity(address=address, hours=hours)

        return web.json_response([
            {
                "wallet_address": a.wallet_address,
                "event_type": a.event_type,
                "details": a.details,
                "block_number": a.block_number,
                "timestamp": a.timestamp,
                "tx_hash": a.tx_hash
            }
            for a in activities
        ])

    async def get_arbitrage(self, request):
        """Get arbitrage opportunities"""
        opps = await self.tracker.get_arbitrage_opportunities()

        return web.json_response([
            {
                "dex_from": o.dex_from,
                "dex_to": o.dex_to,
                "token_path": o.token_path,
                "estimated_profit": o.estimated_profit,
                "profit_percent": o.profit_percent,
                "confidence": o.confidence
            }
            for o in opps
        ])

    async def get_stats(self, request):
        """Get tracker stats"""
        return web.json_response(self.tracker.get_stats())

    async def webhook(self, request):
        """Receive webhook alerts"""
        data = await request.json()
        print(f"📨 Webhook received: {data}")
        return web.json_response({"status": "received"})

    async def health(self, request):
        """Health check"""
        return web.json_response({"status": "ok"})

    async def start(self):
        """Start API server"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        print(f"🌐 API server started at http://{self.host}:{self.port}")

        return runner

    async def stop(self, runner):
        """Stop API server"""
        await runner.cleanup()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Starknet Whale Tracker API")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind")
    parser.add_argument("--rpc", default=DEFAULT_CONFIG.starknet.rpc_url, help="RPC URL")
    parser.add_argument("--db", default="./data/whales.db", help="Database path")

    args = parser.parse_args()

    tracker = create_tracker(
        rpc_url=args.rpc,
        db_path=args.db
    )

    api = API(tracker, args.host, args.port)

    async def run():
        runner = await api.start()

        try:
            while True:
                await asyncio.sleep(3600)
        except asyncio.CancelledError:
            pass
        finally:
            await api.stop(runner)

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")


if __name__ == "__main__":
    main()
