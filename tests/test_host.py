from __future__ import annotations

from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest

from deluge_web_client import Response
from deluge_web_client.client import DelugeWebClient
from tests import MockResponse


def test_start_daemon(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(
            json_data={"result": None, "error": None, "id": 1},
            ok=True,
            status_code=200,
        ),
    )

    response = client.start_daemon()
    assert response.result is None
    assert response.error is None
    assert mock_post.called
    assert mock_post.call_count == 1
    assert mock_post.call_args[1]["json"]["method"] == "web.start_daemon"
    assert mock_post.call_args[1]["json"]["params"] == [58846]  # default daemon_port


def test_start_daemon_custom_port(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    client, mock_post = client_mock
    client.daemon_port = 12345

    mock_post.side_effect = (
        MockResponse(
            json_data={"result": None, "error": None, "id": 1},
            ok=True,
            status_code=200,
        ),
    )

    client.start_daemon()
    assert mock_post.call_args[1]["json"]["params"] == [12345]


def test_stop_daemon(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(
            json_data={"result": None, "error": None, "id": 1},
            ok=True,
            status_code=200,
        ),
    )

    response = client.stop_daemon("host_id_123")
    assert response.result is None
    assert response.error is None
    assert mock_post.called
    assert mock_post.call_count == 1
    assert mock_post.call_args[1]["json"]["method"] == "web.stop_daemon"
    assert mock_post.call_args[1]["json"]["params"] == ["host_id_123"]


def test_update_ui(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    mock_ui_data = {
        "torrents": {"torrent_id_1": {"name": "Test Torrent"}},
        "stats": {"download_rate": 1000},
    }

    mock_post.side_effect = (
        MockResponse(
            json_data={"result": mock_ui_data, "error": None, "id": 1},
            ok=True,
            status_code=200,
        ),
    )

    response = client.update_ui()
    assert response.result == mock_ui_data
    assert response.error is None
    assert mock_post.called
    assert mock_post.call_count == 1
    assert mock_post.call_args[1]["json"]["method"] == "web.update_ui"
    assert mock_post.call_args[1]["json"]["params"] == [[], {}]


def test_update_ui_with_keys_and_filter(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(
            json_data={"result": {}, "error": None, "id": 1},
            ok=True,
            status_code=200,
        ),
    )

    keys = ["name", "size", "state"]
    filter_dict = {"state": "Downloading"}

    response = client.update_ui(keys=keys, filter_dict=filter_dict)
    assert response.error is None
    assert mock_post.call_args[1]["json"]["params"] == [keys, filter_dict]


def test_add_host(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(
            json_data={
                "result": [True, "f3558dd405924807a0c5e5a057f7a496"],
                "error": None,
                "id": 1,
            },
            ok=True,
            status_code=200,
        ),
    )

    response = client.add_host("testuser", "testpassword")
    assert response.result == [True, "f3558dd405924807a0c5e5a057f7a496"]
    assert response.error is None
    assert mock_post.called
    assert mock_post.call_count == 1
    assert mock_post.call_args[1]["json"]["method"] == "web.add_host"
    assert mock_post.call_args[1]["json"]["params"] == [
        "127.0.0.1",
        58846,
        "testuser",
        "testpassword",
    ]


def test_add_host_failure(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(
            json_data={
                "result": [False, "Connection failed"],
                "error": None,
                "id": 1,
            },
            ok=True,
            status_code=200,
        ),
    )

    response = client.add_host("testuser", "wrongpassword")
    assert response.result == [False, "Connection failed"]


def test_remove_host(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(
            json_data={"result": True, "error": None, "id": 1},
            ok=True,
            status_code=200,
        ),
    )

    response = client.remove_host("host_id_123")
    assert response.result is True
    assert response.error is None
    assert mock_post.called
    assert mock_post.call_count == 1
    assert mock_post.call_args[1]["json"]["method"] == "web.remove_host"
    assert mock_post.call_args[1]["json"]["params"] == ["host_id_123"]


def test_remove_host_failure(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(
            json_data={"result": False, "error": None, "id": 1},
            ok=True,
            status_code=200,
        ),
    )

    response = client.remove_host("invalid_host_id")
    assert response.result is False


def test_find_host_id_by_name(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, _ = client_mock

    # Mock the get_hosts method to return a list of hosts
    with patch.object(
        DelugeWebClient,
        "get_hosts",
        return_value=Response(
            result=[
                ["host_id_1", "127.0.0.1", 58846, "localclient"],
                ["host_id_2", "127.0.0.1", 58847, "remoteclient"],
            ],
            error=None,
        ),
    ):
        # Test finding existing host
        response = client.find_host_id_by_name("localclient")
        assert response.result == "host_id_1"
        assert response.error is None

        # Test finding another existing host
        response = client.find_host_id_by_name("remoteclient")
        assert response.result == "host_id_2"
        assert response.error is None


def test_find_host_id_by_name_not_found(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    client, _ = client_mock

    # Mock the get_hosts method
    with patch.object(
        DelugeWebClient,
        "get_hosts",
        return_value=Response(
            result=[["host_id_1", "127.0.0.1", 58846, "localclient"]], error=None
        ),
    ):
        # Test finding non-existent host
        response = client.find_host_id_by_name("nonexistent")
        assert response.result is None
        assert response.error is None


def test_find_host_id_by_name_no_hosts(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    client, _ = client_mock

    # Mock the get_hosts method to return empty list
    with patch.object(
        DelugeWebClient, "get_hosts", return_value=Response(result=[], error=None)
    ):
        response = client.find_host_id_by_name("anyhost")
        assert response.result is None
        assert response.error is None


def test_edit_host(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(
            json_data={"result": True, "error": None, "id": 1},
            ok=True,
            status_code=200,
        ),
    )

    response = client.edit_host("host_id_123", "newuser", "newpassword")
    assert response.result is True
    assert response.error is None
    assert mock_post.called
    assert mock_post.call_count == 1
    assert mock_post.call_args[1]["json"]["method"] == "web.edit_host"
    assert mock_post.call_args[1]["json"]["params"] == [
        "host_id_123",
        "127.0.0.1",
        58846,
        "newuser",
        "newpassword",
    ]


def test_edit_host_failure(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(
            json_data={"result": False, "error": None, "id": 1},
            ok=True,
            status_code=200,
        ),
    )

    response = client.edit_host("invalid_host_id", "user", "pass")
    assert response.result is False


def test_update_ui_defaults(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock
    mock_post.side_effect = (
        MockResponse({"result": {}, "error": None, "id": 1}, ok=True, status_code=200),
    )
    # Call without optional arguments to trigger defaults (lines 653-654)
    client.update_ui()

    assert mock_post.called
    # Verify defaults were substituted: keys=[], filter_dict={}
    assert mock_post.call_args[1]["json"]["params"] == [[], {}]


def test_find_host_id_by_name_malformed(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    client, _ = client_mock

    # Return a malformed host entry with no display name.
    with patch.object(
        DelugeWebClient,
        "get_hosts",
        return_value=Response(
            result=[["host_id_1"]],  # Missing name at index 3
            error=None,
        ),
    ):
        response = client.find_host_id_by_name("localclient")
        assert response.result is None


@pytest.mark.parametrize(
    "hosts",
    [
        "invalid",
        ["invalid"],
        [[123, "127.0.0.1", 58846, "localclient"]],
    ],
)
def test_find_host_id_by_name_rejects_invalid_results(
    client_mock: tuple[DelugeWebClient, MagicMock],
    hosts: object,
) -> None:
    client, _ = client_mock
    with patch.object(
        DelugeWebClient,
        "get_hosts",
        return_value=Response(result=cast(Any, hosts)),
    ):
        response = client.find_host_id_by_name("localclient")

    assert response.result is None
