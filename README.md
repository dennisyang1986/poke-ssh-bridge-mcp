# Poke SSH Bridge MCP

A Python MCP (Model Context Protocol) server that bridges Poke/AI agents to secure SSH access on remote Linux machines.

## What is this?

This deployment exposes only two MCP tools:
- `ssh_execute`: run shell commands on a remote SSH host
- `get_server_info`: retrieve basic information about the MCP server

## Requirements

- Python 3.10+ is required because fastmcp depends on it.
- `pip`

## Why it is useful

- Standardized MCP interface for remote server administration
- Authentication through a shared Poke secret header
- Password-based SSH and SSH key-based SSH support
- Simple deployment behind a tunnel or reverse proxy

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

The server listens on port 8888 by default. When adding this MCP server in Poke, use a URL like `https://your-domain.com/mcp`.

## Running the server

```bash
python main.py
```

Or use the console script after installing the project:

```bash
poke-ssh-bridge-mcp
```

A simple shell wrapper is also included:

```bash
./scripts/start.sh
```

## Security guidance

- Protect your Poke API key: never share or commit it
- Never commit `.env` files
- Never commit SSH private keys to the repository
- Keep the MCP server private and expose it only through a tunnel or proxy
- Restrict SSH users to the minimum permissions needed for your workflow

## License

This project is open source. See the repository license for details.
