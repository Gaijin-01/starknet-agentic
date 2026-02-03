#!/bin/bash
# Security Audit Script
# Runs Slither, Mythril, and other security tools

set -e

TOOL=${1:-all}
OUTPUT_DIR="./security-reports/$(date +%Y%m%d-%H%M%S)"

show_help() {
    echo "Usage: $0 [tool] [output-dir]"
    echo ""
    echo "Tools:"
    echo "  all       - Run all tools (default)"
    echo "  slither   - Slither static analyzer"
    echo  "mythril    - Mythril symbolic execution"
    echo "  echidna   - Echidna property testing"
    echo "  mithril   - Mythril + Slither combo"
    echo ""
    echo "Examples:"
    echo "  $0 slither"
    echo "  $0 all ./my-reports"
}

mkdir -p "$OUTPUT_DIR"

run_slither() {
    echo "🔍 Running Slither..."
    
    if ! command -v slither &> /dev/null; then
        pip install slither-analyzer
    fi
    
    slither . --exclude-dependencies --json "$OUTPUT_DIR/slither.json" 2>&1 | tee "$OUTPUT_DIR/slither.txt"
    
    echo "📊 Slither report: $OUTPUT_DIR/slither.json"
}

run_mythril() {
    echo "🔍 Running Mythril..."
    
    if ! command -v myth &> /dev/null; then
        pip install mythril
    fi
    
    myth analyze . --srv \
        --json "$OUTPUT_DIR/mythril.json" \
        2>&1 | tee "$OUTPUT_DIR/mythril.txt"
    
    echo "📊 Mythril report: $OUTPUT_DIR/mythril.json"
}

run_echidna() {
    echo "🔍 Running Echidna..."
    
    if ! command -v echidna-test &> /dev/null; then
        echo "Install: cargo install --git https://github.com/crytic/echidna --tag v2.0.0"
        return 1
    fi
    
    echidna-test . \
        --config echidna.yaml \
        --json "$OUTPUT_DIR/echidna.json" \
        2>&1 | tee "$OUTPUT_DIR/echidna.txt"
    
    echo "📊 Echidna report: $OUTPUT_DIR/echidna.json"
}

run_securify() {
    echo "🔍 Running Securify..."
    
    # Securify is a web service, use API or docker
    if command -v docker &> /dev/null; then
        docker run -v $(pwd):/project securify \
            --json "$OUTPUT_DIR/securify.json" \
            2>&1 | tee "$OUTPUT_DIR/securify.txt"
    else
        echo "⚠️ Securify requires Docker. Skipping..."
    fi
}

run_all() {
    echo "🛡️ Running full security audit..."
    echo "📁 Output directory: $OUTPUT_DIR"
    echo ""
    
    run_slither
    echo ""
    run_mythril
    
    # Optional: run if available
    if command -v echidna-test &> /dev/null; then
        echo ""
        run_echidna
    fi
    
    echo ""
    echo "✅ Audit complete"
    echo ""
    echo "📊 Summary:"
    echo "  - Slither: $OUTPUT_DIR/slither.json"
    echo "  - Mythril: $OUTPUT_DIR/mythril.json"
}

generate_summary() {
    echo ""
    echo "📋 SECURITY SUMMARY"
    echo "=================="
    
    # Count issues
    if [ -f "$OUTPUT_DIR/slither.json" ]; then
        high=$(grep -o '"high"' "$OUTPUT_DIR/slither.json" | wc -l)
        medium=$(grep -o '"medium"' "$OUTPUT_DIR/slither.json" | wc -l)
        echo "Slither: $high high, $medium medium issues"
    fi
    
    if [ -f "$OUTPUT_DIR/mythril.json" ]; then
        issues=$(grep -c '"issue"' "$OUTPUT_DIR/mythril.json" 2>/dev/null || echo "0")
        echo "Mythril: $issues issues found"
    fi
}

# Main
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
    exit 0
fi

case $TOOL in
    all) run_all ;;
    slither) run_slither ;;
    mythril) run_mythril ;;
    echidna) run_echidna ;;
    securify) run_securify ;;
    *) echo "Unknown tool: $TOOL"; show_help; exit 1 ;;
esac

generate_summary
echo ""
echo "📁 Full reports: $OUTPUT_DIR/"
