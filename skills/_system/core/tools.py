#!/usr/bin/env python3
"""
TOOL_DEFINITIONS.py - MiniMax Tool Calling Schema

This file provides OpenAI-compatible tool definitions for MiniMax LLM.
The LLM can use these tools to call actual skill functions.

IMPORTANT: This file only defines the schema - it does NOT execute anything.
Actual execution is handled by executor.py
"""

# ============================================
# CRYPTO TOOLS
# ============================================

TOOL_DEFINITIONS = [
    # --- PRICES ---
    {
        "type": "function",
        "function": {
            "name": "get_crypto_price",
            "description": "Get current price for a cryptocurrency from CoinGecko",
            "parameters": {
                "type": "object",
                "properties": {
                    "token_id": {
                        "type": "string",
                        "description": "CoinGecko token ID (e.g., 'bitcoin', 'ethereum', 'starknet', 'solana')"
                    },
                    "currency": {
                        "type": "string",
                        "description": "Currency for price (default: 'usd')",
                        "default": "usd"
                    }
                },
                "required": ["token_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_crypto_prices",
            "description": "Get current prices for multiple cryptocurrencies",
            "parameters": {
                "type": "object",
                "properties": {
                    "token_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of CoinGecko token IDs (e.g., ['bitcoin', 'ethereum'])"
                    },
                    "currency": {
                        "type": "string",
                        "description": "Currency for price (default: 'usd')",
                        "default": "usd"
                    },
                    "include_24h_change": {
                        "type": "boolean",
                        "description": "Include 24h price change percentage",
                        "default": True
                    }
                },
                "required": ["token_ids"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_coins",
            "description": "Get top cryptocurrencies by market cap",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of coins to return (default: 10, max: 100)",
                        "default": 10
                    },
                    "currency": {
                        "type": "string",
                        "description": "Currency for prices (default: 'usd')",
                        "default": "usd"
                    }
                }
            }
        }
    },
    
    # --- RESEARCH ---
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for information using multiple providers",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query string"
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of results to return (default: 5, max: 10)",
                        "default": 5
                    },
                    "freshness": {
                        "type": "string",
                        "description": "Filter by date: 'pd' (past day), 'pw' (past week), 'pm' (past month)",
                        "enum": ["pd", "pw", "pm", None],
                        "default": None
                    },
                    "search_lang": {
                        "type": "string",
                        "description": "Language code for results (e.g., 'en', 'ru')",
                        "default": "en"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_fetch",
            "description": "Fetch and extract readable content from a URL",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "HTTP/HTTPS URL to fetch"
                    },
                    "max_chars": {
                        "type": "integer",
                        "description": "Maximum characters to return (default: 5000)",
                        "default": 5000
                    },
                    "extract_mode": {
                        "type": "string",
                        "description": "Content extraction mode",
                        "enum": ["markdown", "text"],
                        "default": "markdown"
                    }
                },
                "required": ["url"]
            }
        }
    },
    
    # --- WHALE TRACKING (STARKNET) ---
    {
        "type": "function",
        "function": {
            "name": "get_whale_stats",
            "description": "Get statistics about tracked whale wallets on Starknet",
            "parameters": {
                "type": "object",
                "properties": {
                    "chain": {
                        "type": "string",
                        "description": "Blockchain network",
                        "enum": ["starknet", "starknet-sepolia"],
                        "default": "starknet"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_whale_activity",
            "description": "Get recent activity from tracked whale wallets",
            "parameters": {
                "type": "object",
                "properties": {
                    "chain": {
                        "type": "string",
                        "description": "Blockchain network",
                        "enum": ["starknet", "starknet-sepolia"],
                        "default": "starknet"
                    },
                    "hours": {
                        "type": "integer",
                        "description": "Lookback period in hours (default: 24)",
                        "default": 24
                    },
                    "tag": {
                        "type": "string",
                        "description": "Filter by whale tag (e.g., 'foundation', 'protocol')",
                        "enum": ["foundation", "protocol", "smart_money", None],
                        "default": None
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_arbitrage",
            "description": "Find arbitrage opportunities across DEXs on Starknet",
            "parameters": {
                "type": "object",
                "properties": {
                    "min_spread_percent": {
                        "type": "number",
                        "description": "Minimum spread percentage to consider (default: 0.05)",
                        "default": 0.05
                    },
                    "chain": {
                        "type": "string",
                        "description": "Blockchain network",
                        "enum": ["starknet", "starknet-sepolia"],
                        "default": "starknet"
                    }
                }
            }
        }
    },
    
    # --- DEFI YIELDS (STARKNET) ---
    {
        "type": "function",
        "function": {
            "name": "get_defi_yields",
            "description": "Get current DeFi yields on Starknet (APY, TVL, risk metrics) for Ekubo, Jediswap, zkLend, Nostra, 10k",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of top yields to return (default: 5)",
                        "default": 5
                    },
                    "protocol": {
                        "type": "string",
                        "description": "Filter by protocol (e.g., 'Ekubo', 'zkLend', 'Nostra')",
                    },
                    "min_tvl": {
                        "type": "number",
                        "description": "Minimum TVL in USD to include"
                    },
                    "risk_level": {
                        "type": "string",
                        "description": "Filter by risk level",
                        "enum": ["low", "medium", "high"]
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_market_summary",
            "description": "Get Starknet DeFi market overview (total TVL, protocol count, pool count)",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    
    # --- CRYPTO TRADING ---
    {
        "type": "function",
        "function": {
            "name": "get_market_metrics",
            "description": "Get on-chain metrics for cryptocurrencies",
            "parameters": {
                "type": "object",
                "properties": {
                    "token_id": {
                        "type": "string",
                        "description": "CoinGecko token ID (e.g., 'bitcoin', 'ethereum')"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days of history (default: 7)",
                        "default": 7
                    }
                },
                "required": ["token_id"]
            }
        }
    },
    
    # --- CONTENT GENERATION ---
    {
        "type": "function",
        "function": {
            "name": "generate_post",
            "description": "Generate a social media post based on a topic and style",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Topic or content for the post"
                    },
                    "style": {
                        "type": "string",
                        "description": "Writing style (e.g., 'ct', 'schizo', 'standard')",
                        "default": "standard"
                    },
                    "platform": {
                        "type": "string",
                        "description": "Target platform",
                        "enum": ["twitter", "telegram", "blog"],
                        "default": "twitter"
                    },
                    "max_length": {
                        "type": "integer",
                        "description": "Maximum characters (default: 280 for Twitter)",
                        "default": 280
                    }
                },
                "required": ["topic"]
            }
        }
    },
    
    # --- STYLE LEARNING ---
    {
        "type": "function",
        "function": {
            "name": "analyze_style",
            "description": "Analyze writing style from example texts",
            "parameters": {
                "type": "object",
                "properties": {
                    "texts": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of example texts to analyze"
                    }
                },
                "required": ["texts"]
            }
        }
    },
    
    # --- IMAGE ANALYSIS ---
    {
        "type": "function",
        "function": {
            "name": "analyze_image",
            "description": "Analyze an image using the configured image model",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Path or URL to the image"
                    },
                    "prompt": {
                        "type": "string",
                        "description": "What to look for in the image"
                    }
                },
                "required": ["image_path", "prompt"]
            }
        }
    },
    
    # --- WEATHER ---
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather or forecast for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City or location name"
                    },
                    "forecast_days": {
                        "type": "integer",
                        "description": "Number of forecast days (0-14, default: 0 for current)",
                        "default": 0
                    }
                },
                "required": ["location"]
            }
        }
    },
]


# ============================================
# TOOL CATEGORY MAPPING
# ============================================

TOOLS_BY_CATEGORY = {
    "crypto": [
        "get_crypto_price",
        "get_crypto_prices", 
        "get_top_coins",
        "get_market_metrics",
        "find_arbitrage"
    ],
    "research": [
        "web_search",
        "web_fetch"
    ],
    "starknet": [
        "get_whale_stats",
        "get_whale_activity"
    ],
    "content": [
        "generate_post",
        "analyze_style"
    ],
    "utilities": [
        "analyze_image",
        "get_weather"
    ]
}


# ============================================
# SCHEMA VERSION
# ============================================

SCHEMA_VERSION = "1.0.0"
LAST_UPDATED = "2026-02-03"
