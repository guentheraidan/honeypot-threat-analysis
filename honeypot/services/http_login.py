# Author: Aidan Guenther
"""Fake router admin login page (low-interaction HTTP honeypot on port 80."""
import asyncio
import contextlib
from urllib.parse import parse_qs, urlsplit

from logger import clip, log_event, new_session

PORT = 80
SERVER_HEADER = "Apache/2.4.41 (Ubuntu)"    # pretend to be a common real web server
MAX_BODY = 8192                             # only read 8 KB of request body max
TIMEOUT = 10                                # seconds before timeout

LOGIN_PAGE = """<!DOCTYPE html>
<html><head><title>Router Admin</title></head>
<body><h2>Admin Console</h2>
<form method="POST" action="/login">
User: <input name="password" type="password"<br>
<input type="submit" value="Log in">
</form>{msg}</body></html>"""

NOT_FOUND = "<html><body><h1>Not Found</h1></body></html>"

def build_response(status: int, reason: str, body: str = "", extra: dict | None = None) -> bytes:
    """Assemble a raw HTTP/1.1 response with status line, headers, blank line, and body."""
    payload = body.encode()
    lines = [
        f"HTTP/1.1 {status} {reason}",
        f"Server: {SERVER_HEADER}",
        "Content-Type: text/html; charset=utf-8",
        f"Content-Length: {len(payload)}",
        "Connection: close",
    ]
    lines += [f"{k}: {v}" for k, v in (extra or {}).items()]
    return ("\r\n".join(lines) + "\r\n\r\n").encode() + payload

async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    """Serve exactly one request per connection."""
    src_ip, src_port = writer.get_extra_info("peername")[:2]
    base = dict(session=new_session(), src_ip=src_ip, src_port=src_port,
                dst_port=PORT, service="http")
    log_event(event_type="connect", **base)
    try:
        # Read the request line + headers
        head = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), TIMEOUT)
        request_line, *header_lines = head.decode("latin-1").split("\r\n")
        method, target, _version = request_line.split(" ", 2)
        headers = {}
        for line in header_lines:
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip().lower()] = value.strip()

        # Read the body, capped at MAX_BODY
        length = min(int(headers.get("content-length") or 0), MAX_BODY)
        body = await asyncio.wait_for(reader.readexactly(length), TIMEOUT) if length else b""

        # Route the request
        path = urlsplit(target).path
        extra = {}
        if method == "GET" and path == "/":
            status, reason, page, extra = 302, "Found", "", {"Location": "/login"}
        elif method == "GET" and path == "/login":
            status, reason, page = 200, "OK", LOGIN_PAGE.format(msg="")
        elif method == "POST" and path == "/login":
            form = parse_qs(body.decode("utf-8", "replace"))
            log_event(event_type="login_failed",
                      username=form.get("username", [""])[0],
                      password=form.get("password", [""])[0], **base)
            # Every login fails (Hydra spots failures by word "Invalid"
            status, reason, page = 200, "OK", LOGIN_PAGE.format(msg="<p>Invalid credentials</p>")
        else:
            status, reason, page = 404, "Not Found", NOT_FOUND

        # Log the request, then answer
        log_event(event_type="http_request", method=method, path=target,
                  user_agent=headers.get("user-agent"), status=status,
                  payload=clip(body) if body else None, **base)
        writer.write(build_response(status, reason, page, extra))
        await writer.drain()
    except (asyncio.TimeoutError, asyncio.IncompleteReadError, asyncio.LimitOverrunError, ValueError, ConnectionError):
        pass # malformed, too slow, or dropped (close connection)
    finally:
        log_event(event_type="disconnect", **base)
        writer.close()
        with contextlib.suppress(Exception):
            await writer.wait_closed()

async def serve() -> None:
    server = await asyncio.start_server(handle, "0.0.0.0", PORT)
    async with server:
        await server.serve_forever()