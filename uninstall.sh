#!/usr/bin/env bash
# ==============================================================================
# /agents - Uninstaller for Antigravity
# ==============================================================================

set -euo pipefail

CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.gemini/config}"
TARGET_DIR="${CONFIG_DIR}/skills/agents"

if [[ -d "${TARGET_DIR}" ]]; then
    rm -rf "${TARGET_DIR}"
    echo "[OK] Successfully uninstalled /agents from ${TARGET_DIR}."
else
    echo "[INFO] /agents is not installed at ${TARGET_DIR}."
fi
