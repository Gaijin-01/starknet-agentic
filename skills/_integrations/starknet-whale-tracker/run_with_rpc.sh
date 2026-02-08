#!/usr/bin/env bash
# Run arbitrage scanner with starknet.py support
# Usage: ./run_with_rpc.sh [args]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="/usr/bin/python3.12"
GLOBAL_SITE_PACKAGES="/home/wner/.local/lib/python3.12/site-packages"

# Add global site-packages to PYTHONPATH
export PYTHONPATH="$GLOBAL_SITE_PACKAGES:$PYTHONPATH"

# Run with Python 3.12 (has starknet-py)
exec $PYTHON_BIN "$@"
