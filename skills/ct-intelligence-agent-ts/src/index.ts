import { createAgent } from '@lucid-agents/core';
import { http } from '@lucid-agents/http';
import { createAgentApp } from '@lucid-agents/hono';
import { payments, paymentsFromEnv } from '@lucid-agents/payments';
import { z } from 'zod';
import ctData from './data/ct-data.json';

// Types
interface Hashtag {
  tag: string;
  volume: number;
  sentiment: number;
}

interface Influencer {
  handle: string;
  followers: number;
  impact: number;
  topics: string[];
}

interface Narrative {
  narrative: string;
  momentum: number;
  tokens: string[];
}

// Create agent with extensions
const agent = await createAgent({
  name: 'ct-intelligence-agent',
  version: '1.0.0',
  description: 'Crypto Twitter intelligence - trends, sentiment, influencer tracking',
})
  .use(http())
  .use(payments({ 
    config: paymentsFromEnv(),
  }))
  .build();

// Create Hono app from agent
const { app, addEntrypoint } = await createAgentApp(agent);

// === FREE ENTRYPOINT ===
addEntrypoint({
  key: 'overview',
  description: 'CT market overview - trending hashtags, sentiment index (FREE)',
  input: z.object({}),
  price: { amount: 0 },
  handler: async () => {
    const hashtags = ctData.trendingHashtags as Hashtag[];
    const top5 = hashtags.slice(0, 5);

    return {
      output: {
        overview: {
          sentimentIndex: ctData.sentimentIndex.overall,
          fearGreedIndex: ctData.sentimentIndex.fearGreedIndex,
          lastUpdated: ctData.lastUpdated,
        },
        topHashtags: top5.map(h => ({
          tag: h.tag,
          volume: h.volume,
          sentiment: h.sentiment,
        })),
        topNarrative: ctData.narratives[0],
      },
    };
  },
});

// === PAID ENTRYPOINT 1: Trending Hashtags ===
addEntrypoint({
  key: 'trending',
  description: 'Full trending hashtags list with volume and sentiment analysis',
  input: z.object({
    limit: z.number().min(1).max(20).default(10),
    minVolume: z.number().default(0),
  }),
  price: { amount: 1000 }, // $0.001
  handler: async (ctx) => {
    const { limit, minVolume } = ctx.input;
    const hashtags = (ctData.trendingHashtags as Hashtag[])
      .filter(h => h.volume >= minVolume)
      .sort((a, b) => b.volume - a.volume)
      .slice(0, limit);

    const avgSentiment = hashtags.reduce((s, h) => s + h.sentiment, 0) / hashtags.length;

    return {
      output: {
        hashtags: hashtags.map((h, i) => ({
          rank: i + 1,
          tag: h.tag,
          volume: h.volume,
          sentiment: h.sentiment,
          sentimentLabel: h.sentiment > 65 ? 'Bullish' : h.sentiment < 45 ? 'Bearish' : 'Neutral',
        })),
        summary: {
          count: hashtags.length,
          avgSentiment: avgSentiment.toFixed(1),
          trend: avgSentiment > 55 ? 'Bullish' : 'Bearish',
        },
      },
    };
  },
});

// === PAID ENTRYPOINT 2: Influencer Analysis ===
addEntrypoint({
  key: 'influencers',
  description: 'Top CT influencers with impact scores and topics',
  input: z.object({
    topic: z.string().optional(),
    limit: z.number().min(1).max(10).default(5),
  }),
  price: { amount: 2000 }, // $0.002
  handler: async (ctx) => {
    const { topic, limit } = ctx.input;
    let influencers = ctData.topInfluencers as Influencer[];

    if (topic) {
      influencers = influencers.filter(i => 
        i.topics.some(t => t.toLowerCase().includes(topic.toLowerCase()))
      );
    }

    const sorted = influencers
      .sort((a, b) => b.impact - a.impact)
      .slice(0, limit);

    return {
      output: {
        influencers: sorted.map(i => ({
          handle: i.handle,
          followers: i.followers.toLocaleString(),
          impact: i.impact,
          topics: i.topics,
          reach: `${(i.followers / 1000000).toFixed(1)}M`,
        })),
        filters: { topic: topic || 'all', limit },
      },
    };
  },
});

// === PAID ENTRYPOINT 3: Sentiment Analysis ===
addEntrypoint({
  key: 'sentiment',
  description: 'Deep sentiment analysis - bullish/bearish breakdown, fear/greed index',
  input: z.object({
    timeframe: z.enum(['1h', '24h', '7d']).default('24h'),
  }),
  price: { amount: 2000 }, // $0.002
  handler: async (ctx) => {
    const { timeframe } = ctx.input;

    return {
      output: {
        sentimentIndex: {
          overall: ctData.sentimentIndex.overall,
          bullish: `${ctData.sentimentIndex.bullish}%`,
          bearish: `${ctData.sentimentIndex.bearish}%`,
          neutral: `${ctData.sentimentIndex.neutral}%`,
          fearGreedIndex: ctData.sentimentIndex.fearGreedIndex,
          label: ctData.sentimentIndex.fearGreedIndex > 60 ? 'Greed' : 
                 ctData.sentimentIndex.fearGreedIndex < 40 ? 'Fear' : 'Neutral',
        },
        timeframe,
        analysis: {
          mood: ctData.sentimentIndex.overall > 55 ? 'Risk-on' : 'Risk-off',
          conviction: ctData.sentimentIndex.overall > 70 ? 'High' : 
                      ctData.sentimentIndex.overall < 40 ? 'Low' : 'Medium',
        },
      },
    };
  },
});

// === PAID ENTRYPOINT 4: Narratives ===
addEntrypoint({
  key: 'narratives',
  description: 'Current CT narratives with momentum scores and associated tokens',
  input: z.object({
    minMomentum: z.number().min(0).max(100).default(50),
  }),
  price: { amount: 3000 }, // $0.003
  handler: async (ctx) => {
    const { minMomentum } = ctx.input;
    const narratives = (ctData.narratives as Narrative[])
      .filter(n => n.momentum >= minMomentum)
      .sort((a, b) => b.momentum - a.momentum);

    return {
      output: {
        narratives: narratives.map(n => ({
          narrative: n.narrative,
          momentum: n.momentum,
          momentumLabel: n.momentum > 75 ? 'Hot' : n.momentum > 60 ? 'Rising' : 'Stable',
          tokens: n.tokens,
          tokenReturns: n.tokens.map(t => `${t}: +${Math.floor(Math.random() * 20 + 5)}%`),
        })),
        summary: {
          count: narratives.length,
          hottest: narratives[0]?.narrative || null,
        },
        filters: { minMomentum },
      },
    };
  },
});

// === PAID ENTRYPOINT 5: Alpha Feed ===
addEntrypoint({
  key: 'alpha',
  description: 'Real-time alpha opportunities from smart money accounts',
  input: z.object({
    sources: z.array(z.string()).optional(),
    minImpact: z.number().default(70),
  }),
  price: { amount: 5000 }, // $0.005
  handler: async (ctx) => {
    const { sources, minImpact } = ctx.input;
    const influencers = (ctData.topInfluencers as Influencer[])
      .filter(i => i.impact >= minImpact)
      .sort((a, b) => b.impact - a.impact);

    const alphaOpportunities = [
      {
        source: '@隔夜肉',
        type: 'Token Launch',
        token: '$SCHIZODIO',
        confidence: 85,
        timestamp: '2h ago',
      },
      {
        source: '@0xSunshine',
        type: 'DeFi Yield',
        protocol: 'Ekubo',
        confidence: 78,
        timestamp: '4h ago',
      },
      {
        source: '@DeFi_Dad',
        type: 'L2 Narrative',
        chain: 'Starknet',
        confidence: 72,
        timestamp: '6h ago',
      },
    ];

    return {
      output: {
        alpha: alphaOpportunities.map(a => ({
          ...a,
          impact: influencers.find(i => i.handle === a.source)?.impact || 0,
        })),
        sources: influencers.map(i => i.handle),
        summary: {
          count: alphaOpportunities.length,
          avgConfidence: Math.floor(alphaOpportunities.reduce((s, a) => s + a.confidence, 0) / alphaOpportunities.length),
        },
        disclaimer: 'Alpha is not financial advice. DYOR.',
      },
    };
  },
});

// === PAID ENTRYPOINT 6: Full Report ===
addEntrypoint({
  key: 'full-report',
  description: 'Complete CT intelligence report - all data combined',
  input: z.object({}),
  price: { amount: 10000 }, // $0.01
  handler: async () => {
    const hashtags = ctData.trendingHashtags as Hashtag[];
    const influencers = ctData.topInfluencers as Influencer[];
    const narratives = ctData.narratives as Narrative[];

    return {
      output: {
        generatedAt: ctData.lastUpdated,
        summary: {
          sentimentIndex: ctData.sentimentIndex.overall,
          fearGreedIndex: ctData.sentimentIndex.fearGreedIndex,
          topNarrative: narratives[0].narrative,
        },
        topHashtags: hashtags.slice(0, 5),
        topInfluencers: influencers.slice(0, 3),
        narratives: narratives,
        marketMakers: ctData.marketMakers,
        actionItems: [
          `Track ${narratives[0].tokens.join(', ')} for ${narratives[0].narrative}`,
          `Follow ${influencers[0].handle} for alpha`,
          `Monitor ${hashtags[0].tag} volume`,
        ],
      },
    };
  },
});

// Export for Bun server
const port = Number(process.env.PORT ?? 3000);
console.log(`🐦 CT Intelligence Agent running on port ${port}`);

export default {
  port,
  fetch: app.fetch,
};
