import base64
import requests
from collections.abc import Iterable
from os import PathLike
from pathlib import Path
from typing import Union, Optional, Any

from deluge_web_client.exceptions import DelugeWebClientError
from deluge_web_client.response import Response
from deluge_web_client.types import ParamArgs


class DelugeWebClient:
    HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}
    ID = 0

    def __init__(self, url: str = "", password: str = "") -> None:
        self.session = requests.Session()
        self.url = self._build_url(url)
        self.password = password

    def __enter__(self) -> "DelugeWebClient":
        """Login and connect to client while using with statement."""
        self.login()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """End of with statement, closes the session."""
        self.close_session()

    def login(self, timeout: int = 30) -> Response:
        """
        Log in to Web UI and connect to the first available host.

        Args:
            timeout (int): Timeout for the login and connection attempts.

        Returns:
            Response: A summary response indicating the success or failure of the login and connection attempts.
        """
        login_response = self._attempt_login(timeout)
        if not login_response.result:
            return self._create_failure_response("Login failed")

        # Check if already connected
        if self._is_connected(timeout):
            return Response(result=True, error=None, id=None)

        # Attempt to connect to a host
        return self._connect_to_first_host(timeout)

    def _attempt_login(self, timeout: int) -> Response:
        """Attempt to log in to the Web UI."""
        login_payload = {
            "method": "auth.login",
            "params": [self.password],
            "id": self.ID,
        }
        return self.execute_call(login_payload, timeout=timeout)

    def _is_connected(self, timeout: int) -> bool:
        """Check if already connected to the Web UI."""
        return True if self.check_connected(timeout).result else False

    def _connect_to_first_host(self, timeout: int) -> Response:
        """Attempt to connect to the first available host."""
        hosts = self.get_hosts()

        if isinstance(hosts.result, list) and hosts.result:
            host_info = hosts.result[0]
            if isinstance(host_info, list) and host_info:
                host_id = host_info[0]
                connect_response = self.connect_to_host(host_id)
                if connect_response.result:
                    return self.check_connected(timeout)

        return self._create_failure_response("Failed to connect to host")

    def _create_failure_response(self, error_message: str) -> Response:
        """Helper method to create a failure response."""
        return Response(result=False, error=error_message, id=None)

    def close_session(self) -> None:
        """
        Closes the `DelugeWebClient` session.
        This is handled automatically
        when `DelugeWebClient` is used in a context manager.
        """
        self.session.close()

    def disconnect(self, timeout: int = 30) -> Response:
        """
        Disconnects from the Web UI.
        Note: This disconnects from all of your logged in instances outside of this program as well
        that is tied to that user/password. Only use this IF needed not on each call.
        """
        payload = {
            "method": "web.disconnect",
            "params": [],
            "id": self.ID,
        }
        return self.execute_call(payload, timeout=timeout)

    def upload_torrent(
        self,
        torrent_path: Union[PathLike[str], str, Path],
        add_paused: bool = False,
        seed_mode: bool = False,
        auto_managed: bool = False,
        save_directory: Optional[str] = None,
        label: Optional[str] = None,
        timeout: int = 30,
    ) -> Response:
        """
        Opens the torrent path building out the payload as needed to
        upload a single torrent to the client.

        Args:
            torrent_path (PathLike[str], str, Path): Path to torrent file (example.torrent).
            add_paused (bool): indicates whether torrent should be added paused. Default to False.
            seed_mode (bool): whether to skip rechecking when adding. Default to recheck (False).
            auto_managed (bool): sets an added torrents to be auto-managed by user settings. Defaults to False.
            save_directory (str, optional): Defined path where the file should go on the host. Defaults to None.
            label (str, optional): Label to apply to uploaded torrent. Defaults to None.
            timeout (int): Time to timeout.

        Returns:
            Response: Response object.
        """
        torrent_path = Path(torrent_path)
        with open(torrent_path, "rb") as tf:
            args = ParamArgs(
                add_paused=add_paused,
                seed_mode=seed_mode,
                auto_managed=auto_managed,
                download_location=None,
            )
            if save_directory:
                args["download_location"] = str(save_directory)
            params = [
                str(torrent_path),
                str(base64.b64encode(tf.read()), encoding="utf-8"),
                args,
            ]
            payload = {
                "method": "core.add_torrent_file",
                "params": params,
                "id": self.ID,
            }
            return self._upload_helper(payload, label, timeout)

    def upload_torrents(
        self,
        torrents: Iterable[Union[PathLike[str], str, Path]],
        save_directory: Optional[str] = None,
        label: Optional[str] = None,
        timeout: int = 30,
    ) -> dict[str, Response]:
        """
        Uploads multiple torrents.

        Args:
            torrents (Iterable[Union[PathLike[str], str, Path]]): A list or other iterable of torrent file paths.
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
                    torrent_path,
                    save_directory=save_directory,
                    label=label,
                    timeout=timeout,
                )
                results[torrent_path.stem] = response
            except Exception as e:
                raise DelugeWebClientError(
                    f"Failed to upload {torrent_path.name}:\n{e}"
                )

        return results

    def add_torrent_magnet(
        self,
        uri: str,
        add_paused: bool = False,
        seed_mode: bool = False,
        auto_managed: bool = False,
        save_directory: Optional[str] = None,
        label: Optional[str] = None,
        timeout: int = 30,
    ):
        """Adds a torrent from a magnet link.

        Args:
            uri (str): Magnet input
            add_paused (bool): indicates whether torrent should be added paused. Default to False.
            seed_mode (bool): whether to skip rechecking when adding. Default to recheck (False).
            auto_managed (bool): sets an added torrents to be auto-managed by user settings. Defaults to False.
            save_directory (str, optional): Defined path where the file should go on the host. Defaults to None.
            label (str, optional): Label to apply to uploaded torrent. Defaults to None.
            timeout (int): Time to timeout.

        Returns:
            Response: Response object.

        """
        args = ParamArgs(
            add_paused=add_paused,
            seed_mode=seed_mode,
            auto_managed=auto_managed,
            download_location=None,
        )
        if save_directory:
            args["download_location"] = str(save_directory)
        payload = {
            "method": "core.add_torrent_magnet",
            "params": [str(uri), args],
            "id": self.ID,
        }
        return self._upload_helper(payload, label, timeout)

    def add_torrent_url(
        self,
        url: str,
        add_paused: bool = False,
        seed_mode: bool = False,
        auto_managed: bool = False,
        save_directory: Optional[str] = None,
        label: Optional[str] = None,
        timeout: int = 30,
    ):
        """Adds a torrent from a URL.

        Args:
            url (str): URL input
            add_paused (bool): indicates whether torrent should be added paused. Default to False.
            seed_mode (bool): whether to skip rechecking when adding. Default to recheck (False).
            auto_managed (bool): sets an added torrents to be auto-managed by user settings. Defaults to False.
            save_directory (str, optional): Defined path where the file should go on the host. Defaults to None.
            label (str, optional): Label to apply to uploaded torrent. Defaults to None.
            timeout (int): Time to timeout.

        Returns:
            Response: Response object.
        """
        args = ParamArgs(
            add_paused=add_paused,
            seed_mode=seed_mode,
            auto_managed=auto_managed,
            download_location=None,
        )
        if save_directory:
            args["download_location"] = str(save_directory)
        payload = {
            "method": "core.add_torrent_url",
            "params": [str(url), args],
            "id": self.ID,
        }
        return self._upload_helper(payload, label, timeout)

    def _upload_helper(
        self, payload: dict, label: Optional[str], timeout: int
    ) -> Response:
        with self.session.post(
            self.url, headers=self.HEADERS, json=payload, timeout=timeout
        ) as response:
            self.ID += 1
            if response.ok:
                result = response.json()
                info_hash = str(result["result"])
                if label:
                    self._apply_label(info_hash, str(label), timeout)
                self.resume_torrent(info_hash, timeout)
                return Response(result=info_hash, error=None, id=1)
            else:
                raise DelugeWebClientError(
                    f"Failed to upload file. Status code: {response.status_code}, Reason: {response.reason}"
                )

    def _apply_label(
        self, info_hash: str, label: str, timeout: int
    ) -> tuple[Response, Response]:
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

    def get_free_space(
        self, path: Optional[Union[str, PathLike[str]]] = None, timeout: int = 30
    ) -> Response:
        """Gets free space"""
        payload = {
            "method": "core.get_free_space",
            "params": [str(path)] if path else [],
            "id": self.ID,
        }
        return self.execute_call(payload, timeout=timeout)

    def get_path_size(
        self, path: Optional[Union[str, PathLike[str]]] = None, timeout: int = 30
    ) -> Response:
        """
        Gets path size.

        Returns the size of the file or folder `path` and `-1` if the path is
        unaccessible (non-existent or insufficient privs)
        """
        payload = {
            "method": "core.get_path_size",
            "params": [str(path)] if path else [],
            "id": self.ID,
        }
        return self.execute_call(payload, timeout=timeout)

    def get_labels(self, timeout: int = 30) -> Response:
        """Gets defined labels"""
        payload = {
            "method": "label.get_labels",
            "params": [],
            "id": self.ID,
        }
        return self.execute_call(payload, timeout=timeout)

    def set_label(self, info_hash: str, label: str, timeout: int = 30) -> Response:
        """Sets the label for a specific torrent"""
        payload = {
            "method": "label.set_torrent",
            "params": [info_hash, label.lower()],
            "id": self.ID,
        }
        return self.execute_call(payload, timeout=timeout)

    def add_label(self, label: str, timeout: int = 30) -> Response:
        """Adds a label to the client, ignoring labels if they already exist"""
        payload = {
            "method": "label.add",
            "params": [label.lower()],
            "id": self.ID,
        }
        response = self.execute_call(payload, handle_error=False, timeout=timeout)
        if response.error is None:
            return response

        if isinstance(
            response.error, dict
        ) and "Label already exists" in response.error.get("message", ""):
            return response

        raise DelugeWebClientError(f"Error adding label:\n{response.error}")

    def get_libtorrent_version(self, timeout: int = 30) -> Response:
        """Gets libtorrent version"""
        payload = {
            "method": "core.get_libtorrent_version",
            "params": [],
            "id": self.ID,
        }
        return self.execute_call(payload, timeout=timeout)

    def get_listen_port(self, timeout: int = 30) -> Response:
        """Gets listen port"""
        payload = {
            "method": "core.get_listen_port",
            "params": [],
            "id": self.ID,
        }
        return self.execute_call(payload, timeout=timeout)

    def get_plugins(self, timeout: int = 30) -> Response:
        """Gets plugins"""
        payload = {
            "method": "web.get_plugins",
            "params": [],
            "id": self.ID,
        }
        return self.execute_call(payload, timeout=timeout)

    def get_torrent_files(self, torrent_id: str, timeout: int = 30) -> Response:
        """Gets the files for a torrent in tree format"""
        payload = {
            "method": "web.get_torrent_files",
            "params": [torrent_id],
            "id": self.ID,
        }
        return self.execute_call(payload, timeout=timeout)

    def get_torrent_status(
        self,
        torrent_id: str,
        keys: list[str] = [],
        diff: bool = False,
        timeout: int = 30,
    ) -> Response:
        """
        Gets the status for a torrent.

        Args:
            torrent_id (str): Torrent hash of for a single torrent.
            keys (list[str]): List of specific torrent's property keys to fetch.
            diff (bool): Whether to return the status difference.
            timeout (int): Time to timeout for the call.

        Returns:
            Response: The response from the API call.
        """
        payload = {
            "method": "core.get_torrent_status",
            "params": [torrent_id, keys, diff],
            "id": self.ID,
        }
        return self.execute_call(payload, timeout=timeout)

    def get_torrents_status(
        self,
        filter_dict: dict = {},
        keys: list[str] = [],
        diff: bool = False,
        timeout: int = 30,
    ) -> Response:
        """
        Gets the status for multiple torrents, returns all torrents,
        optionally filtered by filter_dict

        Args:
            filter_dict (dict): Filtering criteria for torrents.
            keys (list[str]): List of specific torrents' property keys to fetch.
            diff (bool): Whether to return the status difference.
            timeout (int): Time to timeout for the call.

        Returns:
            Response: The response from the API call.

        Example `filter_dict`:
        >>> {"id": ["tid", "tid"]}
        ... or
        >>> state = str(TorrentState.SEEDING)
        >>> {"state": state, "id": ["tid", "tid"]}
        """
        payload = {
            "method": "core.get_torrents_status",
            "params": [filter_dict, keys, diff],
            "id": self.ID,
        }
        return self.execute_call(payload, timeout=timeout)

    def check_connected(self, timeout: int = 30) -> Response:
        """
        Use the `web.connected` method to get a boolean response if the Web UI is
        connected to a deluged host
        """
        payload = {
            "method": "web.connected",
            "params": [],
            "id": self.ID,
        }
        return self.execute_call(payload, timeout=timeout)

    def get_hosts(self, timeout: int = 30) -> Response:
        """Returns hosts we're connected to currently"""
        payload = {
            "method": "web.get_hosts",
            "params": [],
            "id": self.ID,
        }
        return self.execute_call(payload, timeout=timeout)

    def get_host_status(self, host_id: str, timeout: int = 30) -> Response:
        """Get the deluged host status `<hostID>`"""
        payload = {
            "method": "web.get_host_status",
            "params": [host_id],
            "id": self.ID,
        }
        return self.execute_call(payload, timeout=timeout)

    def connect_to_host(self, host_id: str, timeout: int = 30) -> Response:
        """To connect to deluged with `<hostID>`"""
        payload = {
            "method": "web.connect",
            "params": [host_id],
            "id": self.ID,
        }
        return self.execute_call(payload, timeout=timeout)

    def test_listen_port(self, timeout: int = 30) -> bool:
        """Checks if the active port is open

        Returns:
            bool: If active port is opened or closed
        """
        payload = {
            "method": "core.test_listen_port",
            "params": [],
            "id": self.ID,
        }
        check_port = self.execute_call(payload, timeout=timeout)
        if check_port.result is not None:
            return True
        return False

    def pause_torrent(self, torrent_id: str, timeout: int = 30) -> Response:
        """Pause a specific torrent"""
        payload = {
            "method": "core.pause_torrent",
            "params": [torrent_id],
            "id": self.ID,
        }
        return self.execute_call(payload, timeout=timeout)

    def pause_torrents(self, torrent_ids: list, timeout: int = 30) -> Response:
        """Pause a list of torrents"""
        payload = {
            "method": "core.pause_torrents",
            "params": [torrent_ids],
            "id": self.ID,
        }
        return self.execute_call(payload, timeout=timeout)

    def remove_torrent(self, torrent_id: str, timeout: int = 30) -> Response:
        """Removes a specific torrent"""
        payload = {
            "method": "core.remove_torrent",
            "params": [torrent_id],
            "id": self.ID,
        }
        return self.execute_call(payload, timeout=timeout)

    def remove_torrents(self, torrent_ids: list, timeout: int = 30) -> Response:
        """Removes a list of torrents"""
        payload = {
            "method": "core.remove_torrents",
            "params": [torrent_ids],
            "id": self.ID,
        }
        return self.execute_call(payload, timeout=timeout)

    def resume_torrent(self, torrent_id: str, timeout: int = 30) -> Response:
        """Resumes a specific torrent"""
        payload = {
            "method": "core.resume_torrent",
            "params": [torrent_id],
            "id": self.ID,
        }
        return self.execute_call(payload, timeout=timeout)

    def resume_torrents(self, torrent_ids: list, timeout: int = 30) -> Response:
        """Resumes a list of torrents"""
        payload = {
            "method": "core.resume_torrents",
            "params": [torrent_ids],
            "id": self.ID,
        }
        return self.execute_call(payload, timeout=timeout)

    def set_torrent_trackers(
        self, torrent_id: str, trackers: list[dict[str, Any]], timeout: int = 30
    ) -> Response:
        """Sets a torrents tracker list. trackers will be ``[{"url", "tier"}]``"""
        payload = {
            "method": "core.set_torrent_trackers",
            "params": [torrent_id, trackers],
            "id": self.ID,
        }
        return self.execute_call(payload, timeout=timeout)

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
            self.ID += 1
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
    def _normalize_exception(exc_str: Any) -> Union[str, Any]:
        """
        Removes the un-needed ending square bracket and stripping extra white
        space if input is a string
        """
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
