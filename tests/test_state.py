from __future__ import annotations

import pytest

from deluge_web_client import TorrentState


def test_torrent_state_members() -> None:
    """Test that the enum members are correctly instantiated."""
    assert TorrentState.ALLOCATING.value == "Allocating"
    assert TorrentState.CHECKING.value == "Checking"
    assert TorrentState.DOWNLOADING.value == "Downloading"
    assert TorrentState.SEEDING.value == "Seeding"
    assert TorrentState.PAUSED.value == "Paused"
    assert TorrentState.ERROR.value == "Error"
    assert TorrentState.QUEUED.value == "Queued"
    assert TorrentState.MOVING.value == "Moving"


def test_torrent_state_str_method() -> None:
    """Test the __str__ method returns the correct string value."""
    assert str(TorrentState.ALLOCATING) == "Allocating"
    assert str(TorrentState.CHECKING) == "Checking"
    assert str(TorrentState.DOWNLOADING) == "Downloading"


def test_torrent_state_case_insensitive_lookup() -> None:
    """Test case-insensitive enum lookup."""
    assert TorrentState("allocating") == TorrentState.ALLOCATING
    assert TorrentState("CHECKING") == TorrentState.CHECKING
    assert TorrentState("downloading") == TorrentState.DOWNLOADING


def test_torrent_state_invalid_value() -> None:
    """Test that the _missing_ method raises ValueError for invalid values."""
    with pytest.raises(ValueError) as exc_info:
        TorrentState("invalid_state")
    assert str(exc_info.value) == "No TorrentState member with value 'invalid_state'"
