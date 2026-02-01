#!/bin/bash
# Blockchain Project Initializer
# Usage: ./project-init.sh <language> <project-name>
# Languages: solidity, rust, cairo, move, go, vyper

set -e

LANGUAGE=$1
PROJECT_NAME=$2

show_help() {
    echo "Usage: $0 <language> <project-name>"
    echo ""
    echo "Languages:"
    echo "  solidity    - Hardhat or Foundry project"
    echo "  rust        - Solana Anchor or Substrate project"
    echo "  cairo       - Starknet Scarb project"
    echo "  move        - Aptos or Sui project"
    echo "  go          - Cosmos SDK project"
    echo "  vyper       - Ape Framework project"
    echo ""
    echo "Examples:"
    echo "  $0 solidity my-defi"
    echo "  $0 rust my-anchor-program"
    echo "  $0 cairo my-starknet-contract"
}

init_solidity() {
    echo "🔷 Initializing Solidity project: $PROJECT_NAME"
    
    TEMPLATE=${3:-hardhat}  # hardhat or foundry
    
    if [ "$TEMPLATE" = "foundry" ]; then
        forge init "$PROJECT_NAME" --no-git
        cd "$PROJECT_NAME"
        forge install openzeppelin/openzeppelin-contracts
    else
        npx hardhat init "$PROJECT_NAME" --template ts --no-git 2>/dev/null || {
            mkdir -p "$PROJECT_NAME"
            cd "$PROJECT_NAME"
            npm init -y
            npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox typescript ts-node
            npx hardhat init --force 2>/dev/null || cp -r /home/wner/clawd/skills/blockchain-dev/templates/hardhat/* .
        }
    fi
    echo "✅ Solidity project ready"
}

init_rust() {
    echo "🔶 Initializing Rust project: $PROJECT_NAME"
    
    FRAMEWORK=${3:-anchor}  # anchor or substrate
    
    if [ "$FRAMEWORK" = "anchor" ]; then
        if ! command -v anchor &> /dev/null; then
            echo "❌ Anchor not installed. Install: cargo install --git https://github.com/coral-xyz/anchor --tag v0.30.1 anchor-cli --locked"
            exit 1
        fi
        anchor init "$PROJECT_NAME" --skip-lint
    else
        cargo init --lib "$PROJECT_NAME"
        cd "$PROJECT_NAME"
        echo 'wasm-bindgen = "0.2"' >> Cargo.toml
        rustup target add wasm32-unknown-unknown
    fi
    echo "✅ Rust project ready"
}

init_cairo() {
    echo "🟣 Initializing Cairo project: $PROJECT_NAME"
    
    if ! command -v scarb &> /dev/null; then
        echo "❌ Scarb not installed. Install from Starknet docs."
        exit 1
    fi
    
    scarb new "$PROJECT_NAME"
    cd "$PROJECT_NAME"
    
    # Add OpenZeppelin
    cat >> Scarb.toml << 'EOF'

[dependencies]
openzeppelin = "https://github.com/OpenZeppelin/cairo-contracts?tag=v0.12.0"
EOF
    echo "✅ Cairo project ready"
}

init_move() {
    echo "🟢 Initializing Move project: $PROJECT_NAME"
    
    BLOCKCHAIN=${3:-aptos}  # apts or sui
    
    if [ "$BLOCKCHAIN" = "aptos" ]; then
        if ! command -v move &> /dev/null; then
            echo "❌ Aptos CLI not installed."
            exit 1
        fi
        mkdir -p "$PROJECT_NAME"
        cd "$PROJECT_NAME"
        move new "$PROJECT_NAME"
    else
        sui move new "$PROJECT_NAME"
    fi
    echo "✅ Move project ready"
}

init_go() {
    echo "🔵 Initializing Go/Cosmos project: $PROJECT_NAME"
    
    mkdir -p "$PROJECT_NAME"
    cd "$PROJECT_NAME"
    go mod init "$PROJECT_NAME"
    
    # Add Cosmos SDK
    go get github.com/cosmos/cosmos-sdk@latest
    go get github.com/tendermint/tendermint@latest
    
    mkdir -p {app,cmd,x}
    echo "package $PROJECT_NAME" > app/app.go
    echo "package $PROJECT_NAME" > cmd/main.go
    echo "✅ Go project ready"
}

init_vyper() {
    echo "🟡 Initializing Vyper project: $PROJECT_NAME"
    
    mkdir -p "$PROJECT_NAME"
    cd "$PROJECT_NAME"
    python3 -m venv .venv
    source .venv/bin/activate
    pip install ape-framework
    
    ape init --no-git 2>/dev/null || true
    echo "✅ Vyper project ready"
}

# Main
if [ -z "$LANGUAGE" ] || [ -z "$PROJECT_NAME" ]; then
    show_help
    exit 1
fi

case $LANGUAGE in
    solidity) init_solidity ;;
    rust) init_rust ;;
    cairo) init_cairo ;;
    move) init_move ;;
    go) init_go ;;
    vyper) init_vyper ;;
    *) echo "Unknown language: $LANGUAGE"; show_help; exit 1 ;;
esac

echo ""
echo "📁 Project location: $(pwd)/$PROJECT_NAME"
echo "📝 Next: cd $PROJECT_NAME && ./compile-and-test.sh"
