#!/usr/bin/env bun
/**
 * x402 Agents - Payment Gateway
 * Micropayment verification and routing for AI agents
 */

import { serve } from "bun";

interface PaymentProof {
  amount: number;
  currency: string;
  recipient: string;
  signature: string;
  timestamp: number;
}

interface Endpoint {
  path: string;
  price: number;
  currency: string;
  description: string;
}

const ENDPOINTS: Endpoint[] = [
  { path: "/api/free", price: 0, currency: "USD", description: "Free tier endpoint" },
  { path: "/api/basic", price: 0.001, currency: "USD", description: "Basic analytics" },
  { path: "/api/premium", price: 0.005, currency: "USD", description: "Premium features" },
  { path: "/api/enterprise", price: 0.02, currency: "USD", description: "Enterprise access" },
];

// Mock payment verification
function verifyPayment(proof: PaymentProof): boolean {
  // In production: verify on-chain or via Lightning/USDC
  if (!proof.signature || proof.amount <= 0) return false;
  if (Date.now() - proof.timestamp > 3600000) return false; // 1 hour expiry
  return true;
}

function getPaymentRequired(endpoint: string): { price: number; currency: string } {
  const ep = ENDPOINTS.find(e => e.path === endpoint);
  return { price: ep?.price || 0, currency: ep?.currency || "USD" };
}

function getBalance(address: string): { balance: number; currency: string } {
  // Mock balance check
  return { balance: 10.0, currency: "USD" };
}

function createInvoice(
  recipient: string,
  amount: number,
  description: string
): { invoiceId: string; amount; description; expiry } {
  return {
    invoiceId: `inv_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`,
    amount,
    description,
    expiry: Date.now() + 3600000, // 1 hour
  };
}

const server = serve({
  port: 3002,
  routes: {
    "/": `💰 x402 Agents - Payment Gateway

Payment verification for AI agent micropayments

ENDPOINTS:
GET  /api/health              - Health check
GET  /api/endpoints           - List all endpoints + prices
POST /api/verify              - Verify payment proof
GET  /api/balance/:address    - Check balance
POST /api/invoice             - Create payment invoice
GET  /api/wallet              - Wallet info
GET  /dashboard               - Web dashboard`,
    
    "/api/health": { status: "healthy", service: "x402-agents" },
    
    "/api/endpoints": ENDPOINTS,
    
    "/api/verify": async (req) => {
      try {
        const body = await req.json();
        const valid = verifyPayment(body);
        return {
          valid,
          message: valid ? "Payment verified" : "Invalid payment proof",
        };
      } catch {
        return new Response(JSON.stringify({ error: "Invalid JSON" }), { status: 400 });
      }
    },
    
    "/api/balance/:address": (req) => {
      const address = req.params.address || "default";
      return getBalance(address);
    },
    
    "/api/invoice": async (req) => {
      try {
        const { recipient, amount, description } = await req.json();
        return createInvoice(recipient || "anon", amount || 0.001, description || "Service");
      } catch {
        return new Response(JSON.stringify({ error: "Invalid request body" }), { status: 400 });
      }
    },
    
    "/api/wallet": {
      address: "0x1234567890abcdef... (mock)",
      currency: "USDC",
      status: "active",
    },
    
    "/dashboard": {
      headers: { "Content-Type": "text/html" },
      body: `<!DOCTYPE html>
<html>
<head><title>x402 Agents Payment Gateway</title>
<style>body{font-family:system-ui;max-width:800px;margin:40px auto;padding:20px}
.endpoint{background:#f5f5f5;padding:10px;margin:5px 0;border-radius:4px;font-family:monospace}
.price{color:#0066cc;font-weight:bold}</style>
</head>
<body>
<h1>💰 x402 Agents Payment Gateway</h1>
<h2>Available Endpoints</h2>
${ENDPOINTS.map(e => `<div class="endpoint">${e.path} - <span class="price">$${e.price}</span> - ${e.description}</div>`).join("")}
<h2>Quick Links</h2>
<ul>
<li><a href="/api/health">Health Check</a></li>
<li><a href="/api/endpoints">All Endpoints</a></li>
<li><a href="/api/balance/default">Check Balance</a></li>
</ul>
</body>
</html>`,
    },
  },
});

console.log(`💰 x402 Agents running on port 3002`);
