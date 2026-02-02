#!/usr/bin/env bash
# Run arbitrage scanner with starknet.py support
# Usage: ./run_with_rpc.sh [args]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/venv/bin/python3"
GLOBAL_SITE_PACKAGES="/home/wner/.local/lib/python3.12/site-packages"

# Add global site-packages to PYTHONPATH
export PYTHONPATH="$GLOBAL_SITE_PACKAGES:$PYTHONPATH"

# Run with venv python but extended path
exec $VENV_PYTHON "$@"
