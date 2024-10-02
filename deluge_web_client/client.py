import base64
import requests
from collections.abc import Iterable
from os import PathLike
from pathlib import Path
from typing import Union

from .exceptions import DelugeWebClientError
from .response import Response


class DelugeWebClient:
    HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}
    LOGIN_RETRIES = 3

    def __init__(self, url: str, password: str) -> None:
        self.session = requests.Session()
        self.url = self._build_url(url)
        self.password = password

    def __enter__(self) -> "DelugeWebClient":
        """Login and connect to client while using with statement."""
        self.login()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """End of with statement."""
        return False

    def login(self, timeout: int = 30) -> Response:
        """
        Log in to Web UI and connects to the first available host, retrying if needed.

        Args:
            timeout (int): Timeout for the login and connection attempts.

        Returns:
            Response: A summary response indicating the success or failure of the login and connection attempts.
        """
        login_response = self._attempt_login(timeout)
        if not login_response.result:
            return Response(result=False, error="Login failed", id=None)

        # check if already connected
        if self.check_connected(timeout).result:
            return Response(result=True, error=None, id=None)

        # attempt to connect to the first available host with retries
        connection_response = self._connect_to_first_host(timeout)
        if not connection_response.get(
            "connected_now", Response(None, None, None)
        ).result:
            return Response(result=False, error="Failed to connect to host", id=None)

        return Response(result=True, error=None, id=None)

    def _attempt_login(self, timeout: int) -> Response:
        """Attempt to log in to the Web UI"""
        login_payload = {"method": "auth.login", "params": [self.password], "id": 1}
        return self.execute_call(login_payload, timeout)

    def _connect_to_first_host(self, timeout: int) -> dict[str, Response]:
        """Connect to the first available host with retry logic"""
        hosts = self.get_hosts()

        if hosts.result:
            for _ in range(self.LOGIN_RETRIES):
                host_id = hosts.result[0][0]
                connect_response = self.connect_to_host(host_id)

                if connect_response.result:
                    return {"connected_now": self.check_connected(timeout)}

        return {
            "connected_now": Response(
                result=False, error="All attempts failed", id=None
            )
        }

    def disconnect(self, timeout: int = 30) -> Response:
        """
        Disconnects from the Web UI.
        Note: This disconnects from all of your logged in instances outside of this program as well
        that is tied to that user/password. Only use this IF needed not on each call.
        """
        payload = {"method": "web.disconnect", "params": [], "id": 1}
        return self.execute_call(payload, timeout)

    def upload_torrent(
        self,
        torrent_path: Union[PathLike[str], Path],
        save_directory: str = None,
        label: str = None,
        timeout: int = 30,
    ) -> Response:
        """
        Opens the torrent path building out the payload as needed to
        upload a single torrent to the client.

        Args:
            torrent_path (PathLike[str], Path): Path to torrent file (example.torrent).
            save_directory (str, optional): Defined path where the file should go on the host. Defaults to None.
            label (str, optional): Label to apply to uploaded torrent. Defaults to None.
            timeout (int): Time to timeout.

        Returns:
            Response: Response object.
        """
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
            return self._upload_helper(payload, label, timeout)

    def upload_torrents(
        self,
        torrents: Iterable[Union[PathLike[str], Path]],
        save_directory: str = None,
        label: str = None,
        timeout: int = 30,
    ) -> dict[str, Response]:
        """
        Uploads multiple torrents.

        Args:
            torrents (Iterable[Union[PathLike[str], Path]]): A list or other iterable of torrent file paths.
            save_directory (str, optional): Defined path where the file should go on the host. Defaults to None.
            label (str, optional): Label to apply to uploaded torrents. Defaults to None.
            timeout (int): Time to timeout.

        Returns:
            dict[str, Response]: A dictionary of torrent name and Response objects for each torrent.
        """
        results = {}
        for torrent_path in torrents:
            torrent_path = Path(torrent_path)
            try:
                response = self.upload_torrent(
                    torrent_path, save_directory, label, timeout
                )
                results[torrent_path.stem] = response
            except Exception as e:
                raise DelugeWebClientError(
                    f"Failed to upload {torrent_path.name}:\n{e}"
                )

        return results

    def add_torrent_magnet(
        self, uri: str, save_directory: str = None, label: str = None, timeout: int = 30
    ):
        """Adds a torrent from a magnet link.

        Args:
            uri (str): Magnet input
            save_directory (str, optional): Defined path where the file should go on the host. Defaults to None.
            label (str, optional): Label to apply to uploaded torrent. Defaults to None.
            timeout (int): Time to timeout.

        Returns:
            Response: Response object.
        """
        args = {"add_paused": True, "seed_mode": False, "auto_managed": True}
        if save_directory:
            args["download_location"] = str(save_directory)
        payload = {
            "method": "core.add_torrent_magnet",
            "params": [str(uri), args],
            "id": 1,
        }
        return self._upload_helper(payload, label, timeout)

    def _upload_helper(self, payload: dict, label: str, timeout: int) -> Response:
        with self.session.post(
            self.url, headers=self.HEADERS, json=payload, timeout=timeout
        ) as response:
            if response.ok:
                result = response.json()
                info_hash = str(result["result"])
                if label:
                    self._apply_label(info_hash, str(label), timeout)
                self._start_torrent(info_hash, timeout)
                return Response(result=True, error=None, id=1)
            else:
                response.raise_for_status()

    def _apply_label(
        self, info_hash: str, label: str, timeout: int
    ) -> tuple[bool, bool]:
        """
        Used internally to add and apply labels as needed for
        the `upload_torrent` method

        Args:
            info_hash (str): Info has of torrent.
            label (str): Label to apply it to (automatically set to lowercase internally).
            timeout (int): Time to timeout.

        Returns:
            tuple (bool, bool): add_label(), set_label().
        """
        add_label = self.add_label(label, timeout)
        set_label = self.set_label(info_hash, label, timeout)
        return add_label, set_label

    def _start_torrent(self, info_hash: str, timeout: int = 30) -> Response:
        """Helper method to start the torrent after it's been uploaded"""
        payload = {"method": "core.resume_torrent", "params": [info_hash], "id": 1}
        return self.execute_call(payload, timeout)

    def get_labels(self, timeout: int = 30) -> Response:
        """Gets defined labels"""
        payload = {"method": "label.get_labels", "params": [], "id": 1}
        return self.execute_call(payload, timeout)

    def set_label(self, info_hash: str, label: str, timeout: int = 30) -> Response:
        """Sets the label for a specific torrent"""
        payload = {
            "method": "label.set_torrent",
            "params": [info_hash, label.lower()],
            "id": 1,
        }
        return self.execute_call(payload, timeout)

    def add_label(self, label: str, timeout: int = 30) -> Response:
        """Adds a label to the client, ignoring labels if they already exist"""
        payload = {
            "method": "label.add",
            "params": [label.lower()],
            "id": 1,
        }
        response = self.execute_call(payload, handle_error=False, timeout=timeout)
        if response.error != None:
            if "Label already exists" not in response.error.get("message"):
                raise DelugeWebClientError(f"Error adding label:\n{response.error}")
        return response

    def get_plugins(self, timeout: int = 30) -> Response:
        """Gets plugins"""
        payload = {"method": "web.get_plugins", "params": [], "id": 1}
        return self.execute_call(payload, timeout)

    def get_torrent_files(self, torrent_id: str, timeout: int = 30) -> Response:
        """Gets the files for a torrent in tree format"""
        payload = {"method": "web.get_torrent_files", "params": [torrent_id], "id": 1}
        return self.execute_call(payload, timeout)

    def check_connected(self, timeout: int = 30) -> Response:
        """
        Use the `web.connected` method to get a boolean response if the Web UI is
        connected to a deluged host
        """
        payload = {"method": "web.connected", "params": [], "id": 1}
        return self.execute_call(payload, timeout)

    def get_hosts(self, timeout: int = 30) -> Response:
        """Returns hosts we're connected to currently"""
        payload = {"method": "web.get_hosts", "params": [], "id": 1}
        return self.execute_call(payload, timeout)

    def get_host_status(self, host_id: str, timeout: int = 30) -> Response:
        """Get the deluged host status `<hostID>`"""
        payload = {"method": "web.get_host_status", "params": [host_id], "id": 1}
        return self.execute_call(payload, timeout)

    def connect_to_host(self, host_id: str, timeout: int = 30) -> Response:
        """To connect to deluged with `<hostID>`"""
        payload = {"method": "web.connect", "params": [host_id], "id": 1}
        return self.execute_call(payload, timeout)

    def test_listen_port(self, timeout: int = 30) -> bool:
        """Checks if the active port is open

        Returns:
            bool: If active port is opened or closed
        """
        payload = {"method": "core.test_listen_port", "params": [], "id": 1}
        return self.execute_call(payload, timeout).result

    def execute_call(
        self, payload: dict, handle_error: bool = True, timeout: int = 30
    ) -> Response:
        """
        Helper method to execute most calls to the Web UI as needed.

        Args:
            payload (dict): Payload object to be called.
            handle_error (bool, optional): Handle errors here or allow the caller to handle
                the error. Defaults to True.
            timeout (int): Time to timeout.

        Returns:
            Response: Response object for each call.
        """
        with self.session.post(
            self.url, headers=self.HEADERS, json=payload, timeout=timeout
        ) as response:
            if response.ok:
                response_json = response.json()
                data = Response(
                    result=response_json.get("result"),
                    error=self._normalize_exception(response_json.get("error")),
                    id=response_json.get("id"),
                )
                if handle_error and data.error:
                    raise DelugeWebClientError(
                        f"Payload: {payload}, Error: {data.error}"
                    )
                return data
            else:
                raise DelugeWebClientError(
                    f"Failed to execute call. Response code: {response.status_code}. Reason: {response.reason}"
                )

    @staticmethod
    def _normalize_exception(exc_str: any) -> Union[str, None]:
        """
        Removes the un-needed ending square bracket and stripping extra white
        space if input is a string
        """
        if exc_str:
            if isinstance(exc_str, str):
                return exc_str.rstrip("]").strip()
            else:
                return exc_str

    @staticmethod
    def _build_url(url: str) -> str:
        """Automatically fixes urls as needed to access the json api endpoint"""
        if not url.endswith("/"):
            url += "/"

        if "json" not in url:
            url += "json/"

        return url.rstrip("/")
