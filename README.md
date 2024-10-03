<div align="center">

# Deluge Web API Client

Python client implementation for Deluge Web API

</div>

Currently supports qBittorrent [v2.1.1](https://deluge-torrent.org).

User Guide and API Reference available on [Read the Docs](https://deluge-web-client.readthedocs.io).

## Features

- Access to most of the Web API as well as most of the **core** methods (accessed via RPC). [Web API](https://deluge.readthedocs.io/en/deluge-2.0.1/reference/webapi.html) / [RPC API](https://deluge.readthedocs.io/en/deluge-2.0.1/reference/api.html)
- Allows you to use direct **http** connections, allowing access via **reverse proxy** or any **direct url**.

## Installation

Install via pip from [PyPI](https://pypi.org/project/deluge-web-client/)

```bash
python -m pip install deluge-web-client
```

## Before Getting Started

This assumes you have a running Deluge instance with the WebUI enabled and a user of your choice setup.

## Getting Started - Basic

```python
from deluge_web_client import DelugeWebClient

# instantiate a client
client = DelugeWebClient(url="https://site.net/deluge", password="example_password")

# login
# once logged in the `client` will maintain the logged in state as long as you don't call
# client.disconnect()
client.login()

# upload a torrent
upload = client.upload_torrent(
    torrent_path="filepath.torrent",
    add_paused=False, # optional
    seed_mode=False, # optional
    auto_managed=False, # optional
    save_directory=None, # optional
    label=None, # optional
)
# this will return a `Response` object
>>> print(upload)
>>> Response(result=True, error=None, id=1)

# retrieve and show all torrents
all_torrents = client.get_torrents_status()

# pause torrent (pass torrent hash)
pause_torrent = client.pause_torrent("0407326f9d74629d299b525bd5f9b5dd583xxxx")

# remove torrent
remove_torrent = client.remove_torrent("0407326f9d74629d299b525bd5f9b5dd583xxxx")
```

## Getting Started - Context Manager

```python
from deluge_web_client import DelugeWebClient

# using a context manager automatically logs you in
with DelugeWebClient(url="https://site.net/deluge", password="example_password") as client:
    upload = client.upload_torrent(
        torrent_path="filepath.torrent",
        add_paused=False, # optional
        seed_mode=False, # optional
        auto_managed=False, # optional
        save_directory=None, # optional
        label=None, # optional
    )
    >>> print(upload)
    >>> Response(result="0407326f9d74629d299b525bd5f9b5dd583xxxx", error=None, id=1)
```

## Notes

You don't need to explicitly call `client.disconnect()` with either of the above approaches. Calling
this method actually disconnects your user from this instance **and** all instances inside of your
browser.

## Access RPC Directly

This package utilizes HTTP to connect to your client, it relies on the **Web API / JSON** to handle
these calls. It's totally capable of making **all** core calls to the deluge back end. However, if
you want a package explicitly designed for **RPC** only you should look at
[deluge-client](https://github.com/JohnDoee/deluge-client). This project was inspired from **deluge-client** as well
as [qbittorrent-api](https://github.com/rmartin16/qbittorrent-api).
