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

"""Frozen-mode path utilities for PyInstaller / Nuitka bundles.

When the application is bundled into a standalone executable, file paths
that rely on ``__file__`` or the current working directory must be resolved
relative to the extraction directory (``sys._MEIPASS``) instead.
"""

import os
import sys


def is_frozen() -> bool:
    """Return True if the application is running as a frozen bundle.

    Compatible with PyInstaller, cx_Freeze, py2exe, and Nuitka.
    """
    return getattr(sys, "frozen", False)


def data_dir() -> str:
    """Return the absolute path to the bundled data directory.

    In frozen mode (PyInstaller ``--onefile``), this is ``sys._MEIPASS``
    -- the temporary directory where the executable extracts its payload.

    When running from source, this is the project root (two directories
    above this module, i.e. the directory containing ``zooui/``, ``data/``,
    and ``main.py``).
    """
    if is_frozen():
        return sys._MEIPASS  # type: ignore[attr-defined]
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def binary_dir() -> str:
    """Return the absolute path to the directory containing bundled binaries.

    In frozen mode this is the same as :func:`data_dir`. When running from
    source, binaries are expected to be on ``PATH``, so an empty string is
    returned (callers should fall back to the bare binary name).
    """
    return data_dir() if is_frozen() else ""
