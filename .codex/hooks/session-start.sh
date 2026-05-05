#!/usr/bin/env bash
set -euo pipefail

# Opt in so local Codex sessions do not unexpectedly download dependencies.
if [ "${AI_DISRUPTION_AUTO_SYNC:-}" != "true" ]; then
  exit 0
fi

if ! command -v uv &> /dev/null; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

cd "$(dirname "$0")/../.."
uv sync --all-extras
