from __future__ import annotations


class DelugeWebClientError(Exception):
    """Represent an error detected while using the Deluge Web API.

    This is the base class for every exception raised by this package. Catching
    it is enough to handle any Deluge or network related failure::

        try:
            client.login()
        except DelugeWebClientError as exc:
            ...

    The only exceptions that are deliberately *not* wrapped are
    :exc:`ValueError` (a malformed URL passed to
    :class:`~deluge_web_client.client.DelugeWebClient`) and :exc:`OSError`
    (an unreadable torrent file).
    """


class DelugeWebClientConnectionError(DelugeWebClientError):
    """The Deluge Web UI could not be reached.

    Raised when the underlying transport fails outright: the host is
    unreachable, DNS resolution fails, the TLS handshake fails, a proxy
    rejects the request, or there is no Deluge instance listening at the
    configured URL. The originating ``niquests`` exception is available as
    ``__cause__``.
    """


class DelugeWebClientTimeoutError(DelugeWebClientError):
    """The request to the Deluge Web UI timed out.

    Covers both connect and read timeouts. The originating ``niquests``
    exception is available as ``__cause__``.
    """


class DelugeWebClientHTTPError(DelugeWebClientError):
    """The Deluge Web UI returned a non-2xx HTTP status.

    Args:
        message: Human readable description of the failure.
        status_code: HTTP status code returned by the server, if known.
        reason: HTTP reason phrase returned by the server, if known.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        reason: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.reason = reason


class DelugeWebClientRPCError(DelugeWebClientError):
    """The Deluge Web UI returned a JSON-RPC error.

    The HTTP request itself succeeded, but Deluge reported an error in the
    response body (bad password, unknown method, torrent failed to add, ...).

    Args:
        message: Human readable description of the failure.
        method: JSON-RPC method that produced the error, if known.
        error_class: Deluge exception class name parsed out of the error,
            e.g. ``deluge.error.AddTorrentError``.
        info_hash: Info hash parsed out of the error message, if present.
    """

    def __init__(
        self,
        message: str,
        *,
        method: str | None = None,
        error_class: str | None = None,
        info_hash: str | None = None,
    ) -> None:
        super().__init__(message)
        self.method = method
        self.error_class = error_class
        self.info_hash = info_hash


class DelugeWebClientDecodeError(DelugeWebClientError):
    """The response body was not a JSON-RPC object.

    Raised when the body could not be parsed as JSON at all, or parsed into
    something other than a JSON object. Usually means the URL points at
    something that is not a Deluge Web UI.
    """
