#!/usr/bin/env python3
"""
gateway.py - Standalone Telegram Gateway for Clawdbot.

Alternative to Moltbot's built-in gateway.
Can be used independently or alongside Moltbot.

Features:
- Message routing through unified_orchestrator
- Chat history persistence (SQLite)
- Multi-user support
- Rate limiting
- LLM tool calling support (NEW)
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path

# Telegram
try:
    from telegram import Update, Bot
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("Warning: python-telegram-bot not installed")

# Local
from unified_orchestrator import UnifiedRouter

# Tool calling support (NEW)
try:
    from skills._system.core.tools import TOOL_DEFINITIONS
    from skills._system.core.executor import ToolExecutor
    from skills._system.core.minimax_client import MiniMaxClient
    TOOLS_AVAILABLE = True
except ImportError as e:
    TOOLS_AVAILABLE = False
    print(f"Warning: Tool support not available: {e}")

# Config
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USERS = os.getenv("ALLOWED_TELEGRAM_USERS", "").split(",")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
BOT_HOME = os.getenv("BOT_HOME", "/home/wner/clawd")

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{BOT_HOME}/logs/gateway.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Orchestrator
orchestrator = UnifiedRouter()

# Tool executor (NEW)
tool_executor = ToolExecutor() if TOOLS_AVAILABLE else None

# Rate limiter
RATE_LIMIT = 10  # messages per minute per user
rate_limits: Dict[int, list] = {}


class Database:
    """Simple SQLite database for persistence."""
    
    def __init__(self, db_path: str = f"{BOT_HOME}/data/gateway.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Create tables if not exist."""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS chat_history
                     (chat_id INTEGER, user_id INTEGER, message TEXT,
                      response TEXT, timestamp TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS user_stats
                     (user_id INTEGER PRIMARY KEY, message_count INTEGER,
                      last_seen TEXT)''')
        
        conn.commit()
        conn.close()
    
    def save_message(self, chat_id: int, user_id: int, message: str, response: str):
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("INSERT INTO chat_history VALUES (?, ?, ?, ?, ?)",
                  (chat_id, user_id, message, response, datetime.utcnow().isoformat()))
        
        c.execute("INSERT OR REPLACE INTO user_stats VALUES (?, ?, ?)",
                  (user_id, 1, datetime.utcnow().isoformat()))
        c.execute("UPDATE user_stats SET message_count = message_count + 1 WHERE user_id = ?",
                  (user_id,))
        
        conn.commit()
        conn.close()
    
    def get_history(self, chat_id: int, limit: int = 50) -> list:
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("SELECT message, response FROM chat_history WHERE chat_id = ? ORDER BY timestamp DESC LIMIT ?",
                  (chat_id, limit))
        
        rows = c.fetchall()
        conn.close()
        return rows[::-1]  # chronological


db = Database()


def is_allowed_user(user_id: int) -> bool:
    """Check if user is allowed."""
    if not ALLOWED_USERS or ALLOWED_USERS == ['']:
        return True
    return str(user_id) in ALLOWED_USERS


def check_rate_limit(user_id: int) -> bool:
    """Check if user is rate limited."""
    now = datetime.now()
    if user_id not in rate_limits:
        rate_limits[user_id] = []
    
    # Remove old entries
    rate_limits[user_id] = [t for t in rate_limits[user_id] if (now - t).seconds < 60]
    
    if len(rate_limits[user_id]) >= RATE_LIMIT:
        return False
    
    rate_limits[user_id].append(now)
    return True


# ============================================
# LLM TOOL CALLING (NEW)
# ============================================

# MiniMax client instance (lazy initialization)
_minimax_client = None

def get_minimax_client() -> MiniMaxClient:
    """Get or create MiniMax client (synchronous wrapper)."""
    global _minimax_client
    if _minimax_client is None:
        _minimax_client = MiniMaxClient()
    return _minimax_client


async def call_llm_with_tools(text: str, history: list = None) -> str:
    """
    Call LLM with tool support using MiniMax API.
    
    This function:
    1. Formats the message with history
    2. Calls MiniMax with tool definitions
    3. Executes any tool calls via executor
    4. Returns final response
    
    Falls back to orchestrator if tools not available.
    """
    if not TOOLS_AVAILABLE or not tool_executor:
        logger.warning("Tool support not available, using orchestrator")
        return await fallback_to_orchestrator(text, history)
    
    try:
        # Build messages for MiniMax
        messages = []
        
        # System message
        messages.append({
            "role": "system",
            "content": "You are a helpful assistant with access to tools for crypto prices, web search, and whale tracking. Use tools when appropriate."
        })
        
        # Add history context
        if history:
            for msg, resp in history[-5:]:  # Last 5 exchanges
                messages.append({"role": "user", "content": msg[:500]})
                messages.append({"role": "assistant", "content": resp[:500]})
        
        # Add current message
        messages.append({"role": "user", "content": text})
        
        # Get MiniMax client and execute tool calling loop
        client = get_minimax_client()
        response = await client.call_with_tools(
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_executor=tool_executor.execute
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Tool calling error: {e}")
        return await fallback_to_orchestrator(text, history)


async def execute_tool_call(tool_name: str, args: Dict) -> Dict:
    """Execute a tool call and return result."""
    if not tool_executor:
        return {"error": "Tool executor not available"}
    
    try:
        return await tool_executor.execute(tool_name, args)
    except Exception as e:
        logger.error(f"Tool execution error ({tool_name}): {e}")
        return {"error": str(e)}


async def fallback_to_orchestrator(text: str, history: list = None) -> str:
    """Fallback to orchestrator if tool calling fails."""
    try:
        response = await orchestrator.process({
            "text": text,
            "history": history or [],
            "channel": "telegram"
        })
        return response
    except Exception as e:
        logger.error(f"Orchestrator error: {e}")
        return "❌ Error processing request"


# ============================================
# MESSAGE HANDLING
# ============================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages."""
    if not update.message:
        return
    
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    text = update.message.text
    
    if not text:
        return
    
    # Check permissions
    if not is_allowed_user(user_id):
        await update.message.reply_text("⛔ Access denied")
        return
    
    # Check rate limit
    if not check_rate_limit(user_id):
        await update.message.reply_text("⏰ Rate limited. Try again later.")
        return
    
    logger.info(f"Message from {user_id}: {text[:50]}...")
    
    # Get history
    history = db.get_history(chat_id)
    
    # Process through orchestrator (NEW: with tool support)
    try:
        # Check if this might need tool calling
        needs_tools = _detect_tool_needs(text)
        
        if needs_tools and TOOLS_AVAILABLE:
            response = await call_llm_with_tools(text, history)
        else:
            response = await orchestrator.process({
                "text": text,
                "chat_id": chat_id,
                "user_id": user_id,
                "history": history,
                "channel": "telegram"
            })
        
        # Save to database
        db.save_message(chat_id, user_id, text, response)
        
        # Send response
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await update.message.reply_text("❌ Error processing message")


def _detect_tool_needs(text: str) -> bool:
    """Detect if message likely needs tool calling."""
    keywords = [
        "price", "btc", "eth", "starknet", "strk",
        "search", "find", "look up", "get",
        "whale", "arbitrage", "market", "news",
        "analyze", "research"
    ]
    
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords)


# ============================================
# COMMANDS
# ============================================

async def handle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle commands."""
    if not update.message:
        return
    
    command = update.message.text.split()[0]
    
    if command == "/start":
        await update.message.reply_text(
            "🤖 Clawdbot Active\n\n"
            "I'm an AI agent system with skills for:\n"
            "• Price monitoring (crypto, stocks)\n"
            "• Web research & analysis\n"
            "• Whale tracking (Starknet)\n"
            "• Content generation\n"
            "• And more...\n\n"
            "Just send me a message!\n\n"
            "Try: 'BTC price', 'search news', 'whale activity'"
        )
    elif command == "/stats":
        await show_stats(update.message.chat_id)
    elif command == "/help":
        await update.message.reply_text(
            "Available commands:\n"
            "/start - Show welcome\n"
            "/stats - Show statistics\n"
            "/help - Show this message\n\n"
            "Examples:\n"
            "• 'BTC price'\n"
            "• 'search crypto news'\n"
            "• 'whale activity on Starknet'"
        )
    elif command == "/tools":
        if TOOLS_AVAILABLE:
            tool_names = [t['function']['name'] for t in TOOL_DEFINITIONS]
            await update.message.reply_text(
                f"🛠️ Available Tools ({len(tool_names)})\n\n" +
                "\n".join(f"• {n}" for n in tool_names[:10]) +
                ("\n..." if len(tool_names) > 10 else "")
            )
        else:
            await update.message.reply_text("❌ Tool support not available")


async def show_stats(chat_id: int):
    """Show usage statistics."""
    import sqlite3
    conn = sqlite3.connect(db.db_path)
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM chat_history")
    total = c.fetchone()[0]
    
    c.execute("SELECT COUNT(DISTINCT user_id) FROM user_stats")
    users = c.fetchone()[0]
    
    c.execute("SELECT MAX(timestamp) FROM chat_history")
    last = c.fetchone()[0]
    
    conn.close()
    
    tools_status = "✅" if TOOLS_AVAILABLE else "❌"
    
    stats = f"📊 Statistics\n\n" \
            f"Total messages: {total}\n" \
            f"Unique users: {users}\n" \
            f"Last activity: {last}\n" \
            f"Tool support: {tools_status}"
    
    await Bot(token=TELEGRAM_TOKEN).send_message(
        chat_id=chat_id,
        text=stats
    )


# ============================================
# MAIN
# ============================================

async def main():
    """Start the bot."""
    if not TELEGRAM_AVAILABLE:
        logger.error("python-telegram-bot not installed")
        return
    
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set")
        return
    
    logger.info("Starting Clawdbot Gateway...")
    logger.info(f"Tool support: {'✅ Available' if TOOLS_AVAILABLE else '❌ Not available'}")
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", handle_command))
    app.add_handler(CommandHandler("help", handle_command))
    app.add_handler(CommandHandler("stats", handle_command))
    app.add_handler(CommandHandler("tools", handle_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start (initialize required for newer python-telegram-bot)
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    logger.info("Gateway started. Press Ctrl+C to stop.")
    
    # Keep running
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Gateway stopped")
