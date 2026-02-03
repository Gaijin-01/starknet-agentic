#!/bin/bash
# ZK Proof Generator
# Supports Circom, Noir, and Gnark circuits

set -e

CIRCUIT_FILE=$1
WITNESS_FILE=$2
MODE=${3:-circom}

show_help() {
    echo "Usage: $0 <circuit-file> [witness-file] [mode]"
    echo ""
    echo "Modes:"
    echo "  circom  - Circom (R1CS) [default]"
    echo "  noir    - Noir (ACIR)"
    echo "  gnark   - Gnark (Golang)"
    echo ""
    echo "Examples:"
    echo "  $0 circuits/voting.circom"
    echo "  $0 circuits/voting.nr noir"
    echo "  $0 main.go gnark"
}

# Circom workflow
run_circom() {
    local circuit=$1
    local circuit_name=$(basename "$circuit" .circom)
    local output_dir="zk-output/$circuit_name"
    
    mkdir -p "$output_dir"
    
    echo "🟠 Circom: Compiling $circuit..."
    
    if ! command -v circom &> /dev/null; then
        echo "❌ Circom not installed. Install from: https://docs.circom.io/getting-started/installing-circom/"
        exit 1
    fi
    
    # Compile circuit
    circom "$circuit" \
        --output "$output_dir" \
        --r1cs \
        --wasm \
        --sym \
        2>&1 | tee "$output_dir/compile.log"
    
    echo "✅ Circuit compiled"
    echo "📁 R1CS: $output_dir/${circuit_name}.r1cs"
    echo "📁 WASM: $output_dir/${circuit_name}_js/"
    
    if [ -n "$WITNESS_FILE" ]; then
        echo ""
        echo "🧠 Generating witness..."
        cd "$output_dir/${circuit_name}_js"
        node generate_witness.js "$WITNESS_FILE" ../witness.json
        cd -
        
        echo ""
        echo "🔐 Generating proof..."
        if command -v snarkjs &> /dev/null; then
            snarkjs groth16 prove \
                "$output_dir/${circuit_name}.r1cs" \
                "$output_dir/${circuit_name}_js/witness.json" \
                "$output_dir/proof.json" \
                "$output_dir/public.json"
            
            echo "✅ Proof generated"
            echo "📁 Proof: $output_dir/proof.json"
            echo "📁 Public: $output_dir/public.json"
            
            echo ""
            echo "🔍 Verifying proof..."
            snarkjs groth16 verify \
                "$output_dir/verification_key.json" \
                "$output_dir/proof.json" \
                "$output_dir/public.json"
        else
            echo "⚠️ Install snarkjs: npm install -g snarkjs"
        fi
    fi
}

# Noir workflow
run_noir() {
    local circuit=$1
    local circuit_dir=$(dirname "$circuit")
    
    echo "⚫ Noir: Compiling $circuit..."
    
    if ! command -v nargo &> /dev/null; then
        echo "❌ Nargo not installed. Install from: https://noir-lang.org/getting_started/install.html"
        exit 1
    fi
    
    cd "$circuit_dir"
    
    # Check and update if needed
    nargo check 2>/dev/null || true
    
    # Compile
    nargo build
    
    echo "✅ Noir circuit built"
    echo "📁 Circuit: target/${circuit_dir}.nargo/build"
    
    if [ -n "$WITNESS_FILE" ]; then
        echo ""
        echo "🧠 Generating witness..."
        nargo execute "$WITNESS_FILE"
        
        echo ""
        echo "🔐 Generating proof..."
        nargo prove
        
        echo "✅ Proof generated"
        echo "📁 Proof: proofs/"
    fi
    
    cd -
}

# Gnark workflow
run_gnark() {
    local go_file=$1
    local package_name=$(go list -m)
    
    echo "🔵 Gnark: Building $go_file..."
    
    if ! command -v go &> /dev/null; then
        echo "❌ Go not installed"
        exit 1
    fi
    
    # Build
    go build -tags gnark "$go_file"
    
    echo "✅ Gnark circuit built"
    echo "📁 Binary: $(basename $go_file .go)"
    
    if [ -n "$WITNESS_FILE" ]; then
        echo ""
        echo "🔐 Running proof generation..."
        ./$(basename $go_file .go) prove -w "$WITNESS_FILE"
    fi
}

# Main
if [ -z "$CIRCUIT_FILE" ]; then
    show_help
    exit 1
fi

if [ ! -f "$CIRCUIT_FILE" ]; then
    echo "❌ File not found: $CIRCUIT_FILE"
    exit 1
fi

if [ "$CIRCUIT_FILE" = "--help" ]; then
    show_help
    exit 0
fi

case $MODE in
    circom) run_circom "$CIRCUIT_FILE" "$WITNESS_FILE" ;;
    noir) run_noir "$CIRCUIT_FILE" "$WITNESS_FILE" ;;
    gnark) run_gnark "$CIRCUIT_FILE" "$WITNESS_FILE" ;;
    *) echo "Unknown mode: $MODE"; show_help; exit 1 ;;
esac

echo ""
echo "✅ ZK proof generation complete"
