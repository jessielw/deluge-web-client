from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import Any, ClassVar, cast

from deluge_web_client import DelugeWebClient, Response


class _JsonRpcHandler(BaseHTTPRequestHandler):
    """Capture one JSON-RPC request and return a deterministic response."""

    request_data: ClassVar[dict[str, object]] = {}

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        body = cast(dict[str, Any], json.loads(self.rfile.read(length)))
        type(self).request_data = {
            "path": self.path,
            "content_type": self.headers.get("Content-Type"),
            "body": body,
        }

        response = json.dumps(
            {"result": True, "error": None, "id": body["id"]}
        ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, format: str, *args: object) -> None:
        """Suppress test-server logging."""


def test_real_http_request_contract() -> None:
    """Exercise URL, headers, payload IDs, and decoding through niquests."""
    server = ThreadingHTTPServer(("127.0.0.1", 0), _JsonRpcHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    client = DelugeWebClient(
        f"http://127.0.0.1:{server.server_port}/deluge",
        password="unused",
    )

    try:
        response = client.execute_call(
            {"method": "web.connected", "params": []}, timeout=5
        )
    finally:
        client.close_session()
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    assert response == Response(result=True)
    assert _JsonRpcHandler.request_data == {
        "path": "/deluge/json",
        "content_type": "application/json",
        "body": {"method": "web.connected", "params": [], "id": 1},
    }
