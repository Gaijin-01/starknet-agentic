#!/bin/bash
# analyze.sh - Run skill evolution analysis
# Usage: ./analyze.sh [--output <file>] [--alert] [--verbose]

set -e

CLAWD_ROOT="/home/wner/clawd"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ANALYZE_SCRIPT="${CLAWD_ROOT}/skills/skill-evolver/scripts/analyze.py"
OUTPUT_FILE="${CLAWD_ROOT}/memory/evolution.md"
LOG_DIR="${CLAWD_ROOT}/logs"
LOG_FILE="${LOG_DIR}/evolution-$(date +%Y%m%d-%H%M%S).log"

# Options
DO_ALERT=false
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --alert)
            DO_ALERT=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Skill Evolution Analysis${NC}"
echo -e "${BLUE}========================================${NC}"
echo "Timestamp: $(date -Iseconds)"
echo "Output file: ${OUTPUT_FILE}"
echo ""

# Check if analyze.py exists
if [ ! -f "${ANALYZE_SCRIPT}" ]; then
    echo -e "${RED}Error: analyze.py not found at ${ANALYZE_SCRIPT}${NC}"
    exit 1
fi

# Create log directory
mkdir -p "${LOG_DIR}"

# Run analysis
echo -e "${YELLOW}Running evolution analysis...${NC}"
echo "Log file: ${LOG_FILE}"

cd "${SCRIPT_DIR}/.."

if [ "${DO_ALERT}" = true ]; then
    python3 "${ANALYZE_SCRIPT}" \
        --output "${OUTPUT_FILE}" \
        --alert-session "agent:main:main" \
        2>&1 | tee "${LOG_FILE}"
else
    python3 "${ANALYZE_SCRIPT}" \
        --output "${OUTPUT_FILE}" \
        2>&1 | tee "${LOG_FILE}"
fi

EXIT_CODE=${PIPESTATUS[0]}

echo ""

# Check results
if [ ${EXIT_CODE} -eq 0 ]; then
    echo -e "${GREEN}✓ Analysis completed successfully${NC}"
    
    # Show summary
    if [ -f "${OUTPUT_FILE}" ]; then
        echo ""
        echo -e "${BLUE}Analysis Summary:${NC}"
        echo "-------------------"
        
        # Extract key metrics
        if command -v grep &> /dev/null; then
            # Count skills analyzed
            skills_count=$(grep -c "^## " "${OUTPUT_FILE}" 2>/dev/null || echo "0")
            echo -e "Skills analyzed: ${skills_count}"
            
            # Check for issues
            if grep -q "critical\|CRITICAL" "${OUTPUT_FILE}"; then
                echo -e "${RED}⚠ Critical issues found!${NC}"
            elif grep -q "warning\|WARNING" "${OUTPUT_FILE}"; then
                echo -e "${YELLOW}⚠ Warnings found${NC}"
            else
                echo -e "${GREEN}✓ No critical issues${NC}"
            fi
        fi
        
        # Show last few lines
        echo ""
        echo -e "${BLUE}Recent findings:${NC}"
        tail -15 "${OUTPUT_FILE}" | sed 's/^/  /'
    fi
else
    echo -e "${RED}✗ Analysis failed with exit code ${EXIT_CODE}${NC}"
    exit ${EXIT_CODE}
fi

echo ""
echo "Full report: ${OUTPUT_FILE}"
echo "Log file: ${LOG_FILE}"

exit 0
