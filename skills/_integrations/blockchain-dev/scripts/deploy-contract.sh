#!/bin/bash
# Deploy Smart Contract
# Usage: ./deploy-contract.sh <contract-name> <network> [--verify]

set -e

CONTRACT_NAME=$1
NETWORK=$2
VERIFY=${3:-false}

show_help() {
    echo "Usage: $0 <contract-name> <network> [--verify]"
    echo ""
    echo "Networks:"
    echo "  local      - Local Hardhat/Anvil"
    echo "  sepolia    - Ethereum Sepolia"
    echo "  mainnet    - Ethereum Mainnet"
    echo "  polygon    - Polygon Mainnet"
    echo "  arbitrum   - Arbitrum One"
    echo "  optimism   - Optimism"
    echo "  base       - Base"
    echo "  solana     - Solana Mainnet"
    echo "  solana-dev - Solana Devnet"
    echo "  starknet   - Starknet Mainnet"
    echo "  starknet-goerli - Starknet Goerli"
    echo ""
    echo "Examples:"
    echo "  $0 MyContract sepolia --verify"
    echo "  $0 TokenProgram solana-dev"
}

load_env() {
    if [ -f ".env" ]; then
        export $(cat .env | grep -v '^#' | xargs)
    fi
}

get_rpc_url() {
    local network=$1
    case $network in
        local) echo "http://127.0.0.1:8545" ;;
        sepolia) echo "${SEPOLIA_RPC:-https://rpc.sepolia.org}" ;;
        mainnet) echo "${ETH_RPC:-https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY}" ;;
        polygon) echo "${POLYGON_RPC:-https://polygon-rpc.com}" ;;
        arbitrum) echo "${ARB_RPC:-https://arb1.arbitrum.io/rpc}" ;;
        optimism) echo "${OPT_RPC:-https://mainnet.optimism.io}" ;;
        base) echo "${BASE_RPC:-https://mainnet.base.org}" ;;
        *) echo "" ;;
    esac
}

deploy_foundry() {
    echo "🔷 Deploying $CONTRACT_NAME via Foundry..."
    
    load_env
    local rpc=$(get_rpc_url $NETWORK)
    
    if [ -z "$rpc" ]; then
        echo "❌ No RPC URL for $NETWORK"
        exit 1
    fi
    
    forge script script/${CONTRACT_NAME}.sol:${CONTRACT_NAME}Script \
        --rpc-url "$rpc" \
        --broadcast \
        --private-key ${PRIVATE_KEY:-$(cast wallet private-key 2>/dev/null)} \
        -vvv
    
    if [ "$VERIFY" = "--verify" ]; then
        forge verify-contract --chain sepolia $(cat broadcast/*.sol/*/run-latest.json | jq -r '.transactions[0].contractAddress') $CONTRACT_NAME
    fi
}

deploy_hardhat() {
    echo "🔷 Deploying $CONTRACT_NAME via Hardhat..."
    
    load_env
    local rpc=$(get_rpc_url $NETWORK)
    
    npx hardhat run scripts/deploy.ts --network $NETWORK
    
    echo "📝 Check artifacts for deployed address"
}

deploy_anchor() {
    echo "🔶 Deploying $CONTRACT_NAME to Solana..."
    
    local cluster=${NETWORK:-devnet}
    
    anchor deploy --provider.cluster $cluster
    
    echo "📝 Program ID: $(grep -r "declare_id" src/lib.rs | grep -oP '"\K[^"]+')"
}

deploy_scarb() {
    echo "🟣 Deploying $CONTRACT_NAME to Starknet..."
    
    local network=${NETWORK:-starknet-goerli}
    
    # Build first
    scarb build
    
    # Deploy
    starknet deploy --contract target/dev/${CONTRACT_NAME}.contract_class.json
    
    echo "📝 Contract deployed via Starknet CLI"
}

deploy_ape() {
    echo "🟡 Deploying $CONTRACT_NAME via Ape..."
    
    load_env
    
    source .venv/bin/activate
    
    ape run deploy $NETWORK --network $NETWORK
}

# Detect and deploy
detect_and_deploy() {
    if [ -f "foundry.toml" ]; then
        deploy_foundry
    elif [ -f "Anchor.toml" ]; then
        deploy_anchor
    elif [ -f "Scarb.toml" ]; then
        deploy_scarb
    elif [ -f "pyproject.toml" ] && grep -q "ape" "pyproject.toml"; then
        deploy_ape
    elif [ -f "hardhat.config.ts" ] || [ -f "hardhat.config.js" ]; then
        deploy_hardhat
    else
        echo "❌ Unknown project type"
        exit 1
    fi
}

# Main
if [ -z "$CONTRACT_NAME" ] || [ -z "$NETWORK" ]; then
    show_help
    exit 1
fi

if [ "$CONTRACT_NAME" = "--help" ]; then
    show_help
    exit 0
fi

echo "🚀 Deploying $CONTRACT_NAME to $NETWORK..."
detect_and_deploy

echo ""
echo "✅ Deployment completed"
echo "📁 Logs: ./broadcast/ or ./deployments/"
