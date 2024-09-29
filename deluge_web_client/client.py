import base64
import requests
from os import PathLike
from pathlib import Path

from .exceptions import DelugeWebClientError


# TODO: timeout
# TODO: check custom raised error message for each method
# TODO: add other useful rpc methods https://deluge.readthedocs.io/en/deluge-2.0.1/reference/api.html


class DelugeWebClient:
    HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

    def __init__(self, url: str, password: str) -> None:
        self.session = requests.Session()

        self.url = self._build_url(url)
        self.password = password

    def login(self):
        payload = {"method": "auth.login", "params": [self.password], "id": 1}
        response = self.session.post(self.url, headers=self.HEADERS, json=payload)
        if response.ok:
            result = response.json()
            # print(result)
            if result.get("result") == True:
                return True
            else:
                raise DelugeWebClientError(f"Failed to login to client: {result}")
        else:
            response.raise_for_status()

    def logout(self) -> tuple[bool, str]:
        payload = {"method": "web.disconnect", "params": [], "id": 1}
        response = self.session.post(self.url, headers=self.HEADERS, json=payload)
        if response.ok:
            result = response.json()
            if result.get("result") == "Connection was closed cleanly.":
                return True, "Connection was closed cleanly"
            else:
                return False, "Failed to logout of client"
        else:
            response.raise_for_status()

    def upload_torrent(
        self,
        torrent_path: PathLike[str] | Path,
        save_directory: str = None,
        label: str = None,
    ) -> tuple[bool, str]:
        torrent_path = Path(torrent_path)

        with open(torrent_path, "rb") as tf:
            args = {"add_paused": True, "seed_mode": True, "auto_managed": True}
            if save_directory:
                args["download_location"] = str(save_directory)
            params = [
                str(torrent_path),
                str(base64.b64encode(tf.read()), encoding="utf-8"),
                args,
            ]

            payload = {"method": "core.add_torrent_file", "params": params, "id": 1}

            response = self.session.post(self.url, headers=self.HEADERS, json=payload)
            if response.ok:
                result = response.json()
                info_hash = str(result["result"])
                if label:
                    self._apply_label(info_hash, str(label))
                self._start_torrent(info_hash)
                return True, "Torrent injected and started"
            else:
                response.raise_for_status()

    def _apply_label(self, info_hash: str, label: str):
        label = label.lower()
        payload1 = {"method": "label.add", "params": [label], "id": 1}
        create_label = self.session.post(self.url, headers=self.HEADERS, json=payload1)
        if not create_label.ok or create_label.json()["error"] != None:
            # TODO: throw an error!
            pass
        print(create_label.json())

        payload2 = {
            "method": "label.set_torrent",
            "params": [info_hash, label],
            "id": 1,
        }
        set_label = self.session.post(self.url, headers=self.HEADERS, json=payload2)
        if not set_label.ok or set_label.json()["error"] != None:
            # TODO: throw error
            pass
        print(set_label.json())

    def _start_torrent(self, info_hash: str) -> None:
        payload = {"method": "core.resume_torrent", "params": [info_hash], "id": 1}
        response = self.session.post(self.url, headers=self.HEADERS, json=payload)
        if not response.ok or response.json()["error"] != None:
            # TODO: throw error
            pass

    # TODO:
    # def add_torrents(self, torrents: list[PathLike[str]]):

    def check_connected(self) -> tuple[bool, str]:
        payload = {"method": "web.connected", "params": [], "id": 1}
        response = self.session.post(self.url, headers=self.HEADERS, json=payload)
        if response.ok:
            result = response.json()
            if result.get("result") == True:
                return True, "Connected"
            else:
                return False, "Not connected"
        else:
            response.raise_for_status()

    def get_hosts(self) -> list[list[str]]:
        payload = {"method": "web.get_hosts", "params": [], "id": 1}
        response = self.session.post(self.url, headers=self.HEADERS, json=payload)
        if response.ok:
            result = response.json()
            if result.get("result"):
                return result.get("result")
            else:
                return []
        else:
            response.raise_for_status()

    def get_host_status(self, host_id: str) -> list[str]:
        payload = {"method": "web.get_host_status", "params": [host_id], "id": 1}
        response = self.session.post(self.url, headers=self.HEADERS, json=payload)
        if response.ok:
            result = response.json()
            if result.get("result"):
                return result.get("result")
            else:
                return []
        else:
            response.raise_for_status()

    def connect_to_host(self, host_id: str) -> list[str]:
        payload = {"method": "web.connect", "params": [host_id], "id": 1}
        response = self.session.post(self.url, headers=self.HEADERS, json=payload)
        if response.ok:
            result = response.json()
            if result.get("result"):
                return result.get("result")
            else:
                return []
        else:
            response.raise_for_status()

    @staticmethod
    def _build_url(url: str) -> str:
        """Automatically fixes urls as needed to access the json api endpoint"""
        if not url.endswith("/"):
            url += "/"

        if "json" not in url:
            url += "json/"

        return url.rstrip("/")
