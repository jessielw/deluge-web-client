=====================
Deluge Web API Client 
=====================

.. image:: https://img.shields.io/pypi/v/deluge-web-client
    :target: https://pypi.org/project/deluge-web-client
    :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/deluge-web-client
    :target: https://pypi.org/project/deluge-web-client
    :alt: Python Versions

.. image:: https://img.shields.io/github/license/jessielw/deluge-web-client
    :target: https://github.com/jessielw/deluge-web-client
    :alt: License

.. image:: https://github.com/jessielw/deluge-web-client/actions/workflows/python_publish.yml/badge.svg
   :target: https://github.com/jessielw/deluge-web-client/actions/workflows/python_publish.yml
   :alt: PyPI

.. image:: https://github.com/jessielw/deluge-web-client/actions/workflows/ruff.yml/badge.svg
   :target: https://github.com/jessielw/deluge-web-client/actions/workflows/ruff.yml
   :alt: Ruff

.. image:: https://codecov.io/github/jessielw/deluge-web-client/graph/badge.svg?token=TQQQ0NOG5F
   :target: https://codecov.io/github/jessielw/deluge-web-client
   :alt: codecov

Python HTTP client implementation for `Deluge <https://deluge-torrent.org>`_

Features
--------

- Provides access to the majority of Web API methods as well as key **core** functionalities through RPC. For more details, see the official `Web API Documentation <https://deluge.readthedocs.io/en/latest/reference/webapi.html>`_ and `RPC API Documentation <https://deluge.readthedocs.io/en/latest/reference/api.html>`_.

- Allows you to use direct **http** connections, allowing access via **reverse proxy** or any **direct url**.

Installation
------------

Install via pip from `PyPI <https://pypi.org/project/deluge-web-client/>`_:

.. code-block:: bash

    python -m pip install deluge-web-client
    # or
    poetry add deluge-web-client
    # or
    uv add deluge-web-client

Getting Started
---------------

Before getting started, ensure that you have a running instance of Deluge with the WebUI enabled. 
You will also need to have a user set up for authentication. For guidance on setting up the WebUI, 
visit the `Deluge setup guide <https://deluge-torrent.org/userguide/>`_. Another good tutorial is 
`Trash-Guides basic setup <https://trash-guides.info/Downloaders/Deluge/Basic-Setup/>`_.

Basic Usage
-----------

.. code-block:: python

    from deluge_web_client import DelugeWebClient, TorrentOptions

    # instantiate a client
    client = DelugeWebClient(
        url="https://site.net/deluge",
        password="example_password",
        daemon_port=58846,  # optional
    )

    # login
    # once logged in the `client` will maintain the logged in state as long as you don't call
    # client.disconnect()
    client.login()

    # uploading a torrent
    # 1) define your torrent options (what ever you don't set here will utilize Deluge defaults)
    torrent_options = TorrentOptions(
        add_paused=True,
        auto_managed=True,
    )
    # 2) upload the torrent and capture the returned output
    upload = client.upload_torrent(
        torrent_path="filepath.torrent",
        torrent_options=torrent_options,
    )
    # this will return a `Response` object
    print(upload)
    # Response(result=True, error=None, message="Torrent added successfully")

    # retrieve and show all torrents
    all_torrents = client.get_torrents_status()

    # pause torrent (pass torrent hash)
    pause_torrent = client.pause_torrent("0407326f9d74629d299b525bd5f9b5dd583xxxx")

    # remove torrent
    remove_torrent = client.remove_torrent("0407326f9d74629d299b525bd5f9b5dd583xxxx")

Context Manager
---------------

.. code-block:: python

    from deluge_web_client import DelugeWebClient, TorrentOptions

    # using a context manager automatically logs you in
    with DelugeWebClient(url="https://site.net/deluge", password="example_password") as client:
        torrent_options = TorrentOptions(
            add_paused=True,
            auto_managed=True,
        )
        upload = client.upload_torrent(
            torrent_path="filepath.torrent",
            torrent_options=torrent_options,
        )
        print(upload)
        # Response(result="<torrent-id>", error=None, message="Torrent added successfully")

Error Handling
--------------

Every Deluge or network failure raises :exc:`~deluge_web_client.exceptions.DelugeWebClientError`
or one of its subclasses, so catching the base class is always enough::

    DelugeWebClientError
    ├── DelugeWebClientConnectionError   # unreachable host, DNS, TLS, proxy
    ├── DelugeWebClientTimeoutError      # connect / read timeout
    ├── DelugeWebClientHTTPError         # non-2xx (.status_code, .reason)
    ├── DelugeWebClientRPCError          # Deluge reported an error (.method, .error_class, .info_hash)
    └── DelugeWebClientDecodeError       # response body was not a JSON object

.. code-block:: python

    from deluge_web_client import (
        DelugeWebClient,
        DelugeWebClientConnectionError,
        DelugeWebClientError,
        DelugeWebClientRPCError,
    )

    client = DelugeWebClient(url="https://site.net/deluge", password="example_password")

    try:
        client.login()
    except DelugeWebClientConnectionError:
        print("no Deluge Web UI at that URL")
    except DelugeWebClientRPCError as error:
        print(f"Deluge rejected the call: {error.method}")
    except DelugeWebClientError as error:
        # catches everything above, including anything added in the future
        print(f"something went wrong: {error}")

The underlying ``niquests`` exception is preserved as ``__cause__`` on connection
and timeout errors if you need the transport level detail.

Two exceptions are deliberately **not** wrapped, because they signal a bad
argument rather than a Deluge failure:

- :exc:`ValueError` -- the ``url`` passed to ``DelugeWebClient`` is not an
  absolute HTTP/HTTPS URL, or contains a fragment.
- :exc:`OSError` / :exc:`FileNotFoundError` -- a torrent file passed to
  ``upload_torrent`` cannot be read.

Notes
-----

Calling ``client.disconnect()`` disconnects the Web UI session from its currently
connected Deluge daemon. Call ``client.close_session()`` when you only need to
release this client's HTTP resources.

Access RPC Directly
-------------------

This package uses HTTP to connect to the Deluge client, relying on the **Web API / JSON** to handle these calls. It's fully capable of making **all** core calls to the Deluge backend. However, if you are looking for a package focused solely on **RPC**, consider `deluge-client <https://github.com/JohnDoee/deluge-client>`_, which served as inspiration for this project alongside `qbittorrent-api <https://github.com/rmartin16/qbittorrent-api>`_.
