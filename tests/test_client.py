from unittest.mock import MagicMock
from tests import MockResponse


def test_enter(client_mock):
    client, _ = client_mock

    client.login = MagicMock()

    with client as c:
        client.login.assert_called_once()
        assert c is client


def test_exit(client_mock):
    client, mock_post = client_mock

    mock_response = MockResponse(
        {"result": True, "error": None, "id": 0}, ok=True, status_code=200
    )
    mock_post.return_value.__enter__.return_value = mock_response

    client.close_session = MagicMock()

    with client:
        pass

    client.close_session.assert_called_once()


def test_get_libtorrent_version(client_mock):
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


def test_get_listen_port(client_mock):
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


def test_get_plugins(client_mock):
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


def test_check_connected(client_mock):
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


def test_get_hosts(client_mock):
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


def test_get_host_status(client_mock):
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


def test_connect_to_host(client_mock):
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


def test_test_listen_port(client_mock):
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
