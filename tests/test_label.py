from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from deluge_web_client import DelugeWebClientError, TorrentOptions
from deluge_web_client.client import DelugeWebClient
from deluge_web_client.schema import Response
from tests import MockResponse


def test_get_labels(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(
            {"result": ["movies", "shows"], "error": None, "id": 0},
            ok=True,
            status_code=200,
        ),
    )

    response = client.get_labels()
    assert response.result == ["movies", "shows"]
    assert mock_post.called
    assert mock_post.call_count == 1
    assert mock_post.call_args[1]["json"]["method"] == "label.get_labels"


def test_set_label(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(
            {"result": None, "error": None, "id": 0},
            ok=True,
            status_code=200,
        ),
    )

    response = client.set_label("ea5e27b8f2662a5xxxxxxxx214c94190xxxxxxxx", "movies")
    assert response.result is None
    assert mock_post.called
    assert mock_post.call_count == 1
    assert mock_post.call_args[1]["json"]["params"] == [
        "ea5e27b8f2662a5xxxxxxxx214c94190xxxxxxxx",
        "movies",
    ]
    assert mock_post.call_args[1]["json"]["method"] == "label.set_torrent"


def test_add_label_success(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(
            {"result": None, "error": None, "id": 0},
            ok=True,
            status_code=200,
        ),
    )

    response = client.add_label("movies")
    assert response.result is None
    assert mock_post.called
    assert mock_post.call_count == 1
    assert mock_post.call_args[1]["json"]["method"] == "label.add"


def test_add_label_already_exists(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    client, mock_post = client_mock

    already_exists_info = {
        "result": None,
        "error": {
            "message": "Label already exists",
            "code": 4,
        },
        "id": 1,
    }
    mock_post.side_effect = (
        MockResponse(
            already_exists_info,
            ok=True,
            status_code=200,
        ),
    )

    response = client.add_label("movies")
    assert response.result is None
    assert isinstance(response.error, dict)
    assert "Label already exists" in response.error.get("message", "")
    assert mock_post.called
    assert mock_post.call_count == 1
    assert mock_post.call_args[1]["json"]["method"] == "label.add"


def test_add_label_raises_error(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(
            {
                "result": None,
                "error": "Random error",
                "id": 2,
            },
            ok=True,
            status_code=200,
        ),
    )

    with pytest.raises(DelugeWebClientError, match="Error adding label:\nRandom error"):
        client.add_label("movies")


def test_apply_label(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, _ = client_mock

    # Mock both label operations to simulate their real responses.
    with (
        patch.object(
            DelugeWebClient,
            "add_label",
            side_effect=(
                Response(
                    result=None,
                    error=None,
                ),
            ),
        ) as mock_add_label,
        patch.object(
            DelugeWebClient,
            "set_label",
            side_effect=(
                Response(
                    result=None,
                    error=None,
                ),
            ),
        ) as mock_set_label,
    ):
        info_hash = "mocked_info_hash"
        label = "movies"
        timeout = 30

        # call the helper method
        response_add_label, response_set_label = client._apply_label(
            info_hash, label, timeout
        )

        # assert that add_label and set_label were called with correct arguments
        mock_add_label.assert_called_once_with(label, timeout)
        mock_set_label.assert_called_once_with(info_hash, label, timeout)

    # assert that the responses are as expected
    assert response_add_label.result is None
    assert response_set_label.result is None


def test_upload_helper_invalid_json(
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
        client._upload_helper(payload, label=None, timeout=30)


def test_upload_helper_already_exists(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(
            json_data={
                "result": None,
                "error": {
                    "message": (
                        "Torrent already in session "
                        "(1234567890abcdef1234567890abcdef12345678)"
                    ),
                    "code": 4,
                    "class": "deluge.error.AddTorrentError",
                },
                "id": 1,
            },
            ok=True,
            status_code=200,
        ),
    )

    payload: dict[str, Any] = {
        "method": "core.add_torrent_file",
        "params": [],
        "id": 0,
    }
    response = client._upload_helper(payload, label=None, timeout=30)
    assert response.result == "1234567890abcdef1234567890abcdef12345678"
    assert response.message == "Torrent already exists"


def test_upload_helper_duplicate_without_hash_raises(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    client, mock_post = client_mock
    mock_post.side_effect = (
        MockResponse(
            json_data={
                "result": None,
                "error": {
                    "message": "Torrent already in session",
                    "class": "deluge.error.AddTorrentError",
                },
            },
            ok=True,
            status_code=200,
        ),
    )

    with pytest.raises(DelugeWebClientError, match="Torrent already in session"):
        client._upload_helper(
            {"method": "core.add_torrent_file", "params": []},
            label=None,
            timeout=30,
        )


def test_upload_helper_unknown_error(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(
            json_data={
                "result": None,
                "error": {"message": "Unknown error"},
                "id": 1,
            },
            ok=True,
            status_code=200,
        ),
    )

    payload: dict[str, Any] = {
        "method": "core.add_torrent_file",
        "params": [],
        "id": 0,
    }
    with pytest.raises(DelugeWebClientError, match="Failed to add torrent"):
        client._upload_helper(payload, label=None, timeout=30)


def test_upload_helper_rejects_missing_torrent_id(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    client, mock_post = client_mock
    mock_post.side_effect = (
        MockResponse(
            json_data={"result": None, "error": None, "id": 1},
            ok=True,
            status_code=200,
        ),
    )

    with pytest.raises(DelugeWebClientError, match="returned no torrent ID"):
        client._upload_helper(
            {"method": "core.add_torrent_file", "params": []},
            label=None,
            timeout=30,
        )


def test_add_torrent_file(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    # Test for upload_torrent method which is not fully covered
    client, _ = client_mock

    with (
        patch("pathlib.Path.open", new_callable=MagicMock) as mock_file,
        patch.object(
            DelugeWebClient,
            "_upload_helper",
            return_value=Response(result="hash", error=None),
        ) as mock_upload,
    ):
        mock_file.return_value.__enter__.return_value.read.return_value = b"data"

        options = TorrentOptions(label="test")
        client.upload_torrent("test.torrent", options)

        mock_upload.assert_called_once()
        args = mock_upload.call_args
        assert args[0][1] == "test"
