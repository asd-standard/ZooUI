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

"""Pytest configuration for the entire test directory.

Provides fixtures and hooks that apply to both unit and integration tests.
"""

import pytest


@pytest.fixture(autouse=True)
def _reset_converter_pool() -> None:
    """Reset the process pool between tests to prevent BrokenProcessPool cascading.

    The converterrunner module uses a global ProcessPoolExecutor. If a
    test causes a worker crash (e.g. libvips segfault), the pool stays
    broken for all subsequent tests. Resetting it after each test
    ensures isolation.
    """
    yield
    try:
        from zooui.converters import converterrunner

        if converterrunner._executor is not None:
            converterrunner.shutdown()
    except Exception:
        pass
