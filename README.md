# Poke SSH Bridge MCP

A Python MCP (Model Context Protocol) server that bridges Poke/AI agents to secure SSH access on remote Linux machines.

## What is this?

This deployment exposes two MCP tools:
- `ssh_execute`: run shell commands on a remote SSH host
- `get_server_info`: retrieve basic information about the MCP server

## Why it is useful

- Standardized MCP interface for remote server administration
- Authentication through a shared Poke secret header
- Password-based SSH and SSH key-based SSH support
- Simple deployment behind a tunnel or reverse proxy

## Requirements

- Python 3.10+ is required because fastmcp depends on it.
- `pip`

## Setup

### Installation

```bash
git clone https://your-domain.com/poke-ssh-bridge-mcp.git
cd poke-ssh-bridge-mcp
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root:

```env
POKE_API_KEY=your-shared-secret-here
POKE_MCP_HOST=0.0.0.0
POKE_MCP_PORT=8888
POKE_SSH_CONNECT_TIMEOUT=10
POKE_SSH_COMMAND_TIMEOUT=30
```

Poke must be able to reach this bridge over the public internet, so port 8888 MUST be exposed externally. Binding only to localhost is not enough.
Poke must be able to reach this bridge over the public internet, so port 8888 MUST be exposed externally. Binding only to localhost is not enough.

If this machine is behind NAT or a home router, expose port 8888 with a tunnel or forwarding layer such as frp or cloudflared.

## Usage

Start the server from the repository root with the shell wrapper:

```bash
./scripts/start.sh
```

Or run the module directly:

```bash
PYTHONPATH=src python3 -m server
```

If you install the package, the console script also works:

```bash
poke-mcp-ssh-bridge
```

The server listens on port 8888 by default. Make sure your public endpoint forwards to that same port on the machine running the bridge.
pm2 save
pm2 startup
```

## Security guidance

- Keep `POKE_API_KEY` secret and rotate it if it is ever exposed
- Never commit `.env` files, SSH private keys, or other credentials
- Restrict the SSH account to the minimum permissions needed for your workflow
- Prefer key-based SSH auth where possible

## License

This project is open source. See the repository license for details.
