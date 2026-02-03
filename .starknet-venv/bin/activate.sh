#!/bin/bash
export PYTHONPATH="/home/wner/.local/lib/python3.12/site-packages:$PYTHONPATH"
export PATH="/home/wner/clawd/.starknet-venv/bin:$PATH"
alias python="/usr/bin/python3.12"
alias pip="/usr/bin/python3.12 -m pip"
echo "Starknet venv activated (Python 3.12)!"
