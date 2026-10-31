#!/usr/bin/env bash
# ==============================================================================
# /agents - Installer for Antigravity
# Multi-Agent Collaborative Coding Team for Gemini
# Repo: https://github.com/berlin-566/-agents
# ==============================================================================

set -euo pipefail

# ANSI color codes
BOLD='\033[1m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BOLD}${CYAN}"
echo "  +------------------------------------------------------------+"
echo "  |             /agents for Google Antigravity                 |"
echo "  |     Claude-Style Multi-Agent Coding Team for Gemini        |"
echo "  +------------------------------------------------------------+"
echo -e "${NC}"

# Target destination in Antigravity global config
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.gemini/config}"
TARGET_DIR="${CONFIG_DIR}/skills/agents"
REPO_RAW_URL="https://raw.githubusercontent.com/berlin-566/-agents/main"

echo -e "[INFO] Target installation directory: ${YELLOW}${TARGET_DIR}${NC}"

# Create directory structure
mkdir -p "${TARGET_DIR}/references"

# Check if installing from local directory or via curl/remote
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd || echo "")"

if [[ -n "${SCRIPT_DIR}" && -f "${SCRIPT_DIR}/SKILL.md" ]]; then
    echo -e "[INFO] Detected local repository at ${CYAN}${SCRIPT_DIR}${NC}. Installing locally..."
    cp -f "${SCRIPT_DIR}/SKILL.md" "${TARGET_DIR}/SKILL.md"
    if [[ -d "${SCRIPT_DIR}/references" ]]; then
        cp -rf "${SCRIPT_DIR}/references/"* "${TARGET_DIR}/references/"
    fi
else
    echo -e "[INFO] Downloading latest release from GitHub (${CYAN}berlin-566/-agents${NC})..."
    
    if ! command -v curl >/dev/null 2>&1; then
        echo -e "${RED}[ERROR] curl is required to install /agents via one-liner.${NC}"
        exit 1
    fi

    curl -fsSL "${REPO_RAW_URL}/SKILL.md" -o "${TARGET_DIR}/SKILL.md"
    curl -fsSL "${REPO_RAW_URL}/references/agent_prompts.md" -o "${TARGET_DIR}/references/agent_prompts.md"
    curl -fsSL "${REPO_RAW_URL}/references/team_orchestration.md" -o "${TARGET_DIR}/references/team_orchestration.md"
fi

# Verify installation
if [[ -f "${TARGET_DIR}/SKILL.md" ]]; then
    echo -e "\n${BOLD}${GREEN}[OK] Installation successful!${NC}\n"
    echo -e "To start using the multi-agent team in Antigravity:"
    echo -e "  1. Open your project in Antigravity"
    echo -e "  2. Create a ${YELLOW}prd.md${NC} file with your requirements"
    echo -e "  3. Run: ${BOLD}${CYAN}/agents build prd.md${NC} (or simply ${BOLD}${CYAN}/agents${NC})\n"
    echo -e "Other commands available:"
    echo -e "  - ${CYAN}/agents review${NC}  - Adversarial diff review"
    echo -e "  - ${CYAN}/agents test${NC}    - QA test generation and runner"
    echo -e "  - ${CYAN}/agents plan${NC}    - Architecture blueprint only\n"
else
    echo -e "\n${RED}[ERROR] Installation failed. Could not verify ${TARGET_DIR}/SKILL.md.${NC}"
    exit 1
fi
