from enum import Enum


class TorrentState(Enum):
    """
    Deluge torrent states.

    Note: Be sure to cast to string or access the Enum.value.
    """

    ALLOCATING = "Allocating"
    CHECKING = "Checking"
    DOWNLOADING = "Downloading"
    SEEDING = "Seeding"
    PAUSED = "Paused"
    ERROR = "Error"
    QUEUED = "Queued"
    MOVING = "Moving"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def _missing_(cls, value):
        """Override this method to ignore case sensitivity"""
        value = value.lower()
        for member in cls:
            if member.name.lower() == value:
                return member
        raise ValueError(f"No {cls.__name__} member with value '{value}'")
