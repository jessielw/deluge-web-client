from tests import MockResponse


def test_get_free_space(client_mock):
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(
            {"result": 1162332700672, "error": None, "id": 0}, ok=True, status_code=200
        ),
    )

    response = client.get_free_space()
    assert response.result == 1162332700672
    assert mock_post.called
    assert mock_post.call_count == 1
    assert mock_post.call_args[1]["json"]["method"] == "core.get_free_space"


def test_get_path_size(client_mock):
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(
            {"result": 83729670633, "error": None, "id": 0}, ok=True, status_code=200
        ),
    )

    response = client.get_path_size("/downloads")
    assert response.result == 83729670633
    assert mock_post.called
    assert mock_post.call_count == 1
    assert mock_post.call_args[1]["json"]["method"] == "core.get_path_size"
