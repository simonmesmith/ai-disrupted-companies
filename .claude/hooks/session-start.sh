#!/bin/bash
set -euo pipefail

# Only run in remote (Claude Code on the web) environments
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Ensure build tools are up to date (--ignore-installed to bypass debian system packages)
pip install --ignore-installed setuptools wheel

# Install Python dependencies
pip install -r "$CLAUDE_PROJECT_DIR/requirements.txt"
