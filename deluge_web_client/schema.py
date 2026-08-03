from __future__ import annotations

from typing import Any, NamedTuple


class Response(NamedTuple):
    """Object that is filled on each request."""

    result: bool | int | float | str | list[Any] | dict[str, Any] | None = None
    error: str | dict[str, Any] | None = None
    message: str | None = None


class TorrentOptions(NamedTuple):
    """Options for adding a torrent.

    Each attribute maps to the options accepted by Deluge when adding a
    torrent. All fields are optional; unset fields will use server-side
    defaults.

    add_paused:
        If True, add the torrent in a paused state. Default is False.

    auto_managed:
        If True, the torrent will be managed automatically by the client's
        queueing/automanager. When False, the torrent won't be auto-managed.

    download_location:
        Absolute path on the host where the torrent's data should be stored.

    file_priorities:
        Integer or per-file list describing priorities when adding a multi-file
        torrent; leave None to use defaults.

    max_connections:
        Maximum number of peer connections allowed for this torrent (None to
        inherit global/default setting).

    max_download_speed:
        Per-torrent download speed limit in KiB/s. None means unlimited or
        use the global setting.

    max_upload_slots:
        Maximum number of upload slots for this torrent (None to use global
        defaults).

    max_upload_speed:
        Per-torrent upload speed limit in KiB/s. None means unlimited or
        use the global setting.

    move_completed:
        If True, move completed torrents to `move_completed_path` after
        they finish. Defaults to False.

    move_completed_path:
        Destination path to move completed torrents to when `move_completed`
        is True.

    name:
        Suggested name for the torrent (may be used by some CSV/import flows
        or when metadata lacks a name).

    owner:
        Username/owner string to associate with the torrent (implementation
        specific; often unused in simple setups).

    prioritize_first_last_pieces:
        If True, prioritize the first and last pieces of files. Useful for
        streaming playback of media files.

    remove_at_ratio:
        If True, remove the torrent when it reaches `stop_ratio` (requires
        `stop_at_ratio` to be set to True).

    seed_mode:
        If True, enable seed mode where the client assumes data is already
        present and avoids re-checking; useful when adding a torrent whose
        data already exists on disk.

    sequential_download:
        If True, request pieces sequentially (often used for streaming). Use
        with caution as it reduces swarming efficiency.

    shared:
        If True, mark the torrent as shared (affects how it is displayed or
        managed in some frontends/plugins).

    stop_at_ratio:
        If True, stop the torrent once it reaches `stop_ratio`.

    stop_ratio:
        Floating-point ratio at which the torrent should be stopped/removed
        (combined with `stop_at_ratio` / `remove_at_ratio`).

    super_seeding:
        If True, enable super-seeding mode (server will use super-seed
        algorithm where supported). Typically useful when initially seeding
        scarce content.

    label:
        Label or category to assign to the torrent for organizational purposes.
    """

    add_paused: bool | None = None
    auto_managed: bool | None = None
    download_location: str | None = None
    file_priorities: int | list[int] | None = None
    max_connections: int | None = None
    max_download_speed: float | None = None
    max_upload_slots: int | None = None
    max_upload_speed: float | None = None
    move_completed: bool | None = None
    move_completed_path: str | None = None
    name: str | None = None
    owner: str | None = None
    prioritize_first_last_pieces: bool | None = None
    remove_at_ratio: bool | None = None
    seed_mode: bool | None = None
    sequential_download: bool | None = None
    shared: bool | None = None
    stop_at_ratio: bool | None = None
    stop_ratio: float | None = None
    super_seeding: bool | None = None
    label: str | None = None

    def to_dict(self) -> dict[str, bool | int | float | str | list[int]]:
        """Convert the TorrentOptions to a dictionary, excluding None values."""
        return {
            field: getattr(self, field)
            for field in self._fields
            if getattr(self, field) is not None
        }
