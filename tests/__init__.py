from typing import Optional


class MockResponse:
    """Mock to simulate a requests.Response object"""

    def __init__(
        self,
        json_data: Optional[dict] = {},
        ok: Optional[bool] = None,
        status_code: Optional[int] = None,
        reason: Optional[str] = None,
    ):
        self.json_data = json_data
        self.ok = ok
        self.status_code = status_code
        self.reason = reason

    def json(self):
        return self.json_data

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


example_status_dict = {
    "active_time": 59828,
    "seeding_time": 59800,
    "finished_time": 59800,
    "all_time_download": 0,
    "storage_mode": "sparse",
    "distributed_copies": 0.0,
    "download_payload_rate": 0,
    "file_priorities": [1],
    "hash": "mocked_hash",
    "auto_managed": True,
    "is_auto_managed": True,
    "is_finished": True,
    "max_connections": -1,
    "max_download_speed": -1,
    "max_upload_slots": -1,
    "max_upload_speed": -1,
    "message": "OK",
    "move_on_completed_path": "/downloads",
    "move_on_completed": False,
    "move_completed_path": "/downloads",
    "move_completed": False,
    "next_announce": 3430,
    "num_peers": 0,
    "num_seeds": 0,
    "owner": "mocked_user",
    "paused": False,
    "prioritize_first_last": False,
    "prioritize_first_last_pieces": False,
    "sequential_download": False,
    "progress": 100.0,
    "shared": False,
    "remove_at_ratio": False,
    "save_path": "/downloads",
    "download_location": "/downloads",
    "seeds_peers_ratio": 1.0,
    "seed_rank": 536870912,
    "state": "Seeding",
    "stop_at_ratio": False,
    "stop_ratio": 2.0,
    "time_added": 1728254444,
    "total_done": 3515992406,
    "total_payload_download": 0,
    "total_payload_upload": 0,
    "total_peers": -1,
    "total_seeds": -1,
    "total_uploaded": 0,
    "total_wanted": 3515992406,
    "total_remaining": 0,
    "tracker": "",
    "tracker_host": "mocked.me",
    "trackers": [
        {
            "url": "http://mocked/announce",
            "trackerid": "",
            "tier": 0,
            "fail_limit": 0,
            "source": 1,
            "verified": False,
            "message": "",
            "last_error": {"value": 0, "category": ""},
            "next_announce": None,
            "min_announce": None,
            "scrape_incomplete": 0,
            "scrape_complete": 0,
            "scrape_downloaded": 0,
            "fails": 0,
            "updating": False,
            "start_sent": False,
            "complete_sent": False,
            "endpoints": [],
            "send_stats": False,
        }
    ],
    "tracker_status": "Error: skipping tracker announce (unreachable)",
    "upload_payload_rate": 0,
    "comment": "",
    "creator": "",
    "num_files": 1,
    "num_pieces": 839,
    "piece_length": 4194304,
    "private": True,
    "total_size": 3515992406,
    "eta": 0,
    "file_progress": [1.0],
    "files": [
        {
            "index": 0,
            "path": "Random.Movie.2006.BluRay.720p-BHDStudio.mp4",
            "size": 3515992406,
            "offset": 0,
        }
    ],
    "orig_files": [
        {
            "index": 0,
            "path": "Random.Movie.2006.BluRay.720p-BHDStudio.mp4",
            "size": 3515992406,
            "offset": 0,
        }
    ],
    "is_seed": True,
    "peers": [],
    "queue": -1,
    "ratio": 0.0,
    "completed_time": 1728254472,
    "last_seen_complete": 0,
    "name": "Random.Movie.2006.BluRay.720p-BHDStudio.mp4",
    "pieces": None,
    "seed_mode": False,
    "super_seeding": False,
    "time_since_download": -1,
    "time_since_upload": -1,
    "time_since_transfer": -1,
    "label": "media",
}

example_multi_status_dict = {
    "info_hash1": example_status_dict,
    "info_hash2": example_status_dict,
}
