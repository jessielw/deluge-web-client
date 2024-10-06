import pytest
from unittest.mock import patch
from deluge_web_client import DelugeWebClient


@pytest.fixture
def client_mock():
    """Fixture to initialize DelugeWebClient and mock its session."""
    with patch("requests.Session.post") as mock_post:
        client = DelugeWebClient(
            url="http://mocked-deluge-url", password="mocked_password"
        )
        yield client, mock_post
