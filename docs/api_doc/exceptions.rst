==========
Exceptions
==========

Every Deluge or network failure raises :exc:`~deluge_web_client.exceptions.DelugeWebClientError`
or one of its subclasses. Catching the base class handles all of them, including
any subclass added in a future release::

    DelugeWebClientError
    ├── DelugeWebClientConnectionError   # unreachable host, DNS, TLS, proxy
    ├── DelugeWebClientTimeoutError      # connect / read timeout
    ├── DelugeWebClientHTTPError         # non-2xx (.status_code, .reason)
    ├── DelugeWebClientRPCError          # Deluge reported an error (.method, .error_class, .info_hash)
    └── DelugeWebClientDecodeError       # response body was not a JSON object

Transport failures from the underlying ``niquests`` library are translated into
:exc:`~deluge_web_client.exceptions.DelugeWebClientConnectionError` and
:exc:`~deluge_web_client.exceptions.DelugeWebClientTimeoutError`; the original
exception is kept as ``__cause__``.

:exc:`ValueError` (a malformed URL passed to
:class:`~deluge_web_client.client.DelugeWebClient`) and :exc:`OSError` (an
unreadable torrent file) are deliberately not wrapped, as they signal a bad
argument rather than a Deluge failure.

.. autoclass:: deluge_web_client.exceptions.DelugeWebClientError
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: deluge_web_client.exceptions.DelugeWebClientConnectionError
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: deluge_web_client.exceptions.DelugeWebClientTimeoutError
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: deluge_web_client.exceptions.DelugeWebClientHTTPError
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: deluge_web_client.exceptions.DelugeWebClientRPCError
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: deluge_web_client.exceptions.DelugeWebClientDecodeError
   :members:
   :undoc-members:
   :show-inheritance:
