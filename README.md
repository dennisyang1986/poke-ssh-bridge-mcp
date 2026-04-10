# Poke SSH Bridge MCP

A Python MCP (Model Context Protocol) server that bridges Poke/AI agents to secure SSH access on remote Linux machines.

## What this server exposes

This deployment exposes only two MCP tools:
- `ssh_execute`: run shell commands on a remote SSH host
- `get_server_info`: retrieve basic information about the MCP server

There is no file server, image relay, or base64 image handling endpoint in this deployment.

## Why it is useful

- Standardized MCP interface for remote server administration
- Authentication through a shared Poke secret header
- Password-based SSH and SSH key-based SSH support
- Simple deployment behind PM2 and a tunnel or reverse proxy

## Setup

### Prerequisites

- Python 3.10 or newer
- `pip`

### Installation

```bash
git clone https://your-domain.com/dennisyang1986/poke-ssh-bridge-mcp.git
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

The server listens on port 8888 by default. If you deploy it behind a tunnel or proxy, keep the local service on `127.0.0.1:8888` or `0.0.0.0:8888` and expose it externally through the tunnel.

## PM2 deployment

`ecosystem.config.cjs` is the PM2 process management file for this deployment. Use it to keep the MCP server and the optional tunnel process running, and to restart them automatically if they crash.

Example:

```bash
pm2 start ecosystem.config.cjs
pm2 save
```

## Exposing port 8888 publicly

The MCP server should stay private on the machine itself and be published through a tunnel or reverse proxy.

### Using frp

If you already have frp in your current setup, map the local service on port 8888 to the public side.

TCP or remote port mapping example:

```ini
[common]
server_addr = your-domain.com
server_port = 7000

auto_retry_interval = 3

[poke_mcp_http]
type = tcp
local_ip = 127.0.0.1
local_port = 8888
remote_port = 8888
```

If you prefer vhost/HTTP-style routing, point the public hostname at the tunnel and forward requests to the local MCP server:

```ini
[poke_mcp_http]
type = http
local_ip = 127.0.0.1
local_port = 8888
custom_domains = your-domain.com
```

In either case, make sure the public URL routes to the MCP endpoint path, for example `https://your-domain.com/mcp`.

### Using cloudflared

You can also expose the local service with Cloudflare Tunnel:

```bash
cloudflared tunnel --url http://127.0.0.1:8888
```

Or with an ingress rule:

```yaml
ingress:
  - hostname: your-domain.com
    service: http://127.0.0.1:8888
  - service: http_status:404
```

Then publish the MCP endpoint at `https://your-domain.com/mcp`.

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

## `ssh_execute` parameters

- `host`
- `username`
- `command`
- `port` optional, defaults to 22
- `password` optional
- `private_key` optional
- `private_key_path` optional
- `passphrase` optional

## `get_server_info` parameters

This tool takes no extra parameters.

## Security guidance

- Protect your Poke API key: never share or commit it
- Never commit `.env` files
- Never commit SSH private keys to the repository
- Keep the MCP server private and expose it only through a tunnel or proxy
- Restrict SSH users to the minimum permissions needed for your workflow

## License

This project is open source. See the repository license for details.
