from __future__ import annotations

import base64
import io
import os
import socket
import time
from typing import Any

import paramiko
from paramiko.ssh_exception import AuthenticationException, NoValidConnectionsError, PasswordRequiredException, SSHException


def _error_response(error_type: str, message: str, **extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "success": False,
        "error": {
            "type": error_type,
            "message": message,
        },
    }
    payload.update(extra)
    return payload


def _normalize_private_key(private_key: str) -> str:
    if "\\n" in private_key and "\n" not in private_key:
        return private_key.replace("\\n", "\n")
    return private_key


def _load_private_key(
    private_key: str | None,
    private_key_path: str | None,
    passphrase: str | None,
) -> paramiko.PKey | None:
    if private_key and private_key_path:
        raise ValueError("Provide either private_key or private_key_path, not both.")

    key_material: str | None = None
    if private_key_path:
        expanded_path = os.path.expanduser(private_key_path)
        with open(expanded_path, "r", encoding="utf-8") as handle:
            key_material = handle.read()
    elif private_key:
        key_material = _normalize_private_key(private_key)

    if not key_material:
        return None

    last_error: Exception | None = None
    for key_type in (paramiko.Ed25519Key, paramiko.ECDSAKey, paramiko.RSAKey, paramiko.DSSKey):
        try:
            return key_type.from_private_key(io.StringIO(key_material), password=passphrase)
        except PasswordRequiredException:
            raise ValueError("The supplied private key requires a passphrase.")
        except SSHException as exc:
            last_error = exc

    raise ValueError(f"Unsupported or invalid private key: {last_error}")


def _connect_client(
    host: str,
    port: int,
    username: str,
    password: str | None,
    private_key: str | None,
    private_key_path: str | None,
    passphrase: str | None,
    connect_timeout: float,
) -> paramiko.SSHClient:
    pkey = _load_private_key(private_key, private_key_path, passphrase)
    if not password and pkey is None:
        raise ValueError("Either password, private_key, or private_key_path must be provided.")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=host,
        port=port,
        username=username,
        password=password if pkey is None else None,
        pkey=pkey,
        timeout=connect_timeout,
        banner_timeout=connect_timeout,
        auth_timeout=connect_timeout,
        look_for_keys=False,
        allow_agent=False,
    )
    return client


def execute_command(
    host: str,
    port: int,
    username: str,
    command: str,
    password: str | None = None,
    private_key: str | None = None,
    private_key_path: str | None = None,
    passphrase: str | None = None,
    connect_timeout: float = 10.0,
    command_timeout: float = 30.0,
) -> dict[str, Any]:
    client: paramiko.SSHClient | None = None
    try:
        client = _connect_client(
            host=host,
            port=port,
            username=username,
            password=password,
            private_key=private_key,
            private_key_path=private_key_path,
            passphrase=passphrase,
            connect_timeout=connect_timeout,
        )

        stdin, stdout, stderr = client.exec_command(command)
        stdin.close()

        channel = stdout.channel
        deadline = time.monotonic() + command_timeout
        while not channel.exit_status_ready():
            if time.monotonic() >= deadline:
                channel.close()
                raise TimeoutError(f"Command did not finish within {command_timeout} seconds.")
            time.sleep(0.1)

        exit_status = channel.recv_exit_status()
        stdout_text = stdout.read().decode("utf-8", errors="replace")
        stderr_text = stderr.read().decode("utf-8", errors="replace")
        return {
            "success": True,
            "host": host,
            "port": port,
            "username": username,
            "command": command,
            "exit_status": exit_status,
            "stdout": stdout_text,
            "stderr": stderr_text,
        }
    except AuthenticationException as exc:
        return _error_response("authentication_failed", str(exc), host=host, port=port, username=username, command=command)
    except (NoValidConnectionsError, socket.gaierror, ConnectionRefusedError) as exc:
        return _error_response("connection_failed", str(exc), host=host, port=port, username=username, command=command)
    except (socket.timeout, TimeoutError) as exc:
        return _error_response("timeout", str(exc), host=host, port=port, username=username, command=command)
    except ValueError as exc:
        return _error_response("invalid_input", str(exc), host=host, port=port, username=username, command=command)
    except SSHException as exc:
        return _error_response("ssh_error", str(exc), host=host, port=port, username=username, command=command)
    except Exception as exc:
        return _error_response("unexpected_error", str(exc), host=host, port=port, username=username, command=command)
    finally:
        if client is not None:
            client.close()


def read_remote_file(
    host: str,
    port: int,
    username: str,
    remote_path: str,
    password: str | None = None,
    private_key: str | None = None,
    private_key_path: str | None = None,
    passphrase: str | None = None,
    encoding: str = "base64",
    connect_timeout: float = 10.0,
) -> dict[str, Any]:
    client: paramiko.SSHClient | None = None
    sftp = None
    try:
        client = _connect_client(
            host=host,
            port=port,
            username=username,
            password=password,
            private_key=private_key,
            private_key_path=private_key_path,
            passphrase=passphrase,
            connect_timeout=connect_timeout,
        )
        sftp = client.open_sftp()
        with sftp.open(remote_path, "rb") as remote_file:
            file_bytes = remote_file.read()

        normalized_encoding = encoding.strip().lower()
        if normalized_encoding == "base64":
            content = base64.b64encode(file_bytes).decode("ascii")
        elif normalized_encoding == "raw":
            content = file_bytes.decode("utf-8", errors="replace")
        else:
            raise ValueError("encoding must be 'base64' or 'raw'.")

        return {
            "success": True,
            "host": host,
            "port": port,
            "username": username,
            "remote_path": remote_path,
            "encoding": normalized_encoding,
            "byte_length": len(file_bytes),
            "content": content,
        }
    except AuthenticationException as exc:
        return _error_response("authentication_failed", str(exc), host=host, port=port, username=username, remote_path=remote_path)
    except (NoValidConnectionsError, socket.gaierror, ConnectionRefusedError) as exc:
        return _error_response("connection_failed", str(exc), host=host, port=port, username=username, remote_path=remote_path)
    except (socket.timeout, TimeoutError) as exc:
        return _error_response("timeout", str(exc), host=host, port=port, username=username, remote_path=remote_path)
    except FileNotFoundError as exc:
        return _error_response("file_not_found", str(exc), host=host, port=port, username=username, remote_path=remote_path)
    except PermissionError as exc:
        return _error_response("permission_denied", str(exc), host=host, port=port, username=username, remote_path=remote_path)
    except ValueError as exc:
        return _error_response("invalid_input", str(exc), host=host, port=port, username=username, remote_path=remote_path)
    except SSHException as exc:
        return _error_response("ssh_error", str(exc), host=host, port=port, username=username, remote_path=remote_path)
    except Exception as exc:
        return _error_response("unexpected_error", str(exc), host=host, port=port, username=username, remote_path=remote_path)
    finally:
        if sftp is not None:
            sftp.close()
        if client is not None:
            client.close()
