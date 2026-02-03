#!/usr/bin/env python3
"""
Starknet Yield Agent - x402 Paid API
Real-time DeFi yields, protocol analytics, and risk analysis

Based on langoustine69's x402 agent pattern
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from aiohttp import web
import aiohttp

# === CONFIGURATION ===

@dataclass
class Config:
    name: str = "starknet-yield-agent"
    version: str = "1.0.0"
    port: int = int(os.getenv("PORT", "3000"))
    rpc_url: str = os.getenv("STARKNET_RPC_URL", "https://rpc.starknet.lava.build:443")
    
    # x402 Payment config (mock - real implementation uses @lucid-agents/payments)
    payment_enabled: bool = os.getenv("X402_ENABLED", "false").lower() == "true"
    
    # Price per call (in microunits, 1000 = $0.001)
    PRICES = {
        "market-summary": 0,        # FREE
        "top-yields": 1000,         # $0.001
        "protocol-details": 2000,    # $0.002
        "rwa-opportunities": 3000,   # $0.003
        "yield-compare": 2000,      # $0.002
        "risk-analysis": 5000,       # $0.005
        "whale-activity": 3000,     # $0.003
        "arbitrage-alerts": 4000,    # $0.004
        "full-report": 10000,        # $0.01
    }


# === DATA MODELS ===

@dataclass
class Pool:
    asset: str
    apy: float
    tvl: float
    risk: str  # low, medium, high
    protocol: str
    chain: str = "Starknet"

@dataclass  
class Protocol:
    name: str
    chain: str
    category: str
    pools: List[Pool]
    tvl: float = 0
    
    def __post_init__(self):
        self.tvl = sum(p.tvl for p in self.pools)


# === STARKNET DATA (Mock - would fetch from real sources) ===

STARKNET_POOLS = [
    # Ekubo
    Pool(asset="ETH", apy=0.12, tvl=50000000, risk="low", protocol="Ekubo"),
    Pool(asset="STRK", apy=0.25, tvl=15000000, risk="medium", protocol="Ekubo"),
    Pool(asset="USDC", apy=0.08, tvl=25000000, risk="low", protocol="Ekubo"),
    
    # Jediswap
    Pool(asset="ETH", apy=0.10, tvl=30000000, risk="low", protocol="Jediswap"),
    Pool(asset="USDC", apy=0.07, tvl=18000000, risk="low", protocol="Jediswap"),
    Pool(asset="STRK", apy=0.22, tvl=8000000, risk="medium", protocol="Jediswap"),
    
    # 10k
    Pool(asset="ETH", apy=0.11, tvl=20000000, risk="low", protocol="10k"),
    Pool(asset="USDT", apy=0.09, tvl=12000000, risk="low", protocol="10k"),
    
    # zkLend
    Pool(asset="USDC", apy=0.10, tvl=45000000, risk="low", protocol="zkLend"),
    Pool(asset="ETH", apy=0.14, tvl=35000000, risk="low", protocol="zkLend"),
    Pool(asset="STRK", apy=0.30, tvl=12000000, risk="high", protocol="zkLend"),
    
    # Nostra
    Pool(asset="USDC", apy=0.12, tvl=60000000, risk="low", protocol="Nostra"),
    Pool(asset="ETH", apy=0.15, tvl=40000000, risk="low", protocol="Nostra"),
    Pool(asset="DAI", apy=0.09, tvl=15000000, risk="low", protocol="Nostra"),
]


# === DATA SERVICE ===

class StarknetDataService:
    """Fetch and process Starknet DeFi data"""
    
    def __init__(self, rpc_url: str = "https://rpc.starknet.lava.build:443"):
        self.rpc_url = rpc_url
        self.protocols = self._build_protocols()
    
    def _build_protocols(self) -> List[Protocol]:
        """Group pools into protocols"""
        pools_by_protocol = {}
        for pool in STARKNET_POOLS:
            if pool.protocol not in pools_by_protocol:
                pools_by_protocol[pool.protocol] = []
            pools_by_protocol[pool.protocol].append(pool)
        
        # Categorize
        categories = {
            "Ekubo": "AMM",
            "Jediswap": "AMM", 
            "10k": "AMM",
            "zkLend": "Lending",
            "Nostra": "Lending",
        }
        
        return [
            Protocol(
                name=protocol,
                chain="Starknet",
                category=categories.get(protocol, "Other"),
                pools=pools
            )
            for protocol, pools in pools_by_protocol.items()
        ]
    
    def get_market_summary(self) -> Dict:
        """FREE: Basic market overview"""
        total_tvl = sum(p.tvl for p in STARKNET_POOLS)
        avg_apy = sum(p.apy for p in STARKNET_POOLS) / len(STARKNET_POOLS)
        
        return {
            "market": {
                "totalTVL": f"${total_tvl / 1e6:.0f}M",
                "protocolCount": len(self.protocols),
                "avgAPY": f"{avg_apy * 100:.2f}%",
                "poolCount": len(STARKNET_POOLS),
                "lastUpdated": datetime.utcnow().isoformat(),
            },
            "chain": "Starknet",
            "category": "DeFi",
        }
    
    def get_top_yields(
        self, 
        limit: int = 10,
        min_tvl: float = 0,
        risk: Optional[str] = None
    ) -> List[Dict]:
        """PAID: Top yields sorted by APY"""
        filtered = [
            p for p in STARKNET_POOLS
            if p.tvl >= min_tvl and (risk is None or p.risk == risk)
        ]
        sorted_pools = sorted(filtered, key=lambda p: p.apy, reverse=True)[:limit]
        
        return [
            {
                "rank": i + 1,
                "protocol": p.protocol,
                "asset": p.asset,
                "apy": f"{p.apy * 100:.2f}%",
                "tvl": f"${p.tvl / 1e6:.1f}M",
                "chain": p.chain,
                "risk": p.risk,
            }
            for i, p in enumerate(sorted_pools)
        ]
    
    def get_protocol_details(self, name: str) -> Optional[Dict]:
        """PAID: Deep dive on specific protocol"""
        protocol = next((p for p in self.protocols if name.lower() in p.name.lower()), None)
        if not protocol:
            return None
        
        return {
            "protocol": {
                "name": protocol.name,
                "chain": protocol.chain,
                "category": protocol.category,
                "totalTVL": f"${protocol.tvl / 1e6:.1f}M",
                "poolCount": len(protocol.pools),
            },
            "pools": [
                {
                    "asset": p.asset,
                    "apy": f"{p.apy * 100:.2f}%",
                    "tvl": f"${p.tvl / 1e6:.1f}M",
                    "risk": p.risk,
                }
                for p in sorted(protocol.pools, key=lambda x: x.apy, reverse=True)
            ],
            "recommendations": {
                "bestYield": {
                    "asset": max(protocol.pools, key=lambda p: p.apy).asset,
                    "apy": f"{max(protocol.pools, key=lambda p: p.apy).apy * 100:.2f}%",
                },
                "safestOption": {
                    "asset": min(protocol.pools, key=lambda p: p.risk).asset,
                    "risk": min(protocol.pools, key=lambda p: p.risk).risk,
                } if any(p.risk == "low" for p in protocol.pools) else None,
            },
        }
    
    def get_rwa_opportunities(self) -> Dict:
        """PAID: RWA opportunities (mock for Starknet)"""
        return {
            "rwaMarket": {
                "totalOpportunities": 3,
                "note": "Starknet RWA is emerging",
                "trend": "growing",
            },
            "onChainRWA": [
                {
                    "protocol": "Ekubo",
                    "type": "Tokenized Treasuries",
                    "apy": "8-12%",
                    "tvl": "$2M",
                },
                {
                    "protocol": "zkLend", 
                    "type": "Real Estate",
                    "apy": "6-10%",
                    "tvl": "$1M",
                },
            ],
        }
    
    def compare_yields(self, asset: str, chains: List[str] = None) -> Dict:
        """PAID: Compare yields for specific asset"""
        comparisons = [p for p in STARKNET_POOLS if asset.upper() in p.asset.upper()]
        sorted_comp = sorted(comparisons, key=lambda p: p.apy, reverse=True)
        
        return {
            "asset": asset,
            "comparisons": [
                {
                    "protocol": p.protocol,
                    "chain": p.chain,
                    "apy": f"{p.apy * 100:.2f}%",
                    "tvl": f"${p.tvl / 1e6:.0f}M",
                    "risk": p.risk,
                }
                for p in sorted_comp
            ],
            "recommendation": {
                "highestYield": {
                    "protocol": sorted_comp[0].protocol if sorted_comp else None,
                    "apy": f"{sorted_comp[0].apy * 100:.2f}%" if sorted_comp else None,
                } if sorted_comp else None,
            },
        }
    
    def get_risk_analysis(self) -> Dict:
        """PAID: Risk-adjusted yield analysis"""
        risk_multipliers = {"low": 1.0, "medium": 0.7, "high": 0.4}
        risk_free_rate = 4.5  # US 10Y Treasury
        
        analyzed = [
            {
                "protocol": p.protocol,
                "asset": p.asset,
                "rawAPY": p.apy * 100,
                "riskAdjustedAPY": p.apy * 100 * risk_multipliers.get(p.risk, 0.5),
                "risk": p.risk,
                "tvl": p.tvl,
            }
            for p in STARKNET_POOLS
        ]
        
        by_risk_adjusted = sorted(analyzed, key=lambda x: x["riskAdjustedAPY"], reverse=True)
        
        return {
            "methodology": {
                "riskMultipliers": risk_multipliers,
                "riskFreeRate": f"{risk_free_rate}%",
                "note": "Risk-adjusted APY = APY * risk multiplier",
            },
            "topRiskAdjusted": by_risk_adjusted[:10],
            "portfolioSuggestion": {
                "conservative": [a["protocol"] for a in by_risk_adjusted if a["risk"] == "low"][:3],
                "balanced": [a["protocol"] for a in by_risk_adjusted if a["risk"] != "high"][:5],
                "aggressive": [a["protocol"] for a in by_risk_adjusted[:5]],
            },
        }


# === HTTP HANDLERS ===

class StarknetYieldApp:
    """x402-compatible HTTP server with error handling"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.data = None
        self._init_data_service()
        self.app = web.Application()
        self._setup_routes()
    
    def _init_data_service(self):
        """Initialize data service with error handling"""
        try:
            self.data = StarknetDataService(self.config.rpc_url)
            print(f"✅ Data service initialized with {len(STARKNET_POOLS)} pools")
        except Exception as e:
            print(f"⚠️ Data service initialization warning: {e}")
            # Continue with mock data
            self.data = StarknetDataService()
    
    def _setup_routes(self):
        self.app.router.add_get("/", self.handle_root)
        self.app.router.add_get("/health", self.handle_health)
        
        # x402 entrypoints
        self.app.router.add_get("/api/yields-summary", self.handle_summary)
        self.app.router.add_get("/api/top-yields", self.handle_top_yields)
        self.app.router.add_get("/api/protocol/{name}", self.handle_protocol)
        self.app.router.add_get("/api/rwa", self.handle_rwa)
        self.app.router.add_get("/api/compare", self.handle_compare)
        self.app.router.add_get("/api/risk", self.handle_risk)
        
        # Web dashboard
        self.app.router.add_get("/dashboard", self.handle_dashboard)
    
    async def handle_root(self, request):
        return web.Response(
            text="🦞 Starknet Yield Agent - x402 Paid API\n\n"
                 "GET /api/yields-summary - FREE market overview\n"
                 "GET /api/top-yields - Top yields ($0.001/call)\n"
                 "GET /api/protocol/{name} - Protocol details ($0.002/call)\n"
                 "GET /api/rwa - RWA opportunities ($0.003/call)\n"
                 "GET /api/compare?asset=USDC - Yield comparison ($0.002/call)\n"
                 "GET /api/risk - Risk analysis ($0.005/call)\n\n"
                 "See /dashboard for web interface"
        )
    
    async def handle_health(self, request):
        return web.json_response({
            "status": "healthy", 
            "agent": self.config.name,
            "version": self.config.version,
            "data_loaded": self.data is not None
        })
    
    async def handle_summary(self, request):
        """FREE endpoint"""
        try:
            return web.json_response(self.data.get_market_summary())
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_top_yields(self, request):
        """PAID: $0.001"""
        try:
            limit = int(request.query.get("limit", 10))
            min_tvl = float(request.query.get("minTvl", 0))
            risk = request.query.get("risk")
            
            result = self.data.get_top_yields(limit, min_tvl, risk)
            return web.json_response({"topYields": result})
        except ValueError as e:
            return web.json_response({"error": f"Invalid parameter: {e}"}, status=400)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_protocol(self, request):
        """PAID: $0.002"""
        try:
            name = request.match_info["name"]
            if not name or len(name) < 2:
                return web.json_response({"error": "Protocol name required"}, status=400)
            
            result = self.data.get_protocol_details(name)
            
            if not result:
                return web.json_response({"error": "Protocol not found"}, status=404)
            
            return web.json_response(result)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_rwa(self, request):
        """PAID: $0.003"""
        try:
            return web.json_response(self.data.get_rwa_opportunities())
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_compare(self, request):
        """PAID: $0.002"""
        try:
            asset = request.query.get("asset", "USDC")
            if not asset:
                return web.json_response({"error": "Asset parameter required"}, status=400)
            
            return web.json_response(self.data.compare_yields(asset))
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_risk(self, request):
        """PAID: $0.005"""
        try:
            return web.json_response(self.data.get_risk_analysis())
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_dashboard(self, request):
        """Simple web dashboard with error handling"""
        try:
            summary = self.data.get_market_summary()
            top_yields = self.data.get_top_yields(5)
        except Exception as e:
            summary = {"market": {"totalTVL": "N/A", "protocolCount": 0}}
            top_yields = []
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Starknet Yield Agent</title>
    <style>
        body {{ font-family: system-ui; max-width: 800px; margin: 40px auto; padding: 20px; }}
        .card {{ border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 8px; }}
        .metric {{ font-size: 24px; font-weight: bold; color: #0066cc; }}
        .endpoint {{ background: #f5f5f5; padding: 10px; margin: 5px 0; font-family: monospace; }}
        .price {{ color: #666; font-size: 14px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background: #f5f5f5; }}
    </style>
</head>
<body>
    <h1>🦞 Starknet Yield Agent</h1>
    <p>Version: {self.config.version}</p>
    
    <div class="card">
        <h2>Market Summary (FREE)</h2>
        <div class="metric">{summary.get('market', {}).get('totalTVL', 'N/A')}</div>
        <p>TVL across {summary.get('market', {}).get('protocolCount', 0)} protocols</p>
    </div>
    
    <div class="card">
        <h2>Top Yields</h2>
        <table>
            <tr><th>#</th><th>Protocol</th><th>Asset</th><th>APY</th></tr>
            {"".join(f"<tr><td>{i+1}</td><td>{y.get('protocol', 'N/A')}</td><td>{y.get('asset', 'N/A')}</td><td>{y.get('apy', 'N/A')}</td></tr>" for i, y in enumerate(top_yields[:5]))}
        </table>
    </div>
    
    <h2>API Endpoints</h2>
    <div class="endpoint">GET /api/yields-summary - FREE</div>
    <div class="endpoint">GET /api/top-yields - $0.001/call</div>
    <div class="endpoint">GET /api/protocol/{{name}} - $0.002/call</div>
    <div class="endpoint">GET /api/rwa - $0.003/call</div>
    <div class="endpoint">GET /api/compare?asset=USDC - $0.002/call</div>
    <div class="endpoint">GET /api/risk - $0.005/call</div>
</body>
</html>
        """
        return web.Response(text=html, content_type="text/html")
    
    async def run(self):
        """Start the server with error handling"""
        try:
            runner = web.AppRunner(self.app)
            await runner.setup()
            site = web.TCPSite(runner, "0.0.0.0", self.config.port)
            await site.start()
            print(f"🦞 Starknet Yield Agent running on port {self.config.port}")
            return runner
        except OSError as e:
            if e.errno == 98:  # Address already in use
                print(f"⚠️ Port {self.config.port} already in use, trying {self.config.port + 1}")
                self.config.port += 1
                return await self.run()
            raise


# === MAIN ===

async def main():
    config = Config()
    app = StarknetYieldApp(config)
    runner = await app.run()
    
    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
