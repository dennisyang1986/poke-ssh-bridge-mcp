#!/usr/bin/env bash
set -euo pipefail

cd /root/poke-mcp-ssh-bridge

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

export PYTHONPATH="/root/poke-mcp-ssh-bridge/src:/root/poke-mcp-ssh-bridge/.packages"
export PORT="${POKE_MCP_PORT:-8000}"
export ENVIRONMENT="${ENVIRONMENT:-production}"

exec /usr/bin/python3 src/server.py