#!/usr/bin/env python3
"""
Weekly Wrap - Friday 20:00 wrap-up
Week in review, wins/losses, next week preview
"""
import asyncio
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from daily_pulse import load_config, get_prices


def get_week_dates():
    """Get the date range for the current week"""
    today = datetime.now()
    # Find Monday of this week
    monday = today - timedelta(days=today.weekday())
    friday = monday + timedelta(days=4)
    return monday.strftime('%Y-%m-%d'), friday.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')


def format_week_in_review(week_stats):
    """Format the week in review"""
    msg = "📆 *WEEK IN REVIEW*\n\n"
    msg += f"Period: {week_stats['start_date']} → {week_stats['end_date']}\n\n"
    msg += f"📊 *Market Overview*\n"
    msg += f"  SLAY: {week_stats['slay_performance']}\n"
    msg += f"  STRK: {week_stats['strk_performance']}\n"
    msg += f"  ETH:  {week_stats['eth_performance']}\n"
    msg += f"  BTC:  {week_stats['btc_performance']}\n\n"
    msg += f"🐋 *Whale Activity*\n"
    msg += f"  {week_stats['whale_transactions']} large transactions\n"
    msg += f"  {week_stats['new_whale_positions']} new positions opened\n\n"
    msg += f"🐦 *CT Sentiment*\n"
    msg += f"  {week_stats['total_mentions']} mentions tracked\n"
    msg += f"  Overall: {week_stats['sentiment']}\n"
    return msg


def format_wins_losses(wins, losses):
    """Format wins and losses"""
    msg = "🎯 *WINS & LOSSES*\n\n"
    
    msg += "✅ *Wins*\n"
    if wins:
        for win in wins:
            msg += f"  • {win}\n"
    else:
        msg += "  No notable wins this week.\n"
    
    msg += "\n❌ *Areas to Improve*\n"
    if losses:
        for loss in losses:
            msg += f"  • {loss}\n"
    else:
        msg += "  No significant issues.\n"
    
    return msg


def format_next_week_preview(preview):
    """Format next week preview"""
    msg = "\n🔮 *NEXT WEEK PREVIEW*\n\n"
    
    msg += "📅 *Key Events*\n"
    for event in preview.get('events', []):
        msg += f"  • {event}\n"
    
    msg += "\n🎯 *Watch List*\n"
    for item in preview.get('watch_list', []):
        msg += f"  • {item}\n"
    
    msg += "\n⚠️ *Risk Factors*\n"
    for risk in preview.get('risks', []):
        msg += f"  • {risk}\n"
    
    return msg


async def generate_weekly_wrap():
    """Generate the weekly wrap"""
    config = load_config()
    start_date, end_date, today = get_week_dates()
    
    print(f"\n{'='*60}")
    print(f"📡 WEEKLY WRAP")
    print(f"   Week of {start_date} → {end_date}")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")
    
    # Mock data - in production, would aggregate real data
    week_stats = {
        'start_date': start_date,
        'end_date': end_date,
        'slay_performance': '+12.5% (Strong accumulation)',
        'strk_performance': '-3.2% (Consolidation)',
        'eth_performance': '+4.1% (Steady)',
        'btc_performance': '+2.3% (Range-bound)',
        'whale_transactions': 47,
        'new_whale_positions': 8,
        'total_mentions': 234,
        'sentiment': 'Cautiously Bullish 🟢',
    }
    
    wins = [
        "SLAY breakout setup correctly identified",
        "STRK accumulation zone predicted accurately",
        "ETH weekly candle closed green",
        "Whale tracker caught 3 large positions early",
    ]
    
    losses = [
        "Missed SOL rally opportunity",
        "Overleveraged on STRK dip (too early)",
        "Should have taken profits on SLAY at +15%",
    ]
    
    preview = {
        'events': [
            "Monday: Starknet protocol upgrade",
            "Thursday: US CPI data release",
            "Friday: Monthly options expiry",
        ],
        'watch_list': [
            "SLAY - watching for $0.025 resistance break",
            "STRK - potential bounce at $0.80 support",
            "ETH - $2,300 breakout attempt",
            "BTC - $45,000 psychological level",
        ],
        'risks': [
            "Macro uncertainty from Fed statements",
            "L2 competitor announcements",
            "Volume could dry up into weekend",
        ],
    }
    
    # Build the message
    message_parts = []
    message_parts.append("🌇 *WEEKLY WRAP*\n")
    message_parts.append(f"_{start_date} → {end_date}_\n")
    message_parts.append("\n")
    
    message_parts.append(format_week_in_review(week_stats))
    message_parts.append("\n")
    message_parts.append(format_wins_losses(wins, losses))
    message_parts.append(format_next_week_preview(preview))
    
    message_parts.append("\n💭 *Personal Note*\n")
    message_parts.append("This week showed strong accumulation on SLAY. Stay patient, the setup is developing well.\n")
    
    message_parts.append(f"\n_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}_")
    
    full_message = "\n".join(message_parts)
    
    # Output for Telegram
    print(full_message)
    
    return full_message


if __name__ == "__main__":
    asyncio.run(generate_weekly_wrap())
