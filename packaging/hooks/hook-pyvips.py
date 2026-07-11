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

"""PyInstaller hook for pyvips — ensures libvips-42.dll is discoverable.

On Windows, ``libvips-42.dll`` is bundled into the frozen executable via
``--add-binary``. At runtime, Python needs ``os.add_dll_directory()`` called
on the extraction directory before ``import pyvips`` so that the Windows DLL
loader can find the library.

This hook is injected at build time via ``packaging/zooui.spec`` → ``hookspath``.
"""

import os
import sys


def pre_find_module_path(hook_api: object) -> None:
    """Called before pyvips is imported during frozen runtime."""
    if sys.platform == "win32" and getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            os.add_dll_directory(meipass)
