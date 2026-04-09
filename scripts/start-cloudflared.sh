#!/usr/bin/env bash
set -euo pipefail

cd /root/poke-mcp-ssh-bridge

CONFIG_FILE="/root/poke-mcp-ssh-bridge/.cloudflared/config.yml"

if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "Missing cloudflared config file: $CONFIG_FILE" >&2
  exit 1
fi

exec /usr/local/bin/cloudflared tunnel --config "$CONFIG_FILE" run poke-mcp-ssh-bridge