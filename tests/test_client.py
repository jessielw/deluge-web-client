from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from deluge_web_client import DelugeWebClientError
from deluge_web_client.client import DelugeWebClient
from tests import MockResponse


def test_enter(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, _ = client_mock

    with patch.object(DelugeWebClient, "login") as mock_login, client as c:
        mock_login.assert_called_once()
        assert c is client


def test_exit(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    mock_response = MockResponse(
        {"result": True, "error": None, "id": 0}, ok=True, status_code=200
    )
    mock_post.return_value.__enter__.return_value = mock_response

    with patch.object(DelugeWebClient, "close_session") as mock_close_session:
        with client:
            pass

        mock_close_session.assert_called_once()


def test_get_libtorrent_version(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(
            {"result": "2.0.10.0", "error": None, "id": 0},
            ok=True,
            status_code=200,
        ),
    )

    response = client.get_libtorrent_version()
    assert response.result == "2.0.10.0"
    assert mock_post.called
    assert mock_post.call_count == 1
    assert mock_post.call_args[1]["json"]["method"] == "core.get_libtorrent_version"


def test_get_listen_port(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(
            {"result": 6881, "error": None, "id": 0},
            ok=True,
            status_code=200,
        ),
    )

    response = client.get_listen_port()
    assert response.result == 6881
    assert mock_post.called
    assert mock_post.call_count == 1
    assert mock_post.call_args[1]["json"]["method"] == "core.get_listen_port"


def test_get_plugins(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    result_info = {
        "enabled_plugins": ["Label"],
        "available_plugins": [
            "AutoAdd",
            "Blocklist",
            "Execute",
            "Extractor",
            "Label",
            "Notifications",
            "Scheduler",
            "Stats",
            "Toggle",
            "WebUi",
        ],
    }

    mock_post.side_effect = (
        MockResponse(
            {
                "result": result_info,
                "error": None,
                "id": 2,
            },
            ok=True,
            status_code=200,
        ),
    )

    response = client.get_plugins()
    assert response.result == result_info
    assert mock_post.called
    assert mock_post.call_count == 1
    assert mock_post.call_args[1]["json"]["method"] == "web.get_plugins"


def test_check_connected(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(
            {"result": True, "error": None, "id": 0},
            ok=True,
            status_code=200,
        ),
    )

    response = client.check_connected()
    assert response.result is True
    assert mock_post.called
    assert mock_post.call_count == 1
    assert mock_post.call_args[1]["json"]["method"] == "web.connected"


def test_get_hosts(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    result_info = [["6a9de8fd92c449f49f6dcexxxxxxxxxx", "127.0.0.1", 58846, "user"]]

    mock_post.side_effect = (
        MockResponse(
            {"result": result_info, "error": None, "id": 0},
            ok=True,
            status_code=200,
        ),
    )

    response = client.get_hosts()
    assert response.result == result_info
    assert mock_post.called
    assert mock_post.call_count == 1
    assert mock_post.call_args[1]["json"]["method"] == "web.get_hosts"


def test_get_host_status(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    host_id = "6a9de8fd92c449f49f6dcexxxxxxxxxx"
    result_info = [host_id, "Connected", "2.1.1"]

    mock_post.side_effect = (
        MockResponse(
            {"result": result_info, "error": None, "id": 0},
            ok=True,
            status_code=200,
        ),
    )

    response = client.get_host_status(host_id)
    assert response.result == result_info
    assert mock_post.called
    assert mock_post.call_count == 1
    assert mock_post.call_args[1]["json"]["method"] == "web.get_host_status"


def test_connect_to_host(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    host_id = "6a9de8fd92c449f49f6dcexxxxxxxxxx"
    result_info = [
        "core.add_torrent_file",
        "core.add_torrent_file_async",
        "core.add_torrent_files",
        "core.add_torrent_magnet",
        "core.add_torrent_url",
        "...",
    ]

    mock_post.side_effect = (
        MockResponse(
            {"result": result_info, "error": None, "id": 0},
            ok=True,
            status_code=200,
        ),
    )

    response = client.connect_to_host(host_id)
    assert response.result == result_info
    assert mock_post.called
    assert mock_post.call_count == 1
    assert mock_post.call_args[1]["json"]["method"] == "web.connect"


def test_test_listen_port(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(
            {"result": True, "error": None, "id": 0},
            ok=True,
            status_code=200,
        ),
    )

    response = client.test_listen_port()
    assert response is True
    assert mock_post.called
    assert mock_post.call_count == 1
    assert mock_post.call_args[1]["json"]["method"] == "core.test_listen_port"

    mock_post.side_effect = (
        MockResponse(
            {"result": None, "error": None, "id": 1},
            ok=True,
            status_code=200,
        ),
    )

    response = client.test_listen_port()
    assert response is False
    assert mock_post.called
    assert mock_post.call_count == 2
    assert mock_post.call_args[1]["json"]["method"] == "core.test_listen_port"

    mock_post.side_effect = (
        MockResponse(
            {"result": False, "error": None, "id": 2},
            ok=True,
            status_code=200,
        ),
    )

    assert client.test_listen_port() is False


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("http://localhost:8112", "http://localhost:8112/json"),
        ("https://example.test/deluge/", "https://example.test/deluge/json"),
        ("https://example.test/json/", "https://example.test/json"),
        (
            "https://json.example.test/proxy?token=value",
            "https://json.example.test/proxy/json?token=value",
        ),
    ],
)
def test_build_url(source: str, expected: str) -> None:
    assert DelugeWebClient._build_url(source) == expected


@pytest.mark.parametrize(
    "url",
    ["localhost:8112", "ftp://example.test", "https://example.test/#fragment"],
)
def test_build_url_rejects_invalid_urls(url: str) -> None:
    with pytest.raises(ValueError):
        DelugeWebClient._build_url(url)


def test_execute_call_rejects_non_object_json(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    client, mock_post = client_mock
    mock_post.side_effect = (MockResponse([], ok=True, status_code=200),)

    with pytest.raises(
        DelugeWebClientError,
        match="Invalid JSON-RPC response: expected an object",
    ):
        client.execute_call({"method": "web.connected", "params": []})


def test_execute_call_with_error(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    client, _ = client_mock
    payload: dict[str, Any] = {
        "method": "core.add_torrent_file",
        "params": [],
        "id": 0,
    }

    # Simulate a response with an error in the 'error' key
    with (
        patch.object(
            client.session,
            "post",
            return_value=MockResponse(
                json_data={
                    "result": None,
                    "error": "Some error occurred",
                    "id": 1,
                },
                ok=True,
                status_code=200,
            ),
        ),
        pytest.raises(
            DelugeWebClientError, match=r"RPC Error - Method: core\.add_torrent_file"
        ),
    ):
        client.execute_call(payload)


def test_parse_deluge_error_coverage(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    client, _ = client_mock

    # Test 1: Empty error (Line 876)
    parsed = client._parse_deluge_error(None)
    assert parsed["message"] is None

    # Dict error without a class key but with a matching message.
    err_dict = {"message": "<class 'deluge.error.TestError'>: Test Message"}
    parsed = client._parse_deluge_error(err_dict)
    assert parsed["class"] == "deluge.error.TestError"

    # Test 3: String error matching regex (Line 897)
    err_str = "<class 'deluge.error.StringError'>: String Message"
    parsed = client._parse_deluge_error(err_str)
    assert parsed["class"] == "deluge.error.StringError"


def test_execute_call_invalid_json(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    client, mock_post = client_mock

    # Create a mock response that raises an exception when .json() is called
    mock_response = MagicMock()
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_response.text = "Invalid JSON body"
    mock_response.status_code = 200
    mock_response.reason = "OK"
    mock_post.return_value.__enter__.return_value = mock_response

    payload: dict[str, Any] = {
        "method": "core.add_torrent_file",
        "params": [],
        "id": 0,
    }
    with pytest.raises(DelugeWebClientError, match="Invalid JSON response"):
        client.execute_call(payload)
