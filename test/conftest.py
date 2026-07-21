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

import threading

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


@pytest.fixture(autouse=True)
def _stop_leaked_provider_threads() -> None:
    """Stop any TileProvider threads not explicitly shut down by tests.

    Tests that call provider.start() but not provider.stop() leak
    daemon threads that accumulate across tests and eventually
    exhaust system resources (thread stacks, fd table), causing
    segmentation faults.
    """
    try:
        from zooui.tilesystem.tileproviders.tileprovider import TileProvider
    except ImportError:
        yield
        return

    before = {t for t in threading.enumerate() if isinstance(t, TileProvider)}
    yield
    try:
        after = {t for t in threading.enumerate() if isinstance(t, TileProvider)}
        leaked = after - before
        for provider in leaked:
            provider.stop()
        for provider in leaked:
            if provider.is_alive():
                provider.join(timeout=2.0)
    except Exception:
        pass
