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
def _stop_leaked_threads() -> None:
    """Stop any daemon threads leaked by tests and force GC.

    Tests that create threads without joining them (TileProvider.start(),
    TileCache periodic_clean, ThreadPoolExecutor workers, etc.) leak
    daemon threads that accumulate and exhaust system resources.
    """
    before_ids = {id(t) for t in threading.enumerate()}
    yield
    try:
        import gc

        gc.collect()
        after = threading.enumerate()
        leaked = [t for t in after if id(t) not in before_ids and t.daemon and t.is_alive()]
        for thread in leaked:
            for method in ("stop", "shutdown"):
                if hasattr(thread, method):
                    try:
                        getattr(thread, method)()
                    except Exception:
                        pass
        for thread in leaked:
            if thread.is_alive():
                thread.join(timeout=2.0)
    except Exception:
        pass
