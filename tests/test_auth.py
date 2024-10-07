import pytest
from tests import MockResponse
from unittest.mock import MagicMock
from deluge_web_client import DelugeWebClientError, Response


def test_failure_to_connect(client_mock):
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(ok=False, status_code=404, reason="Not Found"),
    )

    with pytest.raises(
        DelugeWebClientError,
        match="Failed to execute call. Response code: 404. Reason: Not Found",
    ):
        client.login()


def test_successful_login_and_host_connection(client_mock):
    client, _ = client_mock

    # Mock execute_call for login
    client._attempt_login = MagicMock(
        return_value=Response(result=True, error=None, id=None)
    )

    # Mock check_connected to simulate not being connected initially, and then connected after host connection
    client.check_connected = MagicMock(
        side_effect=[
            # Not connected yet
            Response(result=False, error=None, id=None),
            # Connected after host connection
            Response(result=True, error=None, id=None),
        ]
    )

    # Mock get_hosts to return a list of hosts
    client.get_hosts = MagicMock(
        return_value=Response(result=[["host_id_1"]], error=None, id=None)
    )

    # Mock connect_to_host to simulate successful host connection
    client.connect_to_host = MagicMock(
        return_value=Response(result=True, error=None, id=None)
    )

    # Call the login method
    response = client.login()

    # Verify the response
    assert response.result is True
    assert response.error is None

    # Verify method calls
    # Login should be called once
    client._attempt_login.assert_called_once()
    # Check connection should be called twice
    client.check_connected.assert_called()
    # Host retrieval should be called once
    client.get_hosts.assert_called_once()
    # Connect to the correct host
    client.connect_to_host.assert_called_once_with("host_id_1")

    # Verify the flow of calls (login, check if connected, get hosts, connect to host)
    assert client.check_connected.call_count == 2


def test_login_failure(client_mock):
    client, mock_post = client_mock

    # Mock the login attempt to return a failure response
    client._attempt_login = MagicMock(
        return_value=Response(result=False, error=None, id=None)
    )

    # Call the login method
    response = client.login()

    # Verify the response
    assert response.result is False
    assert response.error == "Login failed"

    # Verify that _attempt_login was called once
    client._attempt_login.assert_called_once()


def test_already_connected(client_mock):
    client, mock_post = client_mock

    # Mock login success and already connected response
    client._attempt_login = MagicMock(
        return_value=Response(result=True, error=None, id=None)
    )
    client.check_connected = MagicMock(
        return_value=Response(result=True, error=None, id=None)
    )

    # Call the login method
    response = client.login()

    # Verify the response
    assert response.result is True
    assert response.error is None

    # Verify method calls
    # Login should be called once
    client._attempt_login.assert_called_once()
    # Check connection should be called once
    client.check_connected.assert_called_once()


def test_host_connection_failure(client_mock):
    client, mock_post = client_mock

    # Mock the login success
    client._attempt_login = MagicMock(
        return_value=Response(result=True, error=None, id=None)
    )

    # Mock check_connected to simulate not being connected initially
    client.check_connected = MagicMock(
        return_value=Response(result=False, error=None, id=None)
    )

    # Mock get_hosts to return a list of hosts
    client.get_hosts = MagicMock(
        return_value=Response(result=[["host_id_1"]], error=None, id=None)
    )

    # Mock connect_to_host to simulate host connection failure
    client.connect_to_host = MagicMock(
        return_value=Response(result=False, error=None, id=None)
    )

    # Call the login method
    response = client.login()

    # Verify the response
    assert response.result is False
    assert response.error == "Failed to connect to host"

    # Verify method calls
    client._attempt_login.assert_called_once()  # Login should be called once
    client.check_connected.assert_called_once()  # Check connection should be called once
    client.get_hosts.assert_called_once()  # Get hosts should be called once
    client.connect_to_host.assert_called_once_with(
        "host_id_1"
    )  # Connect to the first host


def test_close_session(client_mock):
    client, _ = client_mock

    response = client.close_session()

    assert response is None


def test_disconnect(client_mock):
    client, mock_post = client_mock

    mock_post.side_effect = (
        MockResponse(
            {"result": "Connection was closed cleanly.", "error": None, "id": 0},
            True,
            200,
        ),
    )

    response = client.disconnect()

    assert response == Response(
        result="Connection was closed cleanly.", error=None, id=0
    )
