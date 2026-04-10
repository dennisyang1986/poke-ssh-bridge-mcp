#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import os
from typing import Any

from fastmcp import FastMCP
from fastmcp.exceptions import AuthorizationError
from fastmcp.server.dependencies import CurrentHeaders, get_http_request
from fastmcp.server.middleware import Middleware

from sshbridge import execute_command

SERVER_NAME = os.environ.get("POKE_MCP_NAME", "Poke MCP SSH Bridge").strip() or "Poke MCP SSH Bridge"
POKE_API_KEY = os.environ.get("POKE_API_KEY", "")
DEFAULT_CONNECT_TIMEOUT = float(os.environ.get("POKE_SSH_CONNECT_TIMEOUT", "10"))
DEFAULT_COMMAND_TIMEOUT = float(os.environ.get("POKE_SSH_COMMAND_TIMEOUT", "30"))


def _fingerprint_secret(secret: str) -> str:
    if not secret:
        return "missing"
    digest = hashlib.sha256(secret.encode("utf-8")).hexdigest()[:12]
    return f"len={len(secret)} sha256={digest}"


def _normalize_headers(headers: dict[str, str]) -> dict[str, str]:
    return {str(key).lower(): value for key, value in headers.items()}


def _extract_provided_secret(headers: dict[str, str]) -> tuple[str, str]:
    normalized_headers = _normalize_headers(headers)

    direct_secret = normalized_headers.get("x-poke-secret", "").strip()
    if direct_secret:
        return direct_secret, "x-poke-secret"

    authorization = normalized_headers.get("authorization", "").strip()
    if authorization.lower().startswith("bearer "):
        return authorization[7:].strip(), "authorization-bearer"

    return "", "missing"


def _require_api_key(headers: dict[str, str], *, context_label: str) -> None:
    expected_secret = POKE_API_KEY.strip()
    if not expected_secret:
        return

    normalized_headers = _normalize_headers(headers)
    provided_secret, provided_source = _extract_provided_secret(headers)
    if provided_secret != expected_secret:
        interesting_headers = sorted(normalized_headers.keys())
        print(
            "Auth mismatch "
            f"context={context_label} "
            f"source={provided_source} "
            f"provided={_fingerprint_secret(provided_secret)} "
            f"expected={_fingerprint_secret(expected_secret)} "
            f"headers={interesting_headers}",
            flush=True,
        )
        raise AuthorizationError("Unauthorized: invalid or missing X-Poke-Secret header.")

    print(
        "Auth matched "
        f"context={context_label} "
        f"source={provided_source} "
        f"provided={_fingerprint_secret(provided_secret)}",
        flush=True,
    )


def _require_api_key_from_request(*, context_label: str) -> None:
    request = get_http_request()
    headers = {str(name): str(value) for name, value in request.headers.items()}
    _require_api_key(headers, context_label=context_label)


class PokeApiKeyMiddleware(Middleware):
    async def on_request(self, context: Any, call_next: Any) -> Any:
        _require_api_key_from_request(context_label=f"mcp:{context.method}")
        return await call_next(context)


mcp = FastMCP(SERVER_NAME, middleware=[PokeApiKeyMiddleware()])


@mcp.tool(name="ssh_execute", description="Execute one command on a remote Linux host over SSH.")
def ssh_execute(
    host: str,
    username: str,
    command: str,
    port: int = 22,
    password: str | None = None,
    private_key: str | None = None,
    private_key_path: str | None = None,
    passphrase: str | None = None,
    connect_timeout: float = DEFAULT_CONNECT_TIMEOUT,
    command_timeout: float = DEFAULT_COMMAND_TIMEOUT,
    headers: dict[str, str] = CurrentHeaders(),
) -> dict:
    _require_api_key(headers, context_label="tool:ssh_execute")
    return execute_command(
        host=host,
        port=port,
        username=username,
        command=command,
        password=password,
        private_key=private_key,
        private_key_path=private_key_path,
        passphrase=passphrase,
        connect_timeout=connect_timeout,
        command_timeout=command_timeout,
    )


@mcp.tool(name="get_server_info", description="Get information about the MCP server including name, version, environment, and Python version")
def get_server_info(headers: dict[str, str] = CurrentHeaders()) -> dict:
    _require_api_key(headers, context_label="tool:get_server_info")
    return {
        "server_name": SERVER_NAME,
        "version": "1.0.0",
        "environment": os.environ.get("ENVIRONMENT", "development"),
        "python_version": os.sys.version.split()[0],
    }


def main() -> None:
    port = int(os.environ.get("POKE_MCP_PORT", os.environ.get("PORT", 8888)))
    host = os.environ.get("POKE_MCP_HOST", "0.0.0.0")

    print(f"Starting FastMCP server on {host}:{port}")

    mcp.run(
        transport="http",
        host=host,
        port=port,
        stateless_http=True,
    )


if __name__ == "__main__":
    main()
