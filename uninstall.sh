#!/usr/bin/env bash
# ==============================================================================
# /swarm - Uninstaller for Antigravity
# ==============================================================================

set -euo pipefail

CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.gemini/config}"
SKILLS_DIR="${CONFIG_DIR}/skills/swarm"
PLUGINS_DIR="${CONFIG_DIR}/plugins/swarm"
LEGACY_SKILLS_DIR="${CONFIG_DIR}/skills/agents"
LEGACY_PLUGINS_DIR="${CONFIG_DIR}/plugins/agents"

if [[ -d "${SKILLS_DIR}" ]]; then
    rm -rf "${SKILLS_DIR}"
    echo "[OK] Removed swarm skill from ${SKILLS_DIR}."
fi

if [[ -d "${PLUGINS_DIR}" ]]; then
    rm -rf "${PLUGINS_DIR}"
    echo "[OK] Removed swarm plugin from ${PLUGINS_DIR}."
fi

if [[ -d "${LEGACY_SKILLS_DIR}" ]]; then
    rm -rf "${LEGACY_SKILLS_DIR}"
    echo "[OK] Cleaned legacy agents skill from ${LEGACY_SKILLS_DIR}."
fi

if [[ -d "${LEGACY_PLUGINS_DIR}" ]]; then
    rm -rf "${LEGACY_PLUGINS_DIR}"
    echo "[OK] Cleaned legacy agents plugin from ${LEGACY_PLUGINS_DIR}."
fi

echo "[OK] /swarm uninstalled cleanly."
