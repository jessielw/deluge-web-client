import pytest
from tests import MockResponse
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
