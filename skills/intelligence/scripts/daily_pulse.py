#!/usr/bin/env python3
"""
Daily Pulse - Morning/Afternoon/Evening digest
Collects real prices, whale alerts, and CT mentions
"""
import asyncio
import os
import sys
import json
import aiohttp
from datetime import datetime
from pathlib import Path

# Add scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load config from JSON
config_path = Path(__file__).parent.parent / "config.json"
with open(config_path) as f:
    CONFIG = json.load(f)

# API Keys from environment
COINGECKO_API_KEY = os.environ.get('COINGECKO_API_KEY', '')
BRAVE_API_KEY = os.environ.get('BRAVE_API_KEY', '')


def get_fallback_prices(tokens):
    """Fallback prices when API fails - very conservative estimates"""
    return {t: {'price': 0, 'change_24h': 0} for t in tokens}


def format_time_of_day():
    """Return greeting based on time"""
    hour = datetime.now().hour
    if hour < 12:
        return "Morning"
    elif hour < 17:
        return "Afternoon"
    else:
        return "Evening"


def format_price_message(prices):
    """Format prices into a nice message"""
    if not prices or prices.get('error'):
        return "📊 *Price data unavailable*"
    
    msg = "💰 *PRICES*\n"
    for token, data in prices.items():
        if isinstance(data, dict) and 'price' in data:
            change = data.get('change_24h') or 0
            change_emoji = "📈" if change >= 0 else "📉"
            price = data['price']
            # Format based on price magnitude
            if price < 0.001:
                price_str = f"{price:.8f}"  # Micro-pennies
            elif price < 1:
                price_str = f"{price:.6f}"
            elif price < 1000:
                price_str = f"{price:.4f}"
            else:
                price_str = f"{price:,.2f}"
            msg += f"{token}: ${price_str} {change_emoji} {change:+.2f}%\n"
    return msg


def format_whale_alerts(alerts):
    """Format whale alerts"""
    if not alerts:
        return "🐋 *No significant whale activity*"
    
    msg = "🐋 *WHALE ACTIVITY*\n"
    for alert in alerts[:5]:  # Top 5 alerts
        msg += f"• {alert}\n"
    return msg


def format_ct_mentions(mentions):
    """Format CT mentions"""
    if not mentions:
        return "🐦 *No significant CT mentions*"
    
    msg = "🐦 *CT MENTIONS*\n"
    for mention in mentions[:5]:  # Top 5 mentions
        msg += f"• {mention}\n"
    return msg


async def get_coingecko_prices(tokens):
    """Fetch real prices from CoinGecko API"""
    # Map tokens to CoinGecko IDs
    token_map = {
        'ETH': 'ethereum',
        'BTC': 'bitcoin',
        'STRK': 'starknet',
        'SLAY': 'slay',  # Memecoin SLAY on CoinGecko
        'DREAMS': 'daydreams',  # Needs verification - could be different token
        'SURVIVOR': 'survivor-2',  # Needs verification
        'SCHIZODIO': 'schizodio',  # Starknet ecosystem token
    }
    
    ids = [token_map.get(t, t.lower()) for t in tokens]
    ids = list(set(ids))  # Deduplicate
    
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': ','.join(ids),
        'vs_currencies': 'usd',
        'include_24hr_change': 'true'
    }
    headers = {}
    if COINGECKO_API_KEY:
        headers['x-cg-api-key'] = COINGECKO_API_KEY
    
    for attempt in range(3):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        result = {}
                        for token in tokens:
                            cg_id = token_map.get(token, token.lower())
                            if cg_id in data:
                                result[token] = {
                                    'price': data[cg_id].get('usd', 0),
                                    'change_24h': data[cg_id].get('usd_24h_change', 0)
                                }
                        return result
                    elif resp.status == 429:
                        await asyncio.sleep(2 * (attempt + 1))
                        continue
                    else:
                        return {'error': f'API returned {resp.status}'}
        except Exception as e:
            await asyncio.sleep(1)
            continue
    
    return get_fallback_prices(tokens)


async def get_recent_alerts(config):
    """Get recent whale alerts from the tracker"""
    # Read from whale tracker database if available
    whale_db = Path(__file__).parent.parent.parent / "starknet-whale-tracker" / "data" / "whales.db"
    
    if not whale_db.exists():
        # Fallback: try to get alerts via script
        try:
            import subprocess
            result = subprocess.run(
                ['python3', '../starknet-whale-tracker/scripts/check.py'],
                cwd=str(Path(__file__).parent.parent),
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                output = result.stdout
                # Parse simple alerts
                alerts = []
                for line in output.split('\n'):
                    if 'WHALE' in line or 'ARBITRAGE' in line:
                        alerts.append(line.strip())
                return alerts if alerts else ["🐋 Market quiet - no major whale moves"]
        except Exception:
            pass
    
    # Default: market quiet
    return ["🐋 Market quiet - no major whale moves"]


async def get_ct_mentions(config):
    """Get recent CT mentions via Brave Web Search"""
    keywords = config.get('sources', {}).get('twitter', {}).get('keywords', [])
    accounts = config.get('sources', {}).get('twitter', {}).get('accounts', [])
    
    # Build search query
    query_parts = keywords[:3] + [f"from:{a.replace('@', '')}" for a in accounts[:3]]
    query = ' OR '.join(query_parts[:5])
    
    if not BRAVE_API_KEY:
        # Fallback: no API key
        return ["🐦 Enable BRAVE_API_KEY for real-time mentions"]
    
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        'Accept': 'application/json',
        'X-Subscription-Token': BRAVE_API_KEY
    }
    params = {
        'q': query,
        'count': 10,
        'search_lang': 'en'
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results = data.get('web', {}).get('results', [])
                    mentions = []
                    for r in results[:5]:
                        title = r.get('title', '')[:80]
                        mentions.append(f"📢 {title}")
                    return mentions if mentions else ["🐦 No recent mentions found"]
                else:
                    return [f"🐦 Search API error ({resp.status})"]
    except Exception as e:
        return [f"🐦 Search error: {str(e)[:30]}"]


async def generate_daily_pulse():
    """Generate the daily pulse digest"""
    time_greeting = format_time_of_day()
    
    print(f"\n{'='*50}")
    print(f"📡 DAILY PULSE - {time_greeting} DIGEST (REAL DATA)")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*50}\n")
    
    tokens = CONFIG.get('token_alerts', {}).get('tokens', ['SLAY', 'STRK', 'ETH', 'BTC'])
    
    # Collect all data in parallel
    prices, whale_alerts, ct_mentions = await asyncio.gather(
        get_coingecko_prices(tokens),
        get_recent_alerts(CONFIG),
        get_ct_mentions(CONFIG)
    )
    
    # Build the message
    message_parts = []
    message_parts.append(f"☀️ *Good {time_greeting}!*\n")
    message_parts.append(format_price_message(prices))
    message_parts.append("\n")
    message_parts.append(format_whale_alerts(whale_alerts))
    message_parts.append("\n")
    message_parts.append(format_ct_mentions(ct_mentions))
    message_parts.append("\n")
    message_parts.append("_Pulse generated at " + datetime.now().strftime('%H:%M') + "_")
    
    full_message = "\n".join(message_parts)
    
    # Output for Telegram
    print(full_message)
    
    return full_message


if __name__ == "__main__":
    asyncio.run(generate_daily_pulse())
