#!/bin/bash
# test-all.sh - Test all skills
# Usage: ./test-all.sh [--parallel] [--skip-failing]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="${SCRIPT_DIR}/../skills"
LOG_DIR="${SCRIPT_DIR}/../logs"
RESULTS_FILE="${LOG_DIR}/test-results-$(date +%Y%m%d-%H%M%S).json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Options
PARALLEL=false
SKIP_FAILING=false
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --parallel)
            PARALLEL=true
            shift
            ;;
        --skip-failing)
            SKIP_FAILING=true
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

# Create log directory
mkdir -p "${LOG_DIR}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Testing All Skills${NC}"
echo -e "${BLUE}========================================${NC}"
echo "Results file: ${RESULTS_FILE}"
echo ""

# Get list of skills (exclude dev-scripts and archived)
SKILLS=$(ls -1 "${SKILLS_DIR}" | grep -v dev-scripts | grep -v archived | sort)

TOTAL_SKILLS=$(echo "${SKILLS}" | wc -l)
PASSED=0
FAILED=0
SKIPPED=0

# Initialize results JSON
echo "{" > "${RESULTS_FILE}"
echo "  \"timestamp\": \"$(date -Iseconds)\"," >> "${RESULTS_FILE}"
echo "  \"total\": ${TOTAL_SKILLS}," >> "${RESULTS_FILE}"
echo "  \"skills\": [" >> "${RESULTS_FILE}"

first=true

# Function to test a skill
test_skill() {
    local skill=$1
    local skill_path="${SKILLS_DIR}/${skill}"
    local skill_log="${LOG_DIR}/test-${skill}-$(date +%Y%m%d-%H%M%S).log"
    local start_time=$(date +%s)
    
    echo -e "${YELLOW}Testing: ${skill}${NC}"
    
    # Check if skill has tests
    if [ ! -f "${skill_path}/main.py" ] && \
       [ ! -f "${skill_path}/scripts/test.py" ] && \
       [ ! -f "${skill_path}/tests/test.py" ]; then
        echo -e "  ${BLUE}↳ No tests found, checking structure...${NC}"
        
        # List Python files
        py_files=$(find "${skill_path}" -name "*.py" 2>/dev/null | wc -l)
        echo -e "  ${BLUE}↳ ${py_files} Python files found${NC}"
        
        if [ "${first}" = true ]; then
            first=false
        else
            echo "," >> "${RESULTS_FILE}"
        fi
        
        echo "    {" >> "${RESULTS_FILE}"
        echo "      \"name\": \"${skill}\"," >> "${RESULTS_FILE}"
        echo "      \"status\": \"no_tests\"," >> "${RESULTS_FILE}"
        echo "      \"duration\": 0" >> "${RESULTS_FILE}"
        echo -n "    }" >> "${RESULTS_FILE}"
        
        SKIPPED=$((SKIPPED + 1))
        return 0
    fi
    
    # Run test
    local exit_code=0
    if [ -f "${skill_path}/main.py" ]; then
        cd "${skill_path}"
        python3 main.py > "${skill_log}" 2>&1 || exit_code=$?
    elif [ -f "${skill_path}/scripts/test.py" ]; then
        python3 "${skill_path}/scripts/test.py" > "${skill_log}" 2>&1 || exit_code=$?
    elif [ -f "${skill_path}/tests/test.py" ]; then
        python3 "${skill_path}/tests/test.py" > "${skill_log}" 2>&1 || exit_code=$?
    fi
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    if [ ${exit_code} -eq 0 ]; then
        echo -e "  ${GREEN}✓ ${skill} passed${NC} (${duration}s)"
        PASSED=$((PASSED + 1))
        status="passed"
    else
        echo -e "  ${RED}✗ ${skill} failed${NC} (${duration}s)"
        if [ "${VERBOSE}" = true ]; then
            echo "  Log: ${skill_log}"
            tail -20 "${skill_log}" | sed 's/^/    /'
        fi
        if [ "${SKIP_FAILING}" = true ]; then
            SKIPPED=$((SKIPPED + 1))
        else
            FAILED=$((FAILED + 1))
        fi
        status="failed"
    fi
    
    if [ "${first}" = true ]; then
        first=false
    else
        echo "," >> "${RESULTS_FILE}"
    fi
    
    echo "    {" >> "${RESULTS_FILE}"
    echo "      \"name\": \"${skill}\"," >> "${RESULTS_FILE}"
    echo "      \"status\": \"${status}\"," >> "${RESULTS_FILE}"
    echo "      \"duration\": ${duration}," >> "${RESULTS_FILE}"
    echo "      \"log\": \"${skill_log}\"" >> "${RESULTS_FILE}"
    echo -n "    }" >> "${RESULTS_FILE}"
}

# Run tests
if [ "${PARALLEL}" = true ]; then
    echo "Running tests in parallel..."
    for skill in ${SKILLS}; do
        test_skill "${skill}" &
    done
    wait
else
    for skill in ${SKILLS}; do
        test_skill "${skill}"
    done
fi

# Close JSON
echo "" >> "${RESULTS_FILE}"
echo "  ]," >> "${RESULTS_FILE}"
echo "  \"summary\": {" >> "${RESULTS_FILE}"
echo "    \"passed\": ${PASSED}," >> "${RESULTS_FILE}"
echo "    \"failed\": ${FAILED}," >> "${RESULTS_FILE}"
echo "    \"skipped\": ${SKIPPED}" >> "${RESULTS_FILE}"
echo "  }" >> "${RESULTS_FILE}"
echo "}" >> "${RESULTS_FILE}"

# Summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Test Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Total: ${TOTAL_SKILLS}"
echo -e "${GREEN}Passed: ${PASSED}${NC}"
if [ ${FAILED} -gt 0 ]; then
    echo -e "${RED}Failed: ${FAILED}${NC}"
else
    echo -e "Failed: ${FAILED}"
fi
echo -e "Skipped: ${SKIPPED}"

echo ""
echo "Results saved to: ${RESULTS_FILE}"

# Exit with failure if any tests failed
if [ ${FAILED} -gt 0 ] && [ "${SKIP_FAILING}" = false ]; then
    exit 1
fi

exit 0
