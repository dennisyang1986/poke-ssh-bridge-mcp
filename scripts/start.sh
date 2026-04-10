#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

export PYTHONPATH="$(pwd)/src:$(pwd)/.packages${PYTHONPATH:+:$PYTHONPATH}"
export POKE_MCP_PORT="${POKE_MCP_PORT:-8888}"
export PORT="${PORT:-$POKE_MCP_PORT}"
export ENVIRONMENT="${ENVIRONMENT:-production}"

exec python3 -m poke_mcp_ssh_bridge.server
