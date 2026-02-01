#!/usr/bin/env bun
/**
 * Starknet Yield Agent - TypeScript Implementation
 * x402-compatible API for DeFi yields and analytics
 */

import { serve } from "bun";

interface Pool {
  protocol: string;
  asset: string;
  apy: number;
  tvl: number;
  risk: "low" | "medium" | "high";
}

const MOCK_POOLS: Pool[] = [
  { protocol: "Ekubo", asset: "USDC", apy: 8.5, tvl: 45000000, risk: "low" },
  { protocol: "Jediswap", asset: "USDC", apy: 7.2, tvl: 32000000, risk: "low" },
  { protocol: "10k", asset: "ETH", apy: 12.0, tvl: 15000000, risk: "medium" },
  { protocol: "zkLend", asset: "STRK", apy: 25.0, tvl: 12000000, risk: "medium" },
  { protocol: "Nostra", asset: "STRK", apy: 30.0, tvl: 8000000, risk: "high" },
];

const PRICES: Record<string, number> = {
  STRK: 1.8,
  ETH: 3200,
  USDC: 1,
};

function getMarketSummary() {
  const totalTvl = MOCK_POOLS.reduce((sum, p) => sum + p.tvl, 0);
  const avgApy = MOCK_POOLS.reduce((sum, p) => sum + p.apy, 0) / MOCK_POOLS.length;
  return {
    market: {
      totalTVL: `$${(totalTvl / 1e6).toFixed(0)}M`,
      protocolCount: 5,
      avgAPY: `${avgApy.toFixed(1)}%`,
      poolCount: MOCK_POOLS.length,
    },
    chain: "Starknet",
  };
}

function getTopYields(limit = 10) {
  return [...MOCK_POOLS]
    .sort((a, b) => b.apy - a.apy)
    .slice(0, limit)
    .map((p, i) => ({
      rank: i + 1,
      ...p,
      apy: `${p.apy.toFixed(2)}%`,
      tvl: `$${(p.tvl / 1e6).toFixed(1)}M`,
    }));
}

function getProtocolDetails(name: string) {
  const pool = MOCK_POOLS.find(p => p.protocol.toLowerCase() === name.toLowerCase());
  if (!pool) return null;
  return {
    protocol: pool.protocol,
    asset: pool.asset,
    apy: pool.apy,
    tvl: pool.tvl,
    risk: pool.risk,
    recommendations: pool.risk === "low" 
      ? ["Safe for large positions", "Good for stable income"]
      : pool.risk === "medium"
      ? ["Moderate risk", "Consider smaller positions"]
      : ["High risk", "Only for speculative allocation"],
  };
}

function getRiskAnalysis() {
  const lowRisk = MOCK_POOLS.filter(p => p.risk === "low");
  const mediumRisk = MOCK_POOLS.filter(p => p.risk === "medium");
  const highRisk = MOCK_POOLS.filter(p => p.risk === "high");
  
  return {
    summary: {
      lowRiskCount: lowRisk.length,
      mediumRiskCount: mediumRisk.length,
      highRiskCount: highRisk.length,
    },
    portfolio: {
      conservative: { apy: 7.8, risk: "low", allocation: { USDC: 60, ETH: 40 } },
      balanced: { apy: 12.5, risk: "medium", allocation: { USDC: 40, ETH: 35, STRK: 25 } },
      aggressive: { apy: 22.0, risk: "high", allocation: { STRK: 60, ETH: 25, USDC: 15 } },
    },
    methodology: "Risk scores based on TVL, asset volatility, and protocol audits",
  };
}

const server = serve({
  port: 3001,
  routes: {
    "/": `🦞 Starknet Yield Agent (TS) - x402 Paid API
    
GET /api/yields-summary - FREE market overview
GET /api/top-yields - Top yields ($0.001/call)
GET /api/protocol/:name - Protocol details ($0.002/call)
GET /api/risk - Risk analysis ($0.005/call)

Dashboard: /dashboard`,
    
    "/health": { status: 200, body: JSON.stringify({ status: "healthy", agent: "starknet-yield-agent-ts" }) },
    
    "/api/yields-summary": getMarketSummary(),
    
    "/api/top-yields": (req) => {
      const url = new URL(req.url);
      const limit = parseInt(url.searchParams.get("limit") || "10");
      return { topYields: getTopYields(limit) };
    },
    
    "/api/protocol/:name": (req) => {
      const name = req.params.name;
      const details = getProtocolDetails(name);
      if (!details) return new Response(JSON.stringify({ error: "Protocol not found" }), { status: 404 });
      return details;
    },
    
    "/api/risk": getRiskAnalysis(),
    
    "/dashboard": {
      headers: { "Content-Type": "text/html" },
      body: `<!DOCTYPE html>
<html>
<head><title>Starknet Yield Agent (TS)</title>
<style>body{font-family:system-ui;max-width:800px;margin:40px auto;padding:20px}
.card{border:1px solid #ddd;padding:20px;margin:10px 0;border-radius:8px}
.metric{font-size:24px;font-weight:bold;color:#0066cc}</style>
</head>
<body>
<h1>🦞 Starknet Yield Agent (TypeScript)</h1>
<h2>Market Summary (FREE)</h2>
<div class="card">
<div class="metric">${getMarketSummary().market.totalTVL}</div>
<p>TVL across ${getMarketSummary().market.protocolCount} protocols</p>
</div>
<h2>Top Yields</h2>
<table>
<tr><th>#</th><th>Protocol</th><th>Asset</th><th>APY</th><th>Risk</th></tr>
${getTopYields(5).map(y => `<tr><td>${y.rank}</td><td>${y.protocol}</td><td>${y.asset}</td><td>${y.apy}</td><td>${y.risk}</td></tr>`).join("")}
</table>
</body>
</html>`,
    },
  },
});

console.log(`🦞 Starknet Yield Agent (TS) running on port 3001`);
