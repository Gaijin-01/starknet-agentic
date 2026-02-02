#!/usr/bin/env python3
"""
Weekly Digest - Full week overview (Monday 9:00)
Full week overview, price action summary, top signals, content recommendations
"""
import argparse
import asyncio
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from daily_pulse import get_prices, load_config


def calculate_week_summary(week_data):
    """Calculate weekly summary metrics"""
    return {
        'total_mentions': len(week_data.get('mentions', [])),
        'whale_transactions': len(week_data.get('whales', [])),
        'top_token': 'STRK',  # Would calculate from data
        'sentiment': 'neutral',  # Would calculate from sentiment
    }


def format_price_action_summary(price_data):
    """Format weekly price action"""
    msg = "📊 *WEEKLY PRICE ACTION*\n\n"
    
    for token, data in price_data.items():
        trend = "↑" if data.get('weekly_change', 0) >= 0 else "↓"
        volatility = "🔥 High" if abs(data.get('weekly_change', 0)) > 10 else "→ Low"
        msg += f"{token}: {trend} ${data['price']:,.4f} ({data.get('weekly_change', 0):+.2f}% weekly)\n"
        msg += f"   Volatility: {volatility}\n\n"
    
    return msg


def format_top_signals(signals):
    """Format top trading signals"""
    msg = "🎯 *TOP SIGNALS*\n\n"
    
    if not signals:
        msg += "No strong signals this week.\n"
        return msg
    
    for i, signal in enumerate(signals[:5], 1):
        strength = "🟢🟢🟢🟢🟢" if signal['strength'] >= 80 else \
                   "🟢🟢🟢⚪⚪" if signal['strength'] >= 60 else "🟢⚪⚪⚪⚪"
        msg += f"{i}. {signal['token']} | {signal['type']}\n"
        msg += f"   Strength: {strength} ({signal['strength']}%)\n"
        msg += f"   Rationale: {signal['rationale']}\n\n"
    
    return msg


def format_content_recommendations(articles):
    """Format recommended content"""
    msg = "📚 *CONTENT RECOMMENDATIONS*\n\n"
    
    if not articles:
        msg += "No new recommended content.\n"
        return msg
    
    for i, article in enumerate(articles[:5], 1):
        msg += f"{i}. [{article['title']}]({article['url']})\n"
        msg += f"   Source: {article['source']} | Read time: {article.get('read_time', '5 min')}\n\n"
    
    return msg


async def generate_weekly_digest(dry_run=False):
    """Generate the weekly digest"""
    config = load_config()
    
    print(f"\n{'='*60}")
    print(f"📡 WEEKLY DIGEST")
    print(f"   Week of {datetime.now().strftime('%Y-%m-%d')}")
    if dry_run:
        print(f"   [DRY RUN - No actual data fetching]")
    print(f"{'='*60}\n")
    
    if dry_run:
        # Mock data for dry run
        price_data = {
            'SLAY': {'price': 0.0234, 'weekly_change': 12.5},
            'STRK': {'price': 0.89, 'weekly_change': -3.2},
            'ETH': {'price': 2250.50, 'weekly_change': 4.1},
            'BTC': {'price': 43250.00, 'weekly_change': 2.3},
        }
        
        signals = [
            {'token': 'SLAY', 'type': 'Accumulation', 'strength': 85, 'rationale': 'Whale accumulation + volume spike'},
            {'token': 'STRK', 'type': 'Breakout Setup', 'strength': 72, 'rationale': 'Price consolidating near support'},
            {'token': 'ETH', 'type': 'Hold', 'strength': 65, 'rationale': 'Steady growth, no clear signal'},
        ]
        
        articles = [
            {'title': 'Starknet Q1 2025 Roadmap Review', 'url': 'https://starknet.io', 'source': 'Official', 'read_time': '8 min'},
            {'title': 'SLAY Token Economics Deep Dive', 'url': 'https://example.com/slay', 'source': 'CryptoSlate', 'read_time': '12 min'},
            {'title': 'L2 Arbitrage Opportunities Analysis', 'url': 'https://example.com/arb', 'source': 'The Block', 'read_time': '6 min'},
        ]
        
        whale_activity = [
            "🐋 Foundation moved 5M STRK to Ekubo",
            "🐋 New smart money wallet accumulated 10M SLAY",
            "🐋 Large ETH position moved to cold storage",
        ]
        
    else:
        # In production, fetch real data
        prices = await get_prices(config)
        price_data = {
            'SLAY': {'price': prices['SLAY']['price'], 'weekly_change': 12.5},
            'STRK': {'price': prices['STRK']['price'], 'weekly_change': -3.2},
            'ETH': {'price': prices['ETH']['price'], 'weekly_change': 4.1},
            'BTC': {'price': prices['BTC']['price'], 'weekly_change': 2.3},
        }
        signals = [
            {'token': 'SLAY', 'type': 'Accumulation', 'strength': 85, 'rationale': 'Whale accumulation + volume spike'},
            {'token': 'STRK', 'type': 'Breakout Setup', 'strength': 72, 'rationale': 'Price consolidating near support'},
        ]
        articles = [
            {'title': 'Starknet Q1 2025 Roadmap Review', 'url': 'https://starknet.io', 'source': 'Official', 'read_time': '8 min'},
        ]
        whale_activity = await get_recent_alerts(config)
    
    # Build the message
    message_parts = []
    message_parts.append("🌅 *WEEKLY DIGEST*\n")
    message_parts.append(f"_Week of {datetime.now().strftime('%B %d, %Y')}_\n")
    message_parts.append("\n")
    
    message_parts.append(format_price_action_summary(price_data))
    message_parts.append("\n")
    message_parts.append("🐋 *WHALE ACTIVITY HIGHLIGHTS*\n")
    for activity in whale_activity[:3]:
        message_parts.append(f"• {activity}\n")
    message_parts.append("\n")
    message_parts.append(format_top_signals(signals))
    message_parts.append("\n")
    message_parts.append(format_content_recommendations(articles))
    message_parts.append("\n")
    message_parts.append("💡 *Key Takeaway*: Market showing accumulation signals on SLAY. Monitor for breakout.\n")
    message_parts.append(f"\n_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}_")
    
    full_message = "\n".join(message_parts)
    
    # Output for Telegram
    print(full_message)
    
    return full_message


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Weekly Digest Generator')
    parser.add_argument('--dry-run', action='store_true', help='Run without fetching real data')
    args = parser.parse_args()
    
    asyncio.run(generate_weekly_digest(dry_run=args.dry_run))
