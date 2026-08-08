# Changelog

All notable changes to this project will be documented in this file starting with **v2.0.0**.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.1] - 2026-08-08

### Added

- Added `DelugeWebClientConnectionError`, `DelugeWebClientTimeoutError`, `DelugeWebClientHTTPError`, `DelugeWebClientRPCError`, and `DelugeWebClientDecodeError`, all subclassing `DelugeWebClientError`. Existing `except DelugeWebClientError` code is unaffected.
- Documented error handling in the README and user guide, including the two exceptions that are deliberately not wrapped (`ValueError` for a malformed URL, `OSError` for an unreadable torrent file).

### Fixed

- Transport failures from `niquests` (unreachable host, DNS, TLS, proxy, timeouts) no longer escape as `niquests.exceptions.*`. They are now raised as `DelugeWebClientConnectionError` or `DelugeWebClientTimeoutError`, with the original exception preserved as `__cause__`. This previously affected every call, most visibly `login()` against a URL with no Deluge instance behind it.

## [2.1.0] - 2026-08-03

### Changed

- Replaced mypy with strict basedpyright type checking.
- Strengthened linting, branch coverage, documentation, and package-build checks.
- Updated response and torrent option annotations to match Deluge values.

### Fixed

- Propagated login timeouts through host discovery and connection calls.
- Corrected empty host lookup and closed listen-port results.
- Hardened URL normalization and JSON-RPC response validation.

## [2.0.3] - 2025-12-15

### Added

- Added `py.typed` marker file for PEP 561 compliance, allowing the library's type hints to be used by external tools.
- Added `Typing :: Typed` classifier to project metadata.
- Added Dependabot configuration for automated dependency updates.
- Added strict `mypy` configuration for better type safety.

### Changed

- Modernized type annotations throughout the codebase using `from __future__ import annotations` and Python 3.10+ style unions (`|`).
- Updated development dependencies.

### Fixed

- Fixed potential issues with mutable default arguments in `get_torrent_status`, `get_torrents_status`, and `update_ui`.

## [2.0.2] - 2025-12-10

### Added

- Support for Python 3.14

## [2.0.1] - 2025-11-09

### Added

- `TorrentOptions` for fine grained control of torrents _(replacement for `ParamArgs`)_.
  - This allows for complete control of what happens to your torrent during upload.
- `DelugeWebClient`:
  - Arg for `daemon_port` that defaults to **58846**.
  - Method `start_daemon`.
    - Start local daemon.
  - Method `stop_daemon`.
    - Stop local daemon.
  - Method `update_ui`.
    - Gathers detailed information to update UIs.
  - Method `add_host`.
    - Add a host to the host list.
  - Method `remove_host`.
    - Remove a host from the host list.
  - Method `edit_host`.
    - Edit a host in the host list.
  - Method `find_host_id_by_name`.
    - Find a host ID by its name.

### Changed

- Swap from **Poetry** to **uv**.
- Improved error handling.
- Optimized several parts of the code to keep it light and fast.

### Removed

- `ParamArgs` _(replaced with `TorrentOptions`)_.
- Signature for `Response` has been changed:
  - Removed `id` arg.

### Fixed

- Potential error for for case insensitive enum.
