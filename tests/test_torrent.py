import base64
import pytest
from pathlib import Path
from tests import MockResponse
from unittest.mock import patch, mock_open, MagicMock
from deluge_web_client import DelugeWebClientError


def test_upload_torrent(client_mock):
    client, _ = client_mock

    # Mock parameters for the test
    torrent_path = "mocked_torrent_file.torrent"
    # Mocked content of the torrent file
    mocked_file_content = b"mocked torrent file content"
    base64_encoded_content = base64.b64encode(mocked_file_content).decode("utf-8")

    # Mock the open function to simulate reading a torrent file
    with patch("builtins.open", mock_open(read_data=mocked_file_content)), patch.object(
        client, "_upload_helper", return_value=MagicMock(result=True, error=None)
    ) as mock_upload_helper:
        # Call the upload_torrent method
        response = client.upload_torrent(
            torrent_path, add_paused=True, save_directory="/downloads"
        )

    # Verify the response indicates success
    assert response.result is True
    assert response.error is None

    # Prepare expected payload for the upload_helper
    expected_payload = {
        "method": "core.add_torrent_file",
        "params": [
            str(torrent_path),
            base64_encoded_content,
            {
                "add_paused": True,
                "seed_mode": False,
                "auto_managed": False,
                "download_location": "/downloads",
            },
        ],
        "id": client.ID,
    }

    # Verify that the correct payload was sent to _upload_helper
    mock_upload_helper.assert_called_once_with(expected_payload, None, 30)


def test_upload_torrents(client_mock):
    client, _ = client_mock

    # Mock the responses for upload_torrent
    mock_responses = {
        "torrent1": MagicMock(result=True, error=None),
        "torrent2": MagicMock(result=True, error=None),
    }

    # Patch the upload_torrent method to return mocked responses
    with patch.object(client, "upload_torrent") as mock_upload_torrent:
        # Set side effects for multiple calls
        mock_upload_torrent.side_effect = [
            mock_responses["torrent1"],
            mock_responses["torrent2"],
        ]

        # Define the torrent paths to upload
        torrents = ["path/to/torrent1.torrent", "path/to/torrent2.torrent"]

        # Call the upload_torrents method
        results = client.upload_torrents(torrents, save_directory="/downloads")

    # Assertions to check that the responses are correct
    assert len(results) == 2
    assert results["torrent1"].result is True
    assert results["torrent2"].result is True
    assert results["torrent1"].error is None
    assert results["torrent2"].error is None

    # Verify that upload_torrent was called with the correct arguments
    mock_upload_torrent.assert_any_call(
        Path("path/to/torrent1.torrent"),
        save_directory="/downloads",
        label=None,
        timeout=30,
    )
    mock_upload_torrent.assert_any_call(
        Path("path/to/torrent2.torrent"),
        save_directory="/downloads",
        label=None,
        timeout=30,
    )


def test_upload_torrents_failure(client_mock):
    client, _ = client_mock

    # Mock the upload_torrent method to raise an exception for one of the torrents
    with patch.object(client, "upload_torrent") as mock_upload_torrent:
        mock_upload_torrent.side_effect = [
            MagicMock(result=True, error=None),  # First upload succeeds
            Exception("Upload failed"),  # Second upload fails
        ]

        torrents = ["path/to/torrent1.torrent", "path/to/torrent2.torrent"]

        # Expecting a DelugeWebClientError to be raised
        with pytest.raises(
            DelugeWebClientError, match="Failed to upload torrent2.torrent:"
        ):
            client.upload_torrents(torrents)

        # Verify that upload_torrent was called for both torrents
        mock_upload_torrent.assert_any_call(
            Path("path/to/torrent1.torrent"),
            save_directory=None,
            label=None,
            timeout=30,
        )
        mock_upload_torrent.assert_any_call(
            Path("path/to/torrent2.torrent"),
            save_directory=None,
            label=None,
            timeout=30,
        )


def test_add_torrent_magnet(client_mock):
    client, _ = client_mock
    magnet_uri = "magnet:?xt=urn:btih:...&dn=example"

    # Mock the response for _upload_helper
    mock_response = MagicMock()
    mock_response.json.return_value = {"result": "Ok", "id": client.ID}

    with patch.object(
        client, "_upload_helper", return_value=mock_response
    ) as mock_upload_helper:
        response = client.add_torrent_magnet(
            magnet_uri, add_paused=True, save_directory="/downloads"
        )

    # Assertions to check the response is as expected
    assert response == mock_response
    expected_payload = {
        "method": "core.add_torrent_magnet",
        "params": [
            str(magnet_uri),
            {
                "add_paused": True,
                "seed_mode": False,
                "auto_managed": False,
                "download_location": "/downloads",
            },
        ],
        "id": client.ID,
    }

    # Verify that the correct payload was sent to _upload_helper
    mock_upload_helper.assert_called_once_with(expected_payload, None, 30)


def test_add_torrent_magnet_failure(client_mock):
    client, _ = client_mock
    magnet_uri = "magnet:?xt=urn:btih:..."

    # Mock the _upload_helper to raise an exception
    with patch.object(
        client, "_upload_helper", side_effect=DelugeWebClientError("Upload failed")
    ):
        with pytest.raises(DelugeWebClientError, match=r".+"):
            client.add_torrent_magnet(magnet_uri)


def test_add_torrent_url(client_mock):
    client, _ = client_mock
    torrent_url = "http://example.com/torrent"

    # Mock the response for _upload_helper
    mock_response = MagicMock()
    mock_response.json.return_value = {"result": "Ok", "id": client.ID}

    with patch.object(
        client, "_upload_helper", return_value=mock_response
    ) as mock_upload_helper:
        response = client.add_torrent_url(
            torrent_url, add_paused=False, save_directory="/downloads"
        )

    # Assertions to check the response is as expected
    assert response == mock_response
    expected_payload = {
        "method": "core.add_torrent_url",
        "params": [
            str(torrent_url),
            {
                "add_paused": False,
                "seed_mode": False,
                "auto_managed": False,
                "download_location": "/downloads",
            },
        ],
        "id": client.ID,
    }

    # Verify that the correct payload was sent to _upload_helper
    mock_upload_helper.assert_called_once_with(expected_payload, None, 30)


def test_add_torrent_url_failure(client_mock):
    client, _ = client_mock
    torrent_url = "http://example.com/torrent"

    # Mock the _upload_helper to raise an exception
    with patch.object(
        client, "_upload_helper", side_effect=DelugeWebClientError("Upload failed")
    ):
        with pytest.raises(DelugeWebClientError, match=r".+"):
            client.add_torrent_url(torrent_url)


def test_upload_helper_success(client_mock):
    client, _ = client_mock
    payload = {"method": "core.add_torrent_file", "params": [], "id": 0}
    label = "Test Label"

    with patch.object(
        client.session,
        "post",
        return_value=MockResponse(
            json_data={"result": "info_hash"}, ok=True, status_code=200
        ),
    ):
        response = client._upload_helper(payload, label, timeout=30)

    assert response.result == "info_hash"
    assert response.error is None
    assert client.ID == 4


def test_upload_helper_failure(client_mock):
    client, _ = client_mock
    payload = {"method": "core.add_torrent_file", "params": [], "id": 0}
    label = "Test Label"

    with patch.object(
        client.session,
        "post",
        return_value=MockResponse(
            json_data={"result": "info_hash"}, ok=False, status_code=500
        ),
    ):
        with pytest.raises(DelugeWebClientError) as error_info:
            client._upload_helper(payload, label, timeout=30)
            assert (
                "Failed to upload file. Status code: 500, Reason: Internal Server Error"
                in str(error_info.value)
            )
