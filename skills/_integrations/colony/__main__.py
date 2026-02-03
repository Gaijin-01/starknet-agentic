#!/usr/bin/env python3
"""
Entry point for running colony as a module: python3 -m colony
"""

import sys
from pathlib import Path

# Add colony to path
COLONY_PATH = Path(__file__).parent.resolve()
if str(COLONY_PATH) not in sys.path:
    sys.path.insert(0, str(COLONY_PATH))

# Run main
if __name__ == "__main__":
    import main
    asyncio.run(main.main())
