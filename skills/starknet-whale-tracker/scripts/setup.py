#!/usr/bin/env python3
"""
Starknet Whale Tracker - Setup and Initialization Script
"""
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Loaded config from {env_path}")
else:
    print(f"⚠️ No .env file found at {env_path}")

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from tracker import create_tracker
from config import DEFAULT_CONFIG
from whale_db import WhaleDatabase, WhaleWallet, create_default_whales
from starknet_rpc import StarknetRPC


async def setup_rpc():
    """Test RPC connection"""
    rpc_url = os.getenv("STARKNET_RPC_URL", DEFAULT_CONFIG.starknet.rpc_url)

    if "YOUR_API_KEY" in rpc_url or not rpc_url:
        print("❌ RPC URL not configured!")
        print("   Get free key at https://www.alchemy.com/")
        print("   Edit .env and set STARKNET_RPC_URL")
        return None

    print(f"🔗 Testing RPC: {rpc_url[:50]}...")

    rpc = StarknetRPC(rpc_url)
    try:
        await rpc.connect()
        block = await rpc.get_block_number()
        print(f"✅ Connected! Current block: {block}")
        await rpc.close()
        return rpc_url
    except Exception as e:
        print(f"❌ RPC connection failed: {e}")
        return None


def setup_database(db_path: str = "./data/whales.db"):
    """Initialize database with default whales"""
    print(f"\n📦 Setting up database: {db_path}")

    db = WhaleDatabase(db_path)

    # Add known Starknet entities
    print("🐋 Adding known whales...")
    create_default_whales(db)

    stats = db.get_whale_stats()
    print(f"✅ Database ready: {stats['total_whales']} whales tracked")

    return db


def setup_telegram():
    """Check Telegram configuration"""
    enabled = os.getenv("TELEGRAM_ENABLED", "false").lower() == "true"
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

    if enabled:
        if token and chat_id:
            print("✅ Telegram configured")
            return True
        else:
            print("❌ Telegram enabled but missing token/chat_id")
            return False
    else:
        print("ℹ️ Telegram not enabled (set TELEGRAM_ENABLED=true to enable)")
        return False


async def test_monitoring(rpc_url: str):
    """Test monitoring with real RPC"""
    print(f"\n🧪 Testing monitoring (5 second scan)...")

    tracker = create_tracker(
        rpc_url=rpc_url,
        db_path="./data/whales.db"
    )

    await tracker.connect()

    # Quick scan
    print("📊 Scanning for activity...")
    activities = await tracker.get_activity(hours=1)

    if activities:
        print(f"✅ Found {len(activities)} recent activities")
    else:
        print("ℹ️ No recent activity (this is normal for fresh start)")

    # Quick arbitrage scan
    print("💰 Scanning arbitrage...")
    opps = await tracker.get_arbitrage_opportunities()
    print(f"📈 Found {len(opps)} opportunities")

    await tracker.close()
    print("✅ Monitoring test complete")


def print_usage():
    """Print usage instructions"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║           🐋 Starknet Whale Tracker - Ready!                   ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  Commands:                                                     ║
║                                                                ║
║    python scripts/cli.py start --mode all                      ║
║        Start full monitoring (whales + arbitrage)              ║
║                                                                ║
║    python scripts/cli.py list                                  ║
║        List tracked whales                                     ║
║                                                                ║
║    python scripts/cli.py track 0x123... --tags deployer        ║
║        Add new wallet to track                                 ║
║                                                                ║
║    python scripts/cli.py activity --hours 24                   ║
║        Show recent activity                                    ║
║                                                                ║
║    python scripts/cli.py arbitrage                             ║
║        Scan for arbitrage opportunities                        ║
║                                                                ║
║    python scripts/api.py --port 8080                           ║
║        Start REST API server                                   ║
║                                                                ║
║  Telegram Alerts:                                              ║
║    1. Create bot @BotFather                                    ║
║    2. Get chat ID @userinfobot                                 ║
║    3. Edit .env with credentials                               ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
""")


async def main():
    print("🐋 Starknet Whale Tracker - Setup")
    print("=" * 50)

    # 1. Test RPC
    rpc_url = await setup_rpc()
    if not rpc_url:
        print("\n📝 To continue, edit .env and add your RPC URL")
        print_usage()
        return

    # 2. Setup database
    db = setup_database()

    # 3. Setup Telegram
    setup_telegram()

    # 4. Test monitoring
    await test_monitoring(rpc_url)

    # 5. Print usage
    print_usage()


if __name__ == "__main__":
    asyncio.run(main())
