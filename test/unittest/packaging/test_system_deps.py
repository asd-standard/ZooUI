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

"""
Feature: System Dependency Check

Tests that _check_system_deps() correctly detects the presence or absence
of libvips (required) and pdftoppm (optional).  The function is re-entrant
and can be called multiple times independently of the module-level check.
"""

import ctypes
import ctypes.util
from unittest.mock import patch

import pytest

from zooui.app import _check_system_deps


class TestSystemDepsWithLibvips:
    """Feature: Check passes when libvips is available."""

    def test_check_passes_with_libvips_installed(self):
        """Scenario: _check_system_deps does not raise when libvips is present."""
        try:
            _check_system_deps()
        except SystemExit as e:
            pytest.fail(f"System dep check failed unexpectedly: {e}")


class TestSystemDepsMissingLibvips:
    """Feature: Check fails with clear instructions when libvips is broken."""

    def test_libvips_completely_missing(self):
        """Scenario: find_library returns None and CDLL fails → exit with instructions."""
        with (
            patch.object(ctypes.util, "find_library", return_value=None),
            patch.object(ctypes, "CDLL", side_effect=OSError("test")),
        ):
            with pytest.raises(SystemExit) as exc_info:
                _check_system_deps()

        msg = str(exc_info.value)
        assert "libvips" in msg.lower()
        assert "apt install" in msg
        assert "conda" in msg.lower()
        assert "brew install" in msg

    def test_libvips_found_but_unloadable(self):
        """Scenario: libvips found on disk but CDLL raises → exit with conda-forge hint.

        Simulates a broken installation (e.g., incompatible conda channels).
        """

        def _fail_cdll(_name, _mode=0):
            raise OSError("cannot load library: undefined symbol")

        with (
            patch.object(ctypes.util, "find_library", return_value="/fake/libvips.so.42"),
            patch.object(ctypes, "CDLL", _fail_cdll),
        ):
            with pytest.raises(SystemExit) as exc_info:
                _check_system_deps()

        msg = str(exc_info.value)
        assert "libvips" in msg.lower()
        assert "conda-forge" in msg


class TestSystemDepsPdfToPpm:
    """Feature: pdftoppm is optional — warns but does not exit."""

    def test_pdftoppm_missing_prints_warning(self, capsys):
        """Scenario: shutil.which('pdftoppm') returns None → prints warning to stderr."""
        with patch("shutil.which", return_value=None):
            _check_system_deps()

        captured = capsys.readouterr()
        assert "pdftoppm" in captured.err.lower()
        assert "PDF" in captured.err

    def test_pdftoppm_present_is_silent(self, capsys):
        """Scenario: shutil.which('pdftoppm') returns a path → no warning."""
        with patch("shutil.which", return_value="/usr/bin/pdftoppm"):
            _check_system_deps()

        captured = capsys.readouterr()
        assert "pdftoppm" not in captured.err
