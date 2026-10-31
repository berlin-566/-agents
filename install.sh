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
echo "  |     Multi-Agent Specialist Engineering Team for Gemini     |"
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
            echo "  Default: Installs globally to ~/.gemini/config/ (skills & plugins)"
            echo "  --local: Installs into current workspace (.agents/)"
            exit 0
            ;;
    esac
done

# Determine target directories
if [[ "${INSTALL_MODE}" == "workspace" ]]; then
    SKILLS_DIR="$(pwd)/.agents/skills/agents"
    PLUGINS_DIR="$(pwd)/.agents/plugins/agents"
    echo -e "[INFO] Installation Mode: ${YELLOW}Workspace (Local Project)${NC}"
else
    CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.gemini/config}"
    SKILLS_DIR="${CONFIG_DIR}/skills/agents"
    PLUGINS_DIR="${CONFIG_DIR}/plugins/agents"
    echo -e "[INFO] Installation Mode: ${YELLOW}Global (~/.gemini/config/)${NC}"
fi

REPO_RAW_URL="https://raw.githubusercontent.com/berlin-566/-agents/main"

# Step 1: Check and create directory trees
echo -e "[INFO] Checking target directories:"
echo -e "  - Skills:  ${GRAY}${SKILLS_DIR}${NC}"
echo -e "  - Plugins: ${GRAY}${PLUGINS_DIR}${NC}"

mkdir -p "${SKILLS_DIR}/references"
mkdir -p "${PLUGINS_DIR}/rules"
echo -e "[OK] Directory trees verified."

# Step 2: Detect execution source (Local repository vs Remote curl)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd || echo "")"

if [[ -n "${SCRIPT_DIR}" && -f "${SCRIPT_DIR}/SKILL.md" ]]; then
    echo -e "[INFO] Detected local repository at ${CYAN}${SCRIPT_DIR}${NC}. Installing files..."
    
    # Skill files
    cp -f "${SCRIPT_DIR}/SKILL.md" "${SKILLS_DIR}/SKILL.md"
    if [[ -d "${SCRIPT_DIR}/references" ]]; then
        cp -rf "${SCRIPT_DIR}/references/"* "${SKILLS_DIR}/references/"
    fi

    # Plugin and rule files
    if [[ -f "${SCRIPT_DIR}/plugin.json" ]]; then
        cp -f "${SCRIPT_DIR}/plugin.json" "${PLUGINS_DIR}/plugin.json"
    fi
    if [[ -d "${SCRIPT_DIR}/rules" ]]; then
        cp -rf "${SCRIPT_DIR}/rules/"* "${PLUGINS_DIR}/rules/"
    fi
else
    echo -e "[INFO] Downloading latest files from GitHub (${CYAN}berlin-566/-agents${NC})..."
    
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

    # Download skill files
    echo -e "${GRAY}  -> Fetching SKILL.md...${NC}"
    ${DOWNLOAD_CMD} "${REPO_RAW_URL}/SKILL.md" > "${SKILLS_DIR}/SKILL.md"

    echo -e "${GRAY}  -> Fetching references/agent_prompts.md...${NC}"
    ${DOWNLOAD_CMD} "${REPO_RAW_URL}/references/agent_prompts.md" > "${SKILLS_DIR}/references/agent_prompts.md"

    echo -e "${GRAY}  -> Fetching references/team_orchestration.md...${NC}"
    ${DOWNLOAD_CMD} "${REPO_RAW_URL}/references/team_orchestration.md" > "${SKILLS_DIR}/references/team_orchestration.md"

    # Download plugin manifest and rules
    echo -e "${GRAY}  -> Fetching plugin.json...${NC}"
    ${DOWNLOAD_CMD} "${REPO_RAW_URL}/plugin.json" > "${PLUGINS_DIR}/plugin.json"

    echo -e "${GRAY}  -> Fetching rules/AGENTS.md...${NC}"
    ${DOWNLOAD_CMD} "${REPO_RAW_URL}/rules/AGENTS.md" > "${PLUGINS_DIR}/rules/AGENTS.md"
fi

# Step 3: Validate file integrity and size
REQUIRED_FILES=(
    "${SKILLS_DIR}/SKILL.md"
    "${SKILLS_DIR}/references/agent_prompts.md"
    "${SKILLS_DIR}/references/team_orchestration.md"
    "${PLUGINS_DIR}/plugin.json"
    "${PLUGINS_DIR}/rules/AGENTS.md"
)

INSTALL_VALID=true
for file in "${REQUIRED_FILES[@]}"; do
    if [[ ! -s "${file}" ]]; then
        echo -e "${RED}[ERROR] Verification failed for: ${file}${NC}"
        INSTALL_VALID=false
    fi
done

if [[ "${INSTALL_VALID}" == "true" ]]; then
    chmod -R 644 "${SKILLS_DIR}"/*.md "${SKILLS_DIR}/references"/*.md 2>/dev/null || true
    chmod -R 644 "${PLUGINS_DIR}"/*.json "${PLUGINS_DIR}/rules"/*.md 2>/dev/null || true

    echo -e "\n${BOLD}${GREEN}[OK] Multi-agent system installed successfully!${NC}\n"
    echo -e "Registered Specialist Agents:"
    echo -e "  - ${CYAN}gemini-security-researcher${NC} (Vulnerability auditor, CVE hunter)"
    echo -e "  - ${CYAN}gemini-code-expert${NC}         (Algorithmic specialist, complex logic)"
    echo -e "  - ${CYAN}gemini-perf-expert${NC}         (Performance, memory & latency engineer)"
    echo -e "  - ${CYAN}gemini-architect${NC}           (PRD decomposition & system contracts)"
    echo -e "  - ${CYAN}gemini-coder${NC}               (Surgical polyglot implementation)"
    echo -e "  - ${CYAN}gemini-reviewer${NC}            (Adversarial auditor, zero-emoji gate)"
    echo -e "  - ${CYAN}gemini-tester${NC}              (QA engineer & automated test runner)\n"
    echo -e "Available commands in Antigravity:"
    echo -e "  - ${BOLD}${CYAN}/agents build prd.md${NC}       - Build complete PRD with the entire agent team"
    echo -e "  - ${CYAN}/agents security${NC}           - Run deep security vulnerability audit"
    echo -e "  - ${CYAN}/agents expert <topic>${NC}     - Consult domain & algorithmic code expert"
    echo -e "  - ${CYAN}/agents perf${NC}               - Profile memory leaks and CPU bottlenecks"
    echo -e "  - ${CYAN}/agents review${NC}             - Adversarial diff audit with zero-emoji check"
    echo -e "  - ${CYAN}/agents test${NC}               - QA test generation and automated runner\n"
else
    echo -e "\n${RED}[ERROR] Installation failed. One or more files were not installed properly.${NC}"
    exit 1
fi
