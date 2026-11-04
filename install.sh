#!/usr/bin/env bash
# ==============================================================================
# /swarm - Auto-Installer for Google Antigravity
# Multi-Agent Swarm Orchestration Team for Gemini
# Repo: https://github.com/berlin-566/-swarm
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
echo "  |              /swarm for Google Antigravity                 |"
echo "  |        Multi-Agent Swarm Engineering Team for Gemini       |"
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
            echo "  --local: Installs into current workspace (.swarm/)"
            exit 0
            ;;
    esac
done

# Determine target directories
if [[ "${INSTALL_MODE}" == "workspace" ]]; then
    SKILLS_DIR="$(pwd)/.swarm/skills/swarm"
    PLUGINS_DIR="$(pwd)/.swarm/plugins/swarm"
    LEGACY_SKILLS_DIR="$(pwd)/.agents/skills/agents"
    LEGACY_PLUGINS_DIR="$(pwd)/.agents/plugins/agents"
    echo -e "[INFO] Installation Mode: ${YELLOW}Workspace (Local Project)${NC}"
else
    CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.gemini/config}"
    SKILLS_DIR="${CONFIG_DIR}/skills/swarm"
    PLUGINS_DIR="${CONFIG_DIR}/plugins/swarm"
    LEGACY_SKILLS_DIR="${CONFIG_DIR}/skills/agents"
    LEGACY_PLUGINS_DIR="${CONFIG_DIR}/plugins/agents"
    echo -e "[INFO] Installation Mode: ${YELLOW}Global (~/.gemini/config/)${NC}"
fi

REPO_RAW_URL="https://raw.githubusercontent.com/berlin-566/-swarm/main"

# Step 1: Clean legacy /agents installation to avoid clashes
if [[ -d "${LEGACY_SKILLS_DIR}" ]]; then
    echo -e "[INFO] Removing legacy skill: ${GRAY}${LEGACY_SKILLS_DIR}${NC}"
    rm -rf "${LEGACY_SKILLS_DIR}"
fi
if [[ -d "${LEGACY_PLUGINS_DIR}" ]]; then
    echo -e "[INFO] Removing legacy plugin: ${GRAY}${LEGACY_PLUGINS_DIR}${NC}"
    rm -rf "${LEGACY_PLUGINS_DIR}"
fi

# Step 2: Check and create directory trees
echo -e "[INFO] Checking target directories:"
echo -e "  - Skills:  ${GRAY}${SKILLS_DIR}${NC}"
echo -e "  - Plugins: ${GRAY}${PLUGINS_DIR}${NC}"

mkdir -p "${SKILLS_DIR}/references"
mkdir -p "${SKILLS_DIR}/scripts"
mkdir -p "${PLUGINS_DIR}/rules"
echo -e "[OK] Directory trees verified."

# Step 3: Detect execution source (Local repository vs Remote curl)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd || echo "")"

if [[ -n "${SCRIPT_DIR}" && -f "${SCRIPT_DIR}/SKILL.md" ]]; then
    echo -e "[INFO] Detected local repository at ${CYAN}${SCRIPT_DIR}${NC}. Installing files..."
    
    # Skill files
    cp -f "${SCRIPT_DIR}/SKILL.md" "${SKILLS_DIR}/SKILL.md"
    if [[ -d "${SCRIPT_DIR}/references" ]]; then
        cp -rf "${SCRIPT_DIR}/references/"* "${SKILLS_DIR}/references/"
    fi
    if [[ -d "${SCRIPT_DIR}/scripts" ]]; then
        cp -rf "${SCRIPT_DIR}/scripts/"* "${SKILLS_DIR}/scripts/"
        chmod +x "${SKILLS_DIR}/scripts/"*.py 2>/dev/null || true
    fi

    # Plugin and rule files
    if [[ -f "${SCRIPT_DIR}/plugin.json" ]]; then
        cp -f "${SCRIPT_DIR}/plugin.json" "${PLUGINS_DIR}/plugin.json"
    fi
    if [[ -d "${SCRIPT_DIR}/rules" ]]; then
        cp -rf "${SCRIPT_DIR}/rules/"* "${PLUGINS_DIR}/rules/"
    fi
else
    echo -e "[INFO] Downloading latest files from GitHub (${CYAN}berlin-566/-swarm${NC})..."
    
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

    # Download scripts
    echo -e "${GRAY}  -> Fetching scripts/swarm_bus.py...${NC}"
    ${DOWNLOAD_CMD} "${REPO_RAW_URL}/scripts/swarm_bus.py" > "${SKILLS_DIR}/scripts/swarm_bus.py"

    echo -e "${GRAY}  -> Fetching scripts/test_runner.py...${NC}"
    ${DOWNLOAD_CMD} "${REPO_RAW_URL}/scripts/test_runner.py" > "${SKILLS_DIR}/scripts/test_runner.py"

    echo -e "${GRAY}  -> Fetching scripts/emoji_linter.py...${NC}"
    ${DOWNLOAD_CMD} "${REPO_RAW_URL}/scripts/emoji_linter.py" > "${SKILLS_DIR}/scripts/emoji_linter.py"

    echo -e "${GRAY}  -> Fetching scripts/orchestrator.py...${NC}"
    ${DOWNLOAD_CMD} "${REPO_RAW_URL}/scripts/orchestrator.py" > "${SKILLS_DIR}/scripts/orchestrator.py"
    chmod +x "${SKILLS_DIR}/scripts/"*.py 2>/dev/null || true

    # Download plugin manifest and rules
    echo -e "${GRAY}  -> Fetching plugin.json...${NC}"
    ${DOWNLOAD_CMD} "${REPO_RAW_URL}/plugin.json" > "${PLUGINS_DIR}/plugin.json"

    echo -e "${GRAY}  -> Fetching rules/SWARM.md...${NC}"
    ${DOWNLOAD_CMD} "${REPO_RAW_URL}/rules/SWARM.md" > "${PLUGINS_DIR}/rules/SWARM.md"
fi

# Step 4: Validate file integrity and size
REQUIRED_FILES=(
    "${SKILLS_DIR}/SKILL.md"
    "${SKILLS_DIR}/references/agent_prompts.md"
    "${SKILLS_DIR}/references/team_orchestration.md"
    "${SKILLS_DIR}/scripts/swarm_bus.py"
    "${SKILLS_DIR}/scripts/test_runner.py"
    "${SKILLS_DIR}/scripts/emoji_linter.py"
    "${SKILLS_DIR}/scripts/orchestrator.py"
    "${PLUGINS_DIR}/plugin.json"
    "${PLUGINS_DIR}/rules/SWARM.md"
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

    echo -e "\n${BOLD}${GREEN}[OK] Swarm multi-agent engineering team installed successfully!${NC}\n"
    echo -e "Registered Specialist Agents in Swarm Roster:"
    echo -e "  - ${CYAN}gemini-architect${NC}           (Decomposition, contracts & specs)"
    echo -e "  - ${CYAN}gemini-coder${NC}               (Surgical polyglot implementation)"
    echo -e "  - ${CYAN}gemini-reviewer${NC}            (Adversarial auditor, zero-emoji gate)"
    echo -e "  - ${CYAN}gemini-tester${NC}              (QA engineer & automated test runner)"
    echo -e "  - ${CYAN}gemini-security-researcher${NC} (Vulnerability auditor, CVE hunter)"
    echo -e "  - ${CYAN}gemini-code-expert${NC}         (Algorithmic specialist, complex logic)"
    echo -e "  - ${CYAN}gemini-perf-expert${NC}         (Performance, memory & latency engineer)\n"
    echo -e "Engineered Team Tooling:"
    echo -e "  - ${GRAY}scripts/swarm_bus.py${NC}         - Inter-agent message bus & task board"
    echo -e "  - ${GRAY}scripts/test_runner.py${NC}       - Multi-framework QA test runner"
    echo -e "  - ${GRAY}scripts/emoji_linter.py${NC}      - Zero-emoji policy enforcer"
    echo -e "  - ${GRAY}scripts/orchestrator.py${NC}      - Workflow runner & delivery reporting\n"
    echo -e "Available commands in Antigravity:"
    echo -e "  - ${BOLD}${CYAN}/swarm [task]${NC}             - Interactive swarm selection & collaborative engineering"
    echo -e "  - ${BOLD}${CYAN}/swarm build prd.md${NC}       - Build PRD with autonomous swarm team"
    echo -e "  - ${CYAN}/swarm security${NC}             - Run deep security vulnerability audit"
    echo -e "  - ${CYAN}/swarm expert <topic>${NC}       - Consult domain & algorithmic code expert"
    echo -e "  - ${CYAN}/swarm perf${NC}                 - Profile memory leaks and CPU bottlenecks"
    echo -e "  - ${CYAN}/swarm review${NC}               - Adversarial diff audit with zero-emoji check"
    echo -e "  - ${CYAN}/swarm test${NC}                 - QA test generation and automated runner\n"
else
    echo -e "\n${RED}[ERROR] Installation failed. One or more files were not installed properly.${NC}"
    exit 1
fi
