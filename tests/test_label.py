import pytest
from tests import MockResponse
from unittest.mock import MagicMock
from deluge_web_client import DelugeWebClientError


def test_get_labels(client_mock):
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


def test_set_label(client_mock):
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


def test_add_label_success(client_mock):
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


def test_add_label_already_exists(client_mock):
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


def test_add_label_raises_error(client_mock):
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


def test_apply_label(client_mock):
    client, _ = client_mock

    # mock the add_label and set_label methods using side_effect to simulate real behavior
    client.add_label = MagicMock(
        side_effect=(
            MockResponse(
                {"result": None, "error": None, "id": 0},
                ok=True,
                status_code=200,
                reason="test",
            ),
        )
    )
    client.set_label = MagicMock(
        side_effect=(
            MockResponse(
                {"result": None, "error": None, "id": 1},
                ok=True,
                status_code=200,
                reason="test",
            ),
        )
    )

    info_hash = "mocked_info_hash"
    label = "movies"
    timeout = 30

    # call the helper method
    response_add_label, response_set_label = client._apply_label(
        info_hash, label, timeout
    )

    # assert that add_label and set_label were called with correct arguments
    client.add_label.assert_called_once_with(label, timeout)
    client.set_label.assert_called_once_with(info_hash, label, timeout)

    # assert that the responses are as expected
    assert response_add_label.json().get("result") is None
    assert response_add_label.json().get("id") == 0
    assert response_set_label.json().get("result") is None
    assert response_set_label.json().get("id") == 1
