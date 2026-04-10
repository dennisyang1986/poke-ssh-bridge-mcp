# Poke SSH Bridge MCP

A Python MCP (Model Context Protocol) server that bridges Poke/AI agents to secure SSH access on remote Linux machines.

## What is this?

Poke SSH Bridge MCP enables AI agents to securely execute commands and retrieve system information from remote Linux servers over SSH. It provides three core tools:
- `ssh_execute`: run shell commands on a remote SSH server
- `get_file_contents`: read a remote file and return its contents as raw text or base64
- `get_server_info`: retrieve basic system information from the remote server

![Poke SSH Bridge Architecture](https://pbs.twimg.com/media/HFdyKyYboAAPgYR?format=jpg&name=large)

## Why it is powerful for AI agents

- Seamless integration: AI agents can interact with remote servers using natural language through standardized MCP tools
- Secure access: built-in authentication with a shared Poke secret header
- Flexible authentication: supports password-based auth and SSH private keys, either inline or via file path
- Designed for production: ready to run behind secure tunnels like Cloudflare Tunnel

## Setup

### Prerequisites

- Python 3.10 or newer
- `pip`

### Installation

```bash
git clone https://github.com/dennisyang1986/poke-ssh-bridge-mcp.git
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

When adding this MCP server in Poke at poke.com/integrations/new, make sure the server URL includes the `/mcp` suffix. For example: `https://your-domain.com/mcp`.

The `ssh_execute` tool accepts these runtime parameters when you call it:
- `host`
- `username`
- `command`
- `port` optional, defaults to 22
- `password` optional
- `private_key` optional
- `private_key_path` optional
- `passphrase` optional

The `get_file_contents` tool accepts these runtime parameters when you call it:
- `host`
- `username`
- `remote_path`
- `port` optional, defaults to 22
- `password` optional
- `private_key` optional
- `private_key_path` optional
- `passphrase` optional
- `encoding` optional, either `base64` or `raw`, defaults to `base64`

## Running the server

```bash
python3 -m poke_mcp_ssh_bridge.server
```

Or use the console script after installing the project:

```bash
poke-ssh-bridge-mcp
```

A simple shell wrapper is also included:

```bash
./scripts/start.sh
```

## Network Configuration

If the MCP server runs inside a private network, expose it to the public internet before Poke can access it. Tools such as frp or Cloudflare Tunnel can be used to publish the server safely without opening direct inbound access to the private network.

## Security guidance

- Protect your Poke API key: never share or commit it
- Never commit `.env` files
- Never commit SSH private keys to the repository
- Use secure tunnels such as Cloudflare Tunnel when exposing the service remotely
- Restrict SSH users to the minimum permissions needed for your workflow

## License

This project is open source. See the repository license for details.
