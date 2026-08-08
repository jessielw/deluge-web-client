from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import niquests
import pytest

from deluge_web_client import (
    DelugeWebClient,
    DelugeWebClientConnectionError,
    DelugeWebClientDecodeError,
    DelugeWebClientError,
    DelugeWebClientHTTPError,
    DelugeWebClientRPCError,
    DelugeWebClientTimeoutError,
    TorrentOptions,
)
from tests import MockResponse


def test_login_connection_error_is_wrapped(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    """No Deluge instance at the URL must not leak a niquests exception."""
    client, mock_post = client_mock
    original = niquests.exceptions.ConnectionError("connection refused")
    mock_post.side_effect = original

    with pytest.raises(DelugeWebClientConnectionError) as exc_info:
        client.login()

    assert "Failed to reach Deluge Web UI at" in str(exc_info.value)
    assert exc_info.value.__cause__ is original
    # backwards compatibility: catching the base class still works
    assert isinstance(exc_info.value, DelugeWebClientError)


def test_connect_timeout_is_wrapped(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    """ConnectTimeout subclasses both ConnectionError and Timeout."""
    client, mock_post = client_mock
    mock_post.side_effect = niquests.exceptions.ConnectTimeout("too slow")

    with pytest.raises(DelugeWebClientTimeoutError, match="timed out after 30s"):
        client.login()


def test_read_timeout_is_wrapped(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    client, mock_post = client_mock
    mock_post.side_effect = niquests.exceptions.ReadTimeout("no reply")

    with pytest.raises(DelugeWebClientTimeoutError) as exc_info:
        client.get_free_space(timeout=5)

    assert "timed out after 5s" in str(exc_info.value)


def test_ssl_error_is_wrapped(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock
    mock_post.side_effect = niquests.exceptions.SSLError("bad certificate")

    with pytest.raises(DelugeWebClientConnectionError):
        client.get_hosts()


def test_upload_helper_connection_error_is_wrapped(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    """The upload path uses its own call site and must be wrapped too."""
    client, mock_post = client_mock
    mock_post.side_effect = niquests.exceptions.ConnectionError("connection refused")

    with pytest.raises(DelugeWebClientConnectionError):
        client.add_torrent_magnet("magnet:?xt=urn:btih:...", TorrentOptions())


def test_upload_torrents_preserves_subclass(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    """Batch uploads keep the specific subclass while adding context."""
    client, _ = client_mock

    with patch.object(DelugeWebClient, "upload_torrent") as mock_upload_torrent:
        mock_upload_torrent.side_effect = DelugeWebClientConnectionError("unreachable")

        with pytest.raises(DelugeWebClientConnectionError) as exc_info:
            client.upload_torrents(["path/to/torrent1.torrent"], TorrentOptions())

    assert str(exc_info.value).startswith("Failed to upload torrent1.torrent:")


def test_upload_torrents_non_deluge_error_uses_base(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    """Anything that is not already ours is wrapped in the base class."""
    client, _ = client_mock

    with patch.object(DelugeWebClient, "upload_torrent") as mock_upload_torrent:
        mock_upload_torrent.side_effect = OSError("file is unreadable")

        with pytest.raises(DelugeWebClientError) as exc_info:
            client.upload_torrents(["path/to/torrent1.torrent"], TorrentOptions())

    assert type(exc_info.value) is DelugeWebClientError
    assert "file is unreadable" in str(exc_info.value)


def test_http_error_carries_status(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    client, mock_post = client_mock
    mock_post.side_effect = (
        MockResponse(ok=False, status_code=404, reason="Not Found"),
    )

    with pytest.raises(DelugeWebClientHTTPError) as exc_info:
        client.login()

    assert exc_info.value.status_code == 404
    assert exc_info.value.reason == "Not Found"


def test_rpc_error_carries_method_and_class(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    client, mock_post = client_mock
    error = (
        "<class 'deluge.error.WrappedException'>: "
        "torrent 0407326f9d74629d299b525bd5f9b5dd5831b2c9 is broken"
    )
    mock_post.side_effect = (
        MockResponse(
            json_data={"result": None, "error": error, "id": 1},
            ok=True,
            status_code=200,
            reason="OK",
        ),
    )

    with pytest.raises(DelugeWebClientRPCError) as exc_info:
        client.get_free_space()

    assert exc_info.value.method == "core.get_free_space"
    assert exc_info.value.error_class == "deluge.error.WrappedException"
    assert exc_info.value.info_hash == "0407326f9d74629d299b525bd5f9b5dd5831b2c9"


def test_upload_helper_rpc_error(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    """A 200 response carrying an error is an RPC error, not an HTTP error."""
    client, mock_post = client_mock
    mock_post.side_effect = (
        MockResponse(
            json_data={"result": None, "error": "torrent file is invalid", "id": 1},
            ok=True,
            status_code=200,
            reason="OK",
        ),
    )

    with pytest.raises(DelugeWebClientRPCError) as exc_info:
        client.add_torrent_magnet("magnet:?xt=urn:btih:...", TorrentOptions())

    assert "Failed to add torrent" in str(exc_info.value)
    assert exc_info.value.method == "core.add_torrent_magnet"


def test_upload_helper_http_error(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    """A non-2xx response on the upload path is an HTTP error."""
    client, mock_post = client_mock
    mock_post.side_effect = (
        MockResponse(
            json_data={"result": None, "error": "nope", "id": 1},
            ok=False,
            status_code=503,
            reason="Service Unavailable",
        ),
    )

    with pytest.raises(DelugeWebClientHTTPError) as exc_info:
        client.add_torrent_magnet("magnet:?xt=urn:btih:...", TorrentOptions())

    assert exc_info.value.status_code == 503
    assert exc_info.value.reason == "Service Unavailable"


def test_decode_error(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock
    mock_post.side_effect = (
        MockResponse(json_data=["not", "an", "object"], ok=True, status_code=200),
    )

    with pytest.raises(DelugeWebClientDecodeError):
        client.get_free_space()


def test_post_does_not_mistake_body_errors_for_transport_errors(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    """Errors raised inside the `with` body must pass through untouched."""
    client, mock_post = client_mock
    mock_post.return_value.__enter__.return_value = MockResponse(
        json_data={"result": None, "error": None, "id": 1}, ok=True, status_code=200
    )

    payload: dict[str, Any] = {"method": "core.get_free_space", "params": []}
    with pytest.raises(RuntimeError, match="from the body"), client._post(payload, 30):  # pyright: ignore[reportPrivateUsage]
        raise RuntimeError("from the body")


@pytest.mark.parametrize(
    "exc_class",
    [
        DelugeWebClientConnectionError,
        DelugeWebClientTimeoutError,
        DelugeWebClientHTTPError,
        DelugeWebClientRPCError,
        DelugeWebClientDecodeError,
    ],
)
def test_subclasses_construct_with_message_only(
    exc_class: type[DelugeWebClientError],
) -> None:
    """`upload_torrents` reconstructs exceptions with only a message."""
    exc = exc_class("boom")

    assert isinstance(exc, DelugeWebClientError)
    assert str(exc) == "boom"


def test_optional_attributes_default_to_none() -> None:
    http_error = DelugeWebClientHTTPError("boom")
    rpc_error = DelugeWebClientRPCError("boom")

    assert http_error.status_code is None
    assert http_error.reason is None
    assert rpc_error.method is None
    assert rpc_error.error_class is None
    assert rpc_error.info_hash is None
