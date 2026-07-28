## ZooUI - Zooming User Interface
## Copyright (C) 2009 David Roberts <d@vidr.cc>
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 3
## of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, see <https://www.gnu.org/licenses/>.

"""XDG Base Directory path resolution for writable user data.

Centralizes all writable path resolution into a single module backed by
``platformdirs``, following the XDG Base Directory specification.

``platformdirs`` is platform-neutral:
- Linux: respects ``$XDG_CONFIG_HOME``, ``$XDG_DATA_HOME``,
  ``$XDG_CACHE_HOME``, ``$XDG_STATE_HOME`` env vars
- macOS: ``~/Library/Application Support/zooui/`` etc.
- Windows: ``%APPDATA%`` / ``%LOCALAPPDATA%`` equivalents
"""

from pathlib import Path

from platformdirs import user_cache_dir, user_config_dir, user_data_dir, user_state_dir

APPNAME = "zooui"


def get_config_file() -> Path:
    """Return the path to the application config file.

    Example: ``~/.config/zooui/config.json``
    """
    return Path(user_config_dir(APPNAME, ensure_exists=False)) / "config.json"


def get_data_dir() -> Path:
    """Return the writable data directory for the application.

    Subdirectories (backups, colorstore, etc.) are created by callers.

    Example: ``~/.local/share/zooui/``
    """
    return Path(user_data_dir(APPNAME, ensure_exists=False))


def get_cache_dir() -> Path:
    """Return the cache directory for the application.

    Cache data (tiles, SVG render cache) may be deleted without data loss.

    Example: ``~/.cache/zooui/``
    """
    return Path(user_cache_dir(APPNAME, ensure_exists=False))


def get_state_dir() -> Path:
    """Return the state directory for the application.

    State data (logs) is non-essential application state.

    Example: ``~/.local/state/zooui/``
    """
    return Path(user_state_dir(APPNAME, ensure_exists=False))


def get_colorstore_dir() -> Path:
    """Return the color history storage directory.

    Example: ``~/.local/share/zooui/colorstore/``
    """
    return get_data_dir() / "colorstore"
