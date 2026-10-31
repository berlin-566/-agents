#!/usr/bin/env bash
# ==============================================================================
# /agents - Uninstaller for Antigravity
# ==============================================================================

set -euo pipefail

CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.gemini/config}"
SKILLS_DIR="${CONFIG_DIR}/skills/agents"
PLUGINS_DIR="${CONFIG_DIR}/plugins/agents"

if [[ -d "${SKILLS_DIR}" ]]; then
    rm -rf "${SKILLS_DIR}"
    echo "[OK] Removed skill from ${SKILLS_DIR}."
fi

if [[ -d "${PLUGINS_DIR}" ]]; then
    rm -rf "${PLUGINS_DIR}"
    echo "[OK] Removed plugin from ${PLUGINS_DIR}."
fi

echo "[OK] /agents uninstalled cleanly."
