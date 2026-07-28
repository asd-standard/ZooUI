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

"""Path utilities for data files across source, pip, and frozen deployments.

Resolves the application data directory (``zooui/data/``) in three modes:

- **Source checkout**: ``__file__``-relative, ``zooui/utils/`` → ``zooui/``
- **Pip install**: ``importlib.resources.files("zooui")`` → package directory
- **Frozen** (PyInstaller / Nuitka): ``sys._MEIPASS`` → extraction root
"""

import importlib.resources
import os
import sys


def is_frozen() -> bool:
    """Return True if the application is running as a frozen bundle.

    Compatible with PyInstaller, cx_Freeze, py2exe, and Nuitka.
    """
    return getattr(sys, "frozen", False)


def data_dir() -> str:
    """Return the absolute path to the ``zooui/`` package directory.

    This is the directory that directly contains the ``data/`` subdirectory
    with bundled resources (icon, home scene, SVGs, etc.).

    In frozen mode (PyInstaller ``--onefile``), this is ``sys._MEIPASS``
    -- the temporary directory where the executable extracts its payload.
    Callers append ``"data"`` to reach bundled resources.
    """
    if is_frozen():
        return sys._MEIPASS  # type: ignore[attr-defined]
    try:
        return str(importlib.resources.files("zooui"))
    except Exception:
        pass
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def binary_dir() -> str:
    """Return the absolute path to the directory containing bundled binaries.

    In frozen mode this is the same as :func:`data_dir`. When running from
    source, binaries are expected to be on ``PATH``, so an empty string is
    returned (callers should fall back to the bare binary name).
    """
    return data_dir() if is_frozen() else ""
