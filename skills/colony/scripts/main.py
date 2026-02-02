#!/usr/bin/env python3
"""
Colony CLI Wrapper - Entry point for Starknet Intelligence Colony

Usage:
    python3 scripts/main.py              # Run all agents
    python3 scripts/main.py --market     # Market agent only
    python3 scripts/main.py --research   # Research agent only
    python3 scripts/main.py --content    # Content agent only
    python3 scripts/main.py --dashboard  # Run dashboard only
"""
import sys
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPT_DIR)

try:
    from main import main
except ImportError as e:
    logger.error(f"Failed to import colony modules: {e}")
    logger.error("Make sure dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Colony failed: {e}")
        sys.exit(1)
