#!/usr/bin/env bash
# ==============================================================================
# /agents - Auto-Installer for Google Antigravity
# Multi-Agent Collaborative Coding Team for Gemini
# Repo: https://github.com/berlin-566/-agents
# Zero-Emoji Policy Enforced
# ==============================================================================

set -euo pipefail

# ANSI color codes for clean terminal output
BOLD='\033[1m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

echo -e "${BOLD}${CYAN}"
echo "  +------------------------------------------------------------+"
echo "  |             /agents for Google Antigravity                 |"
echo "  |     Claude-Style Multi-Agent Coding Team for Gemini        |"
echo "  +------------------------------------------------------------+"
echo -e "${NC}"

# Parse optional arguments
INSTALL_MODE="global"
for arg in "$@"; do
    case "$arg" in
        --local|--workspace)
            INSTALL_MODE="workspace"
            shift
            ;;
        --help|-h)
            echo "Usage: install.sh [--local|--help]"
            echo "  Default: Installs globally to ~/.gemini/config/skills/agents"
            echo "  --local: Installs into current workspace (.agents/skills/agents)"
            exit 0
            ;;
    esac
done

# Determine target directory
if [[ "${INSTALL_MODE}" == "workspace" ]]; then
    TARGET_DIR="$(pwd)/.agents/skills/agents"
    echo -e "[INFO] Installation Mode: ${YELLOW}Workspace (Local Project)${NC}"
else
    CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.gemini/config}"
    TARGET_DIR="${CONFIG_DIR}/skills/agents"
    echo -e "[INFO] Installation Mode: ${YELLOW}Global (~/.gemini/config/skills/agents)${NC}"
fi

REPO_RAW_URL="https://raw.githubusercontent.com/berlin-566/-agents/main"

# Step 1: Check if target directory exists
echo -e "[INFO] Checking target directory: ${GRAY}${TARGET_DIR}${NC}"
if [[ -d "${TARGET_DIR}" ]]; then
    echo -e "[INFO] Existing installation detected. Upgrading to the latest release..."
else
    echo -e "[INFO] Target directory not found. Creating directory tree automatically..."
fi

# Automatically create the required directory structure
mkdir -p "${TARGET_DIR}/references"
echo -e "[OK] Directory structure ready: ${GREEN}${TARGET_DIR}/references${NC}"

# Step 2: Detect execution source (Local repository vs Remote curl)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd || echo "")"

if [[ -n "${SCRIPT_DIR}" && -f "${SCRIPT_DIR}/SKILL.md" ]]; then
    echo -e "[INFO] Detected local repository at ${CYAN}${SCRIPT_DIR}${NC}. Copying files..."
    cp -f "${SCRIPT_DIR}/SKILL.md" "${TARGET_DIR}/SKILL.md"
    if [[ -d "${SCRIPT_DIR}/references" ]]; then
        cp -rf "${SCRIPT_DIR}/references/"* "${TARGET_DIR}/references/"
    fi
else
    echo -e "[INFO] Downloading files from GitHub repository (${CYAN}berlin-566/-agents${NC})..."
    
    # Check download utility
    DOWNLOAD_CMD=""
    if command -v curl >/dev/null 2>&1; then
        DOWNLOAD_CMD="curl -fsSL"
    elif command -v wget >/dev/null 2>&1; then
        DOWNLOAD_CMD="wget -qO-"
    else
        echo -e "${RED}[ERROR] Neither curl nor wget was found. Please install curl or wget to continue.${NC}"
        exit 1
    fi

    # Download required skill files
    echo -e "${GRAY}  -> Fetching SKILL.md...${NC}"
    ${DOWNLOAD_CMD} "${REPO_RAW_URL}/SKILL.md" > "${TARGET_DIR}/SKILL.md"

    echo -e "${GRAY}  -> Fetching references/agent_prompts.md...${NC}"
    ${DOWNLOAD_CMD} "${REPO_RAW_URL}/references/agent_prompts.md" > "${TARGET_DIR}/references/agent_prompts.md"

    echo -e "${GRAY}  -> Fetching references/team_orchestration.md...${NC}"
    ${DOWNLOAD_CMD} "${REPO_RAW_URL}/references/team_orchestration.md" > "${TARGET_DIR}/references/team_orchestration.md"
fi

# Step 3: Validate file integrity and size
REQUIRED_FILES=(
    "${TARGET_DIR}/SKILL.md"
    "${TARGET_DIR}/references/agent_prompts.md"
    "${TARGET_DIR}/references/team_orchestration.md"
)

INSTALL_VALID=true
for file in "${REQUIRED_FILES[@]}"; do
    if [[ ! -s "${file}" ]]; then
        echo -e "${RED}[ERROR] Verification failed for: ${file}${NC}"
        INSTALL_VALID=false
    fi
done

if [[ "${INSTALL_VALID}" == "true" ]]; then
    chmod -R 644 "${TARGET_DIR}"/*.md "${TARGET_DIR}/references"/*.md 2>/dev/null || true
    echo -e "\n${BOLD}${GREEN}[OK] Auto-installation completed successfully!${NC}\n"
    echo -e "Location: ${CYAN}${TARGET_DIR}${NC}\n"
    echo -e "How to use the multi-agent team in Antigravity:"
    echo -e "  1. Open your project in Antigravity"
    echo -e "  2. Create or open ${YELLOW}prd.md${NC} with your project requirements"
    echo -e "  3. Run: ${BOLD}${CYAN}/agents build prd.md${NC} (or simply ${BOLD}${CYAN}/agents${NC})\n"
    echo -e "Available subcommands:"
    echo -e "  - ${CYAN}/agents review${NC}      - Adversarial diff audit with zero-emoji enforcement"
    echo -e "  - ${CYAN}/agents test${NC}        - QA test generation and automated runner"
    echo -e "  - ${CYAN}/agents plan <task>${NC} - Architecture blueprint only"
    echo -e "  - ${CYAN}/agents decompose${NC}   - Modular work-stream mapping without writing code\n"
else
    echo -e "\n${RED}[ERROR] Installation failed. One or more files were not installed properly.${NC}"
    exit 1
fi
