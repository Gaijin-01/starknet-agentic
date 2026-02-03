#!/bin/bash
# Compile and Test Blockchain Projects
# Auto-detects language and runs appropriate test suite

set -e

NETWORK=${1:-local}
VERBOSE=${2:-false}

show_help() {
    echo "Usage: $0 [network] [verbose]"
    echo ""
    echo "Examples:"
    echo "  $0 local           # Test on local network"
    echo "  $0 sepolia true    # Test on Sepolia with verbose output"
}

detect_language() {
    if [ -f "foundry.toml" ]; then
        echo "foundry"
    elif [ -f "hardhat.config.ts" ] || [ -f "hardhat.config.js" ]; then
        echo "hardhat"
    elif [ -f "Anchor.toml" ]; then
        echo "anchor"
    elif [ -f "Scarb.toml" ]; then
        echo "scarb"
    elif [ -f "Move.toml" ]; then
        echo "aptos"
    elif [ -f "pyproject.toml" ] && grep -q "ape" "pyproject.toml"; then
        echo "ape"
    else
        echo "unknown"
    fi
}

test_foundry() {
    echo "🧪 Running Foundry tests..."
    
    if [ "$VERBOSE" = "true" ]; then
        forge test -vvv --match-path "test/**/*.sol"
    else
        forge test
    fi
    
    echo "📊 Gas report:"
    forge test --gas-report 2>/dev/null || echo "No gas report generated"
}

test_hardhat() {
    echo "🧪 Running Hardhat tests..."
    
    if [ "$VERBOSE" = "true" ]; then
        npx hardhat test --verbose
    else
        npx hardhat test
    fi
    
    echo "📊 Coverage:"
    npx hardhat coverage 2>/dev/null || echo "Coverage not configured"
}

test_anchor() {
    echo "🧪 Running Anchor tests..."
    
    if [ "$VERBOSE" = "true" ]; then
        anchor test --verbose
    else
        anchor test
    fi
}

test_scarb() {
    echo "🧪 Running Scarb/Cairo tests..."
    scarb test
    
    echo "📊 Starknet gas usage:"
    grep -r "resource" target/dev/*.json 2>/dev/null || echo "Gas info not available"
}

test_ape() {
    echo "🧪 Running Ape/Vyper tests..."
    
    source .venv/bin/activate
    
    if [ "$VERBOSE" = "true" ]; then
        ape test --verbose
    else
        ape test
    fi
}

test_local_network() {
    echo "🌐 Starting local network and testing..."
    
    LANGUAGE=$(detect_language)
    
    case $LANGUAGE in
        foundry)
            anvil > /dev/null 2>&1 &
            ANVIL_PID=$!
            sleep 3
            forge test --fork-url http://127.0.0.1:8545
            kill $ANVIL_PID 2>/dev/null
            ;;
        hardhat)
            npx hardhat node > /dev/null 2>&1 &
            HARDHAT_PID=$!
            sleep 5
            npx hardhat test --network localhost
            kill $HARDHAT_PID 2>/dev/null
            ;;
        anchor)
            anchor test
            ;;
        *)
            echo "⚠️ Local network not supported for $LANGUAGE"
            ;;
    esac
}

# Main
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
    exit 0
fi

echo "🔍 Detecting project type..."
LANGUAGE=$(detect_language)
echo "📦 Detected: $LANGUAGE"

if [ "$NETWORK" = "local" ]; then
    test_local_network
else
    case $LANGUAGE in
        foundry) test_foundry ;;
        hardhat) test_hardhat ;;
        anchor) test_anchor ;;
        scarb) test_scarb ;;
        ape) test_ape ;;
        *) echo "❌ Unknown project type"; exit 1 ;;
    esac
fi

echo ""
echo "✅ Tests completed"
