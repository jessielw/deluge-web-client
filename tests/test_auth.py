from __future__ import annotations

from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest

from deluge_web_client import DelugeWebClientError, Response
from deluge_web_client.client import DelugeWebClient
from tests import MockResponse


def test_failure_to_connect(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(ok=False, status_code=404, reason="Not Found"),
    )

    with pytest.raises(
        DelugeWebClientError,
        match="HTTP Error - Status: 404, Reason: Not Found",
    ):
        client.login()


def test_successful_login_and_host_connection(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    client, _ = client_mock

    # Mock execute_call for login
    with (
        patch.object(
            DelugeWebClient,
            "_attempt_login",
            return_value=Response(result=True, error=None),
        ) as mock_attempt_login,
        patch.object(
            DelugeWebClient,
            "check_connected",
            side_effect=[
                # Not connected yet
                Response(result=False, error=None),
                # Connected after host connection
                Response(result=True, error=None),
            ],
        ) as mock_check_connected,
        patch.object(
            DelugeWebClient,
            "get_hosts",
            return_value=Response(result=[["host_id_1"]], error=None),
        ) as mock_get_hosts,
        patch.object(
            DelugeWebClient,
            "connect_to_host",
            return_value=Response(result=True, error=None),
        ) as mock_connect_to_host,
    ):
        # Call the login method
        response = client.login()

        # Verify the response
        assert response.result is True
        assert response.error is None

        # Verify method calls
        # Login should be called once
        mock_attempt_login.assert_called_once()
        # Check connection should be called twice
        mock_check_connected.assert_called()
        # Host retrieval should be called once
        mock_get_hosts.assert_called_once_with(30)
        # Connect to the correct host
        mock_connect_to_host.assert_called_once_with("host_id_1", 30)

        # Verify login, connection check, host lookup, and host connection flow.
        assert mock_check_connected.call_count == 2


def test_login_failure(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, _ = client_mock

    # Mock the login attempt to return a failure response
    with patch.object(
        DelugeWebClient,
        "_attempt_login",
        return_value=Response(result=False, error=None),
    ) as mock_attempt_login:
        # Call the login method
        response = client.login()

        # Verify the response
        assert response.result is False
        assert response.error == "Login failed"

        # Verify that _attempt_login was called once
        mock_attempt_login.assert_called_once()


def test_already_connected(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, _ = client_mock

    # Mock login success and already connected response
    with (
        patch.object(
            DelugeWebClient,
            "_attempt_login",
            return_value=Response(result=True, error=None),
        ) as mock_attempt_login,
        patch.object(
            DelugeWebClient,
            "check_connected",
            return_value=Response(result=True, error=None),
        ) as mock_check_connected,
    ):
        # Call the login method
        response = client.login()

        # Verify the response
        assert response.result is True
        assert response.error is None

        # Verify method calls
        # Login should be called once
        mock_attempt_login.assert_called_once()
        # Check connection should be called once
        mock_check_connected.assert_called_once()


def test_host_connection_failure(
    client_mock: tuple[DelugeWebClient, MagicMock],
) -> None:
    client, _ = client_mock

    # Mock the login success
    with (
        patch.object(
            DelugeWebClient,
            "_attempt_login",
            return_value=Response(result=True, error=None),
        ) as mock_attempt_login,
        patch.object(
            DelugeWebClient,
            "check_connected",
            return_value=Response(result=False, error=None),
        ) as mock_check_connected,
        patch.object(
            DelugeWebClient,
            "get_hosts",
            return_value=Response(result=[["host_id_1"]], error=None),
        ) as mock_get_hosts,
        patch.object(
            DelugeWebClient,
            "connect_to_host",
            return_value=Response(result=False, error=None),
        ) as mock_connect_to_host,
    ):
        # Call the login method
        response = client.login()

        # Verify the response
        assert response.result is False
        assert response.error == "Failed to connect to host"

        # Verify method calls
        mock_attempt_login.assert_called_once()  # Login should be called once
        mock_check_connected.assert_called_once()
        mock_get_hosts.assert_called_once_with(30)
        mock_connect_to_host.assert_called_once_with("host_id_1", 30)


@pytest.mark.parametrize("hosts", ["invalid", [[]], [[123]]])
def test_login_rejects_malformed_host_entries(
    client_mock: tuple[DelugeWebClient, MagicMock],
    hosts: object,
) -> None:
    client, _ = client_mock
    with (
        patch.object(
            DelugeWebClient,
            "_attempt_login",
            return_value=Response(result=True),
        ),
        patch.object(
            DelugeWebClient,
            "check_connected",
            return_value=Response(result=False),
        ),
        patch.object(
            DelugeWebClient,
            "get_hosts",
            return_value=Response(result=cast(Any, hosts)),
        ),
    ):
        response = client.login(timeout=12)

    assert response == Response(result=False, error="Failed to connect to host")


def test_close_session(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, _ = client_mock

    client.close_session()


def test_disconnect(client_mock: tuple[DelugeWebClient, MagicMock]) -> None:
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(
            {"result": "Connection was closed cleanly.", "error": None, "id": 0},
            True,
            200,
        ),
    )

    response = client.disconnect()

    assert response == Response(result="Connection was closed cleanly.", error=None)
