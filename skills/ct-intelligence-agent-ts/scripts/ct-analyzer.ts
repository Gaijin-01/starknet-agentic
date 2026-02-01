#!/usr/bin/env bun
/**
 * CT Intelligence Agent - TypeScript
 * Crypto Twitter analytics, sentiment analysis, trend detection
 */

import { serve } from "bun";

interface Tweet {
  id: string;
  author: string;
  content: string;
  timestamp: number;
  engagement: { likes: number; retweets: number; replies: number };
  sentiment: "bullish" | "bearish" | "neutral";
  topics: string[];
}

interface Trend {
  topic: string;
  volume: number;
  sentiment: number; // -1 to 1
  velocity: number; // growth rate
}

const MOCK_TWEETS: Tweet[] = [
  {
    id: "1",
    author: "VitalikButerin",
    content: "ZK rollups are the future of Ethereum scaling",
    timestamp: Date.now() - 3600000,
    engagement: { likes: 2500, retweets: 450, replies: 120 },
    sentiment: "bullish",
    topics: ["ZK", " Ethereum", " scaling"],
  },
  {
    id: "2",
    author: "hasu",
    content: "Starknet's approach to account abstraction is underrated",
    timestamp: Date.now() - 7200000,
    engagement: { likes: 890, retweets: 150, replies: 45 },
    sentiment: "bullish",
    topics: ["Starknet", "AA", "account abstraction"],
  },
  {
    id: "3",
    author: "0xfoobar",
    content: "Another day, another L2 drama",
    timestamp: Date.now() - 10800000,
    engagement: { likes: 320, retweets: 80, replies: 200 },
    sentiment: "neutral",
    topics: ["L2", "drama"],
  },
];

const MOCK_TRENDS: Trend[] = [
  { topic: "Starknet", volume: 15000, sentiment: 0.7, velocity: 1.2 },
  { topic: "ZK-Rollups", volume: 12000, sentiment: 0.8, velocity: 1.5 },
  { topic: "STRK", volume: 8000, sentiment: 0.5, velocity: 0.9 },
  { topic: "Account Abstraction", volume: 6500, sentiment: 0.6, velocity: 1.1 },
  { topic: "DeFi", volume: 5000, sentiment: 0.4, velocity: 0.7 },
];

function analyzeSentiment(text: string): "bullish" | "bearish" | "neutral" {
  const bullish = ["bullish", "moon", "up", "growth", "future", "innovation"];
  const bearish = ["bearish", "crash", "down", "scam", "overpriced", "failed"];
  
  const lower = text.toLowerCase();
  if (bullish.some(w => lower.includes(w))) return "bullish";
  if (bearish.some(w => lower.includes(w))) return "bearish";
  return "neutral";
}

function getFeed(limit = 20) {
  return MOCK_TWEETS.slice(0, limit);
}

function searchTweets(query: string) {
  const lower = query.toLowerCase();
  return MOCK_TWEETS.filter(t => 
    t.content.toLowerCase().includes(lower) || 
    t.topics.some(t => t.toLowerCase().includes(lower))
  );
}

function getTrends(limit = 10) {
  return [...MOCK_TRENDS].sort((a, b) => b.volume - a.volume).slice(0, limit);
}

function getSentimentIndex(): { overall: number; topics: Record<string, number> } {
  const topics: Record<string, number> = {};
  MOCK_TWEETS.forEach(t => {
    t.topics.forEach(topic => {
      topics[topic] = (topics[topic] || 0) + (t.sentiment === "bullish" ? 1 : t.sentiment === "bearish" ? -1 : 0);
    });
  });
  return {
    overall: 0.55, // Slightly bullish
    topics,
  };
}

function getInfluencerScore(username: string): { score: number; followers: number; impact: string } {
  const scores: Record<string, { score: number; followers: number }> = {
    "VitalikButerin": { score: 98, followers: 5000000 },
    "hasu": { score: 85, followers: 250000 },
    "0xfoobar": { score: 82, followers: 180000 },
  };
  const data = scores[username] || { score: 50, followers: 10000 };
  let impact = "low";
  if (data.score > 90 || data.followers > 1000000) impact = "very high";
  else if (data.score > 75 || data.followers > 100000) impact = "high";
  else if (data.score > 60) impact = "medium";
  return { ...data, impact };
}

const server = serve({
  port: 3003,
  routes: {
    "/": `🐦 CT Intelligence Agent (TS) - Crypto Twitter Analytics

ENDPOINTS:
GET  /api/feed              - Timeline of tweets
GET  /api/search?q=         - Search tweets
GET  /api/trends            - Trending topics
GET  /api/sentiment         - Market sentiment index
GET  /api/influencer/:name  - Influencer score
GET  /dashboard             - Web dashboard`,
    
    "/api/feed": (req) => {
      const url = new URL(req.url);
      const limit = parseInt(url.searchParams.get("limit") || "20");
      return { feed: getFeed(limit) };
    },
    
    "/api/search": (req) => {
      const url = new URL(req.url);
      const query = url.searchParams.get("q") || "";
      return { results: searchTweets(query), query };
    },
    
    "/api/trends": (req) => {
      const url = new URL(req.url);
      const limit = parseInt(url.searchParams.get("limit") || "10");
      return { trends: getTrends(limit) };
    },
    
    "/api/sentiment": getSentimentIndex(),
    
    "/api/influencer/:name": (req) => {
      const name = req.params.name || "unknown";
      return getInfluencerScore(name);
    },
    
    "/dashboard": {
      headers: { "Content-Type": "text/html" },
      body: `<!DOCTYPE html>
<html>
<head><title>CT Intelligence Agent</title>
<style>body{font-family:system-ui;max-width:800px;margin:40px auto;padding:20px}
.card{border:1px solid #ddd;padding:15px;margin:10px 0;border-radius:8px}
.tweet{bborder-left:3px solid #1da1f2;padding-left:15px;margin:10px 0}
.sentiment{color:#0066cc;font-weight:bold}</style>
</head>
<body>
<h1>🐦 CT Intelligence Agent (TypeScript)</h1>
<h2>Market Sentiment: <span class="sentiment">${(getSentimentIndex().overall * 100).toFixed(0)}% Bullish</span></h2>
<h2>Trending Topics</h2>
${getTrends(5).map(t => `<div class="card"><strong>${t.topic}</strong> - ${t.volume.toLocaleString()} mentions - ${t.velocity > 1 ? "📈" : "📉"} ${((t.velocity - 1) * 100).toFixed(0)}%</div>`).join("")}
<h2>Recent Tweets</h2>
${getFeed(3).map(t => `<div class="tweet"><strong>@${t.author}</strong>: ${t.content}<br><small>${t.engagement.likes} likes · ${t.sentiment}</small></div>`).join("")}
</body>
</html>`,
    },
  },
});

console.log(`🐦 CT Intelligence Agent running on port 3003`);
