from __future__ import annotations

from pathlib import Path
from typing import Any, cast
from unittest.mock import MagicMock, mock_open, patch

import pytest

from deluge_web_client import DelugeWebClientError, TorrentOptions
from deluge_web_client.client import DelugeWebClient
from tests import MockResponse, example_multi_status_dict, example_status_dict


def test_upload_torrent(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, _ = client_mock

    # Mock parameters for the test
    torrent_path = "mocked_torrent_file.torrent"
    # Mocked content of the torrent file
    mocked_file_content = b"mocked torrent file content"

    # Mock the open function to simulate reading a torrent file
    with (
        patch("pathlib.Path.open", mock_open(read_data=mocked_file_content)),
        patch.object(
            DelugeWebClient,
            "_upload_helper",
            return_value=MagicMock(result=True, error=None),
        ) as mock_upload_helper,
    ):
        # Call the upload_torrent method
        options = TorrentOptions(add_paused=True, download_location="/downloads")
        response = client.upload_torrent(torrent_path, options)

    # Verify the response indicates success
    assert response.result is True
    assert response.error is None

    # Prepare expected payload for the upload_helper
    # Verify that the correct payload was sent to _upload_helper
    mock_upload_helper.assert_called_once()
    called_payload, called_label, called_timeout = mock_upload_helper.call_args[0]
    assert called_payload["method"] == "core.add_torrent_file"
    assert called_payload["params"][0] == str(torrent_path)
    assert called_label is None
    assert called_timeout == 30


def test_upload_torrents(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, _ = client_mock

    # Mock the responses for upload_torrent
    mock_responses = {
        "torrent1": MagicMock(result=True, error=None),
        "torrent2": MagicMock(result=True, error=None),
    }

    # Patch the upload_torrent method to return mocked responses
    with patch.object(DelugeWebClient, "upload_torrent") as mock_upload_torrent:
        # Set side effects for multiple calls
        mock_upload_torrent.side_effect = [
            mock_responses["torrent1"],
            mock_responses["torrent2"],
        ]

        # Define the torrent paths to upload
        torrents = ["path/to/torrent1.torrent", "path/to/torrent2.torrent"]
        options = TorrentOptions(download_location="/downloads", label=None)

        # Call the upload_torrents method
        results = client.upload_torrents(torrents, options)

    # Assertions to check that the responses are correct
    assert len(results) == 2
    assert results["torrent1"].result is True
    assert results["torrent2"].result is True
    assert results["torrent1"].error is None
    assert results["torrent2"].error is None

    # Verify that upload_torrent was called with the correct arguments
    mock_upload_torrent.assert_any_call(
        Path("path/to/torrent1.torrent"),
        torrent_options=options,
        timeout=30,
    )
    mock_upload_torrent.assert_any_call(
        Path("path/to/torrent2.torrent"),
        torrent_options=options,
        timeout=30,
    )


def test_upload_torrents_failure(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    client, _ = client_mock

    # Mock the upload_torrent method to raise an exception for one of the torrents
    with patch.object(DelugeWebClient, "upload_torrent") as mock_upload_torrent:
        mock_upload_torrent.side_effect = [
            MagicMock(result=True, error=None),  # First upload succeeds
            Exception("Upload failed"),  # Second upload fails
        ]

        torrents = ["path/to/torrent1.torrent", "path/to/torrent2.torrent"]
        options = TorrentOptions()

        # Expecting a DelugeWebClientError to be raised
        with pytest.raises(
            DelugeWebClientError, match=r"Failed to upload torrent2\.torrent:"
        ):
            client.upload_torrents(torrents, options)

        # Verify that upload_torrent was called for both torrents
        assert mock_upload_torrent.call_count == 2


def test_add_torrent_magnet(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, _ = client_mock
    magnet_uri = "magnet:?xt=urn:btih:...&dn=example"

    # Mock the response for _upload_helper
    mock_response = MagicMock()
    mock_response.json.return_value = {"result": "Ok", "id": 0}

    with patch.object(
        DelugeWebClient, "_upload_helper", return_value=mock_response
    ) as mock_upload_helper:
        options = TorrentOptions(add_paused=True, download_location="/downloads")
        response = client.add_torrent_magnet(magnet_uri, options)

    # Assertions to check the response is as expected
    assert response == mock_response
    # Verify that the correct payload was sent to _upload_helper
    mock_upload_helper.assert_called_once()
    called_payload = mock_upload_helper.call_args[0][0]
    assert called_payload["method"] == "core.add_torrent_magnet"
    assert called_payload["params"][0] == str(magnet_uri)


def test_add_torrent_magnet_failure(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    client, _ = client_mock
    magnet_uri = "magnet:?xt=urn:btih:..."

    # Mock the _upload_helper to raise an exception
    with (
        patch.object(
            DelugeWebClient,
            "_upload_helper",
            side_effect=DelugeWebClientError("Upload failed"),
        ),
        pytest.raises(DelugeWebClientError, match=r".+"),
    ):
        options = TorrentOptions()
        client.add_torrent_magnet(magnet_uri, options)


def test_add_torrent_url(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, _ = client_mock
    torrent_url = "http://example.com/torrent"

    # Mock the response for _upload_helper
    mock_response = MagicMock()
    mock_response.json.return_value = {"result": "Ok", "id": 0}

    with patch.object(
        DelugeWebClient, "_upload_helper", return_value=mock_response
    ) as mock_upload_helper:
        options = TorrentOptions(add_paused=False, download_location="/downloads")
        response = client.add_torrent_url(torrent_url, options)

    # Assertions to check the response is as expected
    assert response == mock_response
    # Verify that the correct payload was sent to _upload_helper
    mock_upload_helper.assert_called_once()
    called_payload = mock_upload_helper.call_args[0][0]
    assert called_payload["method"] == "core.add_torrent_url"
    assert called_payload["params"][0] == str(torrent_url)


def test_add_torrent_url_failure(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    client, _ = client_mock
    torrent_url = "http://example.com/torrent"

    # Mock the _upload_helper to raise an exception
    with (
        patch.object(
            DelugeWebClient,
            "_upload_helper",
            side_effect=DelugeWebClientError("Upload failed"),
        ),
        pytest.raises(DelugeWebClientError, match=r".+"),
    ):
        options = TorrentOptions()
        client.add_torrent_url(torrent_url, options)


def test_upload_helper_success(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, _ = client_mock
    payload: dict[str, Any] = {"method": "core.add_torrent_file", "params": [], "id": 0}
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
    # client.ID counter removed; ensure we get a valid response and no exceptions


def test_upload_helper_success_without_label(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    client, mock_post = client_mock
    mock_post.side_effect = (
        MockResponse(
            json_data={"result": "info_hash", "error": None},
            ok=True,
            status_code=200,
        ),
    )

    response = client._upload_helper(
        {"method": "core.add_torrent_file", "params": []},
        label=None,
        timeout=30,
    )

    assert response.result == "info_hash"


def test_upload_helper_failure(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, _ = client_mock
    payload: dict[str, Any] = {"method": "core.add_torrent_file", "params": [], "id": 0}
    label = "Test Label"

    with (
        patch.object(
            client.session,
            "post",
            return_value=MockResponse(
                json_data={"result": "info_hash"}, ok=False, status_code=500
            ),
        ),
        pytest.raises(DelugeWebClientError) as error_info,
    ):
        client._upload_helper(payload, label, timeout=30)
        assert (
            "Failed to upload file. Status code: 500, Reason: Internal Server Error"
            in str(error_info.value)
        )


def test_get_torrent_files(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    contents = {
        "contents": {
            "Random.Movie.2006.BluRay.720p-BHDStudio.mp4": {
                "type": "file",
                "index": 0,
                "path": "Random.Movie.2006.BluRay.720p-BHDStudio.mp4",
                "size": 3515992406,
                "offset": 0,
                "progress": 1.0,
                "priority": 1,
            }
        },
        "type": "dir",
    }

    mock_post.side_effect = (
        MockResponse(
            {
                "result": contents,
                "error": None,
                "id": 1,
            },
            ok=True,
            status_code=200,
        ),
    )

    response = client.get_torrent_files("mock_torrent_id")
    assert response.error is None
    assert response.result == contents
    assert mock_post.called
    assert mock_post.call_count == 1
    assert mock_post.call_args[1]["json"]["method"] == "web.get_torrent_files"


def test_get_torrent_status(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(
            {
                "result": example_status_dict,
                "error": None,
                "id": 1,
            },
            ok=True,
            status_code=200,
        ),
    )

    response = client.get_torrent_status("mock_torrent_id")
    assert response.error is None
    assert response.result == example_status_dict
    assert mock_post.called
    assert mock_post.call_count == 1
    assert mock_post.call_args[1]["json"]["method"] == "core.get_torrent_status"


def test_get_torrents_status(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(
            {
                "result": example_multi_status_dict,
                "error": None,
                "id": 1,
            },
            ok=True,
            status_code=200,
        ),
    )

    response = client.get_torrents_status(cast(Any, "mock_torrent_id"))
    assert response.error is None
    assert response.result == example_multi_status_dict
    assert mock_post.called
    assert mock_post.call_count == 1
    assert mock_post.call_args[1]["json"]["method"] == "core.get_torrents_status"


def test_pause_torrent(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(
            {
                "result": None,
                "error": None,
                "id": 1,
            },
            ok=True,
            status_code=200,
        ),
    )

    response = client.pause_torrent("mock_torrent_id")
    assert response.error is None
    assert response.result is None
    assert mock_post.called
    assert mock_post.call_count == 1
    assert mock_post.call_args[1]["json"]["method"] == "core.pause_torrent"


def test_pause_torrents(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(
            {
                "result": None,
                "error": None,
                "id": 1,
            },
            ok=True,
            status_code=200,
        ),
    )

    response = client.pause_torrents(["mock_torrent_id1", "mock_torrent_id2"])
    assert response.error is None
    assert response.result is None
    assert mock_post.called
    assert mock_post.call_count == 1
    assert mock_post.call_args[1]["json"]["method"] == "core.pause_torrents"


def test_remove_torrent(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(
            {
                "result": None,
                "error": None,
                "id": 1,
            },
            ok=True,
            status_code=200,
        ),
        MockResponse(
            {
                "result": None,
                "error": None,
                "id": 2,
            },
            ok=True,
            status_code=200,
        ),
    )

    response = client.remove_torrent("mock_torrent_id")
    assert response.error is None
    assert response.result is None
    assert mock_post.called
    assert mock_post.call_count == 1
    assert mock_post.call_args[1]["json"]["method"] == "core.remove_torrent"
    assert mock_post.call_args[1]["json"]["params"] == ["mock_torrent_id", False]

    # Second call: remove_data=True
    response = client.remove_torrent("mock_torrent_id", remove_data=True)
    assert mock_post.call_args[1]["json"]["params"] == ["mock_torrent_id", True]


def test_remove_torrents(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    # Provide two responses for two calls
    mock_post.side_effect = (
        MockResponse(
            {
                "result": None,
                "error": None,
                "id": 1,
            },
            ok=True,
            status_code=200,
        ),
        MockResponse(
            {
                "result": None,
                "error": None,
                "id": 2,
            },
            ok=True,
            status_code=200,
        ),
    )

    response = client.remove_torrents(["mock_torrent_id1", "mock_torrent_id2"])
    assert response.error is None
    assert response.result is None
    assert mock_post.called
    assert mock_post.call_count == 1
    assert mock_post.call_args[1]["json"]["method"] == "core.remove_torrents"
    assert mock_post.call_args[1]["json"]["params"] == [
        ["mock_torrent_id1", "mock_torrent_id2"],
        False,
    ]

    response = client.remove_torrents(
        ["mock_torrent_id1", "mock_torrent_id2"], remove_data=True
    )
    assert mock_post.call_args[1]["json"]["params"] == [
        ["mock_torrent_id1", "mock_torrent_id2"],
        True,
    ]


def test_resume_torrent(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(
            {
                "result": None,
                "error": None,
                "id": 1,
            },
            ok=True,
            status_code=200,
        ),
    )

    response = client.resume_torrent("mock_torrent_id")
    assert response.error is None
    assert response.result is None
    assert mock_post.called
    assert mock_post.call_count == 1
    assert mock_post.call_args[1]["json"]["method"] == "core.resume_torrent"


def test_resume_torrents(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(
            {
                "result": None,
                "error": None,
                "id": 1,
            },
            ok=True,
            status_code=200,
        ),
    )

    response = client.resume_torrents(["mock_torrent_id1", "mock_torrent_id2"])
    assert response.error is None
    assert response.result is None
    assert mock_post.called
    assert mock_post.call_count == 1
    assert mock_post.call_args[1]["json"]["method"] == "core.resume_torrents"


def test_set_torrent_trackers(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(
            {
                "result": None,
                "error": None,
                "id": 1,
            },
            ok=True,
            status_code=200,
        ),
    )

    response = client.set_torrent_trackers(
        "mock_torrent_id", [{"tracker1": 1}, {"tracker2": 1}]
    )
    assert response.error is None
    assert response.result is None
    assert mock_post.called
    assert mock_post.call_count == 1
    assert mock_post.call_args[1]["json"]["method"] == "core.set_torrent_trackers"


def test_get_torrents_status_defaults_none(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(
            {
                "result": {},
                "error": None,
                "id": 1,
            },
            ok=True,
            status_code=200,
        ),
    )

    # Call without arguments to trigger the None -> default replacement logic
    response = client.get_torrents_status()

    assert response.error is None
    assert mock_post.called
    assert mock_post.call_count == 1
    assert mock_post.call_args[1]["json"]["method"] == "core.get_torrents_status"
    # Verify defaults were correctly substituted: filter_dict={}, keys=[], diff=False
    assert mock_post.call_args[1]["json"]["params"] == [{}, [], False]


def test_status_methods_with_explicit_filters(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    client, mock_post = client_mock
    mock_post.side_effect = (
        MockResponse({"result": {}, "error": None}, ok=True, status_code=200),
        MockResponse({"result": {}, "error": None}, ok=True, status_code=200),
    )

    client.get_torrent_status("torrent", keys=["name"])
    client.get_torrents_status(
        filter_dict={"state": "Seeding"}, keys=["name"], diff=True
    )

    first_call, second_call = mock_post.call_args_list
    assert first_call.kwargs["json"]["params"] == ["torrent", ["name"], False]
    assert second_call.kwargs["json"]["params"] == [
        {"state": "Seeding"},
        ["name"],
        True,
    ]


def test_get_torrent_status_defaults(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    client, mock_post = client_mock
    mock_post.side_effect = (
        MockResponse({"result": {}, "error": None, "id": 1}, ok=True, status_code=200),
    )
    # Call without optional arguments to trigger defaults (lines 272-274)
    client.get_torrent_status("torrent_id")

    assert mock_post.called
    # Verify defaults were substituted: keys=[], diff=False
    assert mock_post.call_args[1]["json"]["params"] == ["torrent_id", [], False]


def test_get_torrents_status_defaults(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    client, mock_post = client_mock
    mock_post.side_effect = (
        MockResponse({"result": {}, "error": None, "id": 1}, ok=True, status_code=200),
    )
    # Call without optional arguments to trigger defaults (lines 295-297)
    client.get_torrents_status()

    assert mock_post.called
    # Verify defaults were substituted: filter_dict={}, keys=[], diff=False
    assert mock_post.call_args[1]["json"]["params"] == [{}, [], False]
