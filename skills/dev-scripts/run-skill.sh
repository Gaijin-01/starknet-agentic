#!/bin/bash
# run-skill.sh - Run a single skill test
# Usage: ./run-skill.sh <skill-name>

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="${SCRIPT_DIR}/../skills"
LOG_DIR="${SCRIPT_DIR}/../logs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Usage function
usage() {
    echo "Usage: $0 <skill-name>"
    echo ""
    echo "Available skills:"
    ls -1 "${SKILLS_DIR}" | grep -v dev-scripts | grep -v archived | head -20
    exit 1
}

# Check arguments
if [ $# -lt 1 ]; then
    usage
fi

SKILL_NAME="$1"
SKILL_PATH="${SKILLS_DIR}/${SKILL_NAME}"

# Check if skill exists
if [ ! -d "${SKILL_PATH}" ]; then
    echo -e "${RED}Error: Skill '${SKILL_NAME}' not found${NC}"
    echo "Available skills:"
    ls -1 "${SKILLS_DIR}" | grep -v dev-scripts | grep -v archived
    exit 1
fi

# Create log directory
mkdir -p "${LOG_DIR}"

# Log file
LOG_FILE="${LOG_DIR}/skill-${SKILL_NAME}-$(date +%Y%m%d-%H%M%S).log"

echo -e "${YELLOW}Running skill: ${SKILL_NAME}${NC}"
echo "Log file: ${LOG_FILE}"

# Check for main.py or test file
if [ -f "${SKILL_PATH}/main.py" ]; then
    echo "Found main.py, running..."
    cd "${SKILL_PATH}"
    python3 main.py 2>&1 | tee "${LOG_FILE}"
    EXIT_CODE=${PIPESTATUS[0]}
elif [ -f "${SKILL_PATH}/scripts/test.py" ]; then
    echo "Found scripts/test.py, running..."
    python3 "${SKILL_PATH}/scripts/test.py" 2>&1 | tee "${LOG_FILE}"
    EXIT_CODE=${PIPESTATUS[0]}
elif [ -f "${SKILL_PATH}/tests/test.py" ]; then
    echo "Found tests/test.py, running..."
    python3 "${SKILL_PATH}/tests/test.py" 2>&1 | tee "${LOG_FILE}"
    EXIT_CODE=${PIPESTATUS[0]}
else
    echo -e "${YELLOW}No test file found for ${SKILL_NAME}${NC}"
    echo "Checking skill structure..."
    
    # List skill contents
    echo -e "\n${YELLOW}Skill structure:${NC}"
    find "${SKILL_PATH}" -type f -name "*.py" | head -10
    
    # Check for SKILL.md
    if [ -f "${SKILL_PATH}/SKILL.md" ]; then
        echo -e "\n${YELLOW}Skill description:${NC}"
        head -30 "${SKILL_PATH}/SKILL.md"
    fi
    
    EXIT_CODE=0
fi

# Report result
if [ ${EXIT_CODE} -eq 0 ]; then
    echo -e "${GREEN}✓ Skill ${SKILL_NAME} completed successfully${NC}"
else
    echo -e "${RED}✗ Skill ${SKILL_NAME} failed with exit code ${EXIT_CODE}${NC}"
fi

exit ${EXIT_CODE}
