<div align="center">

# Deluge Web API Client

![PyPI Version](https://img.shields.io/pypi/v/deluge-web-client)
![Python Versions](https://img.shields.io/pypi/pyversions/deluge-web-client)
![License](https://img.shields.io/github/license/jessielw/deluge-web-client)
[![Mypy](https://github.com/jessielw/deluge-web-client/actions/workflows/mypy.yml/badge.svg)](https://github.com/jessielw/deluge-web-client/actions/workflows/mypy.yml)
[![PyPI](https://github.com/jessielw/deluge-web-client/actions/workflows/python_publish.yml/badge.svg)](https://github.com/jessielw/deluge-web-client/actions/workflows/python_publish.yml)
[![Ruff](https://github.com/jessielw/deluge-web-client/actions/workflows/ruff.yml/badge.svg)](https://github.com/jessielw/deluge-web-client/actions/workflows/ruff.yml)
[![codecov](https://codecov.io/github/jessielw/deluge-web-client/graph/badge.svg?token=TQQQ0NOG5F)](https://codecov.io/github/jessielw/deluge-web-client)

Python client implementation for [Deluge](https://deluge-torrent.org/) Web API

</div>

User Guide and API Reference available on [Read the Docs](https://deluge-web-client.readthedocs.io).

## Features

- Provides access to the majority of Web API methods as well as key **core** functionalities through RPC. For more details, see the official [Web API Documentation](https://deluge.readthedocs.io/en/deluge-2.0.1/reference/webapi.html) and [RPC API Documentation](https://deluge.readthedocs.io/en/deluge-2.0.1/reference/api.html).

- Allows you to use direct **http** connections, allowing access via **reverse proxy** or any **direct url**.

## Installation

Install via pip from [PyPI](https://pypi.org/project/deluge-web-client/):

```bash
python -m pip install deluge-web-client
# or
poetry add deluge-web-client
```

## Getting Started

Before getting started, ensure that you have a running instance of Deluge with the WebUI enabled. You will also need to have a user set up for authentication. For guidance on setting up the WebUI, visit the [Deluge setup guide](https://deluge-torrent.org/userguide/). Another good tutorial is [Trash-Guides basic setup](https://trash-guides.info/Downloaders/Deluge/Basic-Setup/).

## Basic Usage

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
print(upload)
# Response(result=True, error=None, id=1)

# retrieve and show all torrents
all_torrents = client.get_torrents_status()

# pause torrent (pass torrent hash)
pause_torrent = client.pause_torrent("0407326f9d74629d299b525bd5f9b5dd583xxxx")

# remove torrent
remove_torrent = client.remove_torrent("0407326f9d74629d299b525bd5f9b5dd583xxxx")
```

## Context Manager

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
    print(upload)
    # Response(result="0407326f9d74629d299b525bd5f9b5dd583xxxx", error=None, id=1)
```

## Notes

Calling `client.disconnect()` will log the user out of the WebUI in both the client and **any connected web browser**. Be cautious if you're also logged in to the WebUI via your browser as this will terminate your session there as well.

## Access RPC Directly

This package uses HTTP to connect to the Deluge client, relying on the **Web API / JSON** to handle these calls. It's fully capable of making **all** core calls to the Deluge backend. However, if you are looking for a package focused solely on **RPC**, consider [deluge-client](https://github.com/JohnDoee/deluge-client), which served as inspiration for this project alongside [qbittorrent-api](https://github.com/rmartin16/qbittorrent-api).
