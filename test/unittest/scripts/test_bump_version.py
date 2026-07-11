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
Feature: Version Bump Utility

The bump_version script manages SemVer version bumps across the project.
It updates `zooui/__init__.py`, `pyproject.toml`, `data/home.pzs`, and
captures a fresh `data/home.png` screenshot.
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest import mock

import pytest

_scripts_dir = Path(__file__).resolve().parents[3] / "scripts"
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

import bump_version as bv


@pytest.fixture
def temp_init_file(tmp_path):
    """Create a temporary __init__.py with a version string."""
    path = tmp_path / "zooui" / "__init__.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('__version__ = "0.5.2"\n', encoding="utf-8")
    return path


@pytest.fixture
def temp_home_pzs(tmp_path):
    """Create a temporary home.pzs with a version string embedded."""
    path = tmp_path / "data" / "home.pzs"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "-5.0\t620.0 350.0\n"
        'StringMediaObject\tstring:62AA27:0.5.2\t5.5\t14243.0\t7920.0\n',
        encoding="utf-8",
    )
    return path


@pytest.fixture
def temp_pyproject_toml(tmp_path):
    """Create a temporary pyproject.toml with a version string."""
    path = tmp_path / "pyproject.toml"
    path.write_text(
        '[project]\nversion = "0.5.2"\n', encoding="utf-8"
    )
    return path


class TestReadCurrentVersion:
    """Feature: Reading current version from __init__.py"""

    def test_reads_version_string(self, temp_init_file):
        """Scenario: Version string is read from __init__.py"""
        with mock.patch.object(bv, "INIT_PATH", temp_init_file):
            version, line_num, line = bv._read_current_version()
            assert version == "0.5.2"
            assert line_num == 0
            assert '__version__ = "0.5.2"' in line

    def test_exits_when_file_not_found(self):
        """Scenario: Missing __init__.py exits with error"""
        with mock.patch.object(bv, "INIT_PATH", Path("/nonexistent/__init__.py")):
            with pytest.raises(SystemExit) as exc_info:
                bv._read_current_version()
            assert "not found" in str(exc_info.value).lower()

    def test_exits_when_version_not_found(self, tmp_path):
        """Scenario: __init__.py without __version__ exits with error"""
        path = tmp_path / "__init__.py"
        path.write_text("no version here\n", encoding="utf-8")
        with mock.patch.object(bv, "INIT_PATH", path):
            with pytest.raises(SystemExit) as exc_info:
                bv._read_current_version()
            assert "not found" in str(exc_info.value).lower()


class TestWriteNewVersion:
    """Feature: Writing new version to __init__.py"""

    def test_writes_new_version(self, temp_init_file):
        """Scenario: __init__.py is updated with new version string"""
        with mock.patch.object(bv, "INIT_PATH", temp_init_file):
            bv._write_new_version(0, '__version__ = "0.5.2"', "0.6.0")
            content = temp_init_file.read_text(encoding="utf-8")
            assert '__version__ = "0.6.0"' in content

    def test_preserves_other_lines(self, tmp_path):
        """Scenario: Non-version lines are untouched"""
        path = tmp_path / "__init__.py"
        path.write_text(
            '"""Module docstring"""\n__version__ = "0.5.2"\nother = "stuff"\n',
            encoding="utf-8",
        )
        with mock.patch.object(bv, "INIT_PATH", path):
            bv._write_new_version(1, '__version__ = "0.5.2"', "0.6.0")
            content = path.read_text(encoding="utf-8")
            assert '"""Module docstring"""' in content
            assert 'other = "stuff"' in content


class TestUpdateHomePzs:
    """Feature: Updating version in home.pzs StringMediaObject"""

    def test_replaces_version(self, temp_home_pzs):
        """Scenario: Version string in home.pzs is updated"""
        with mock.patch.object(bv, "HOME_PZS_PATH", temp_home_pzs):
            bv._update_home_pzs("0.5.2", "0.6.0")
            content = temp_home_pzs.read_text(encoding="utf-8")
            assert "string:62AA27:0.6.0" in content
            assert "string:62AA27:0.5.2" not in content

    def test_skips_when_file_missing(self):
        """Scenario: Missing home.pzs is silently skipped"""
        with mock.patch.object(bv, "HOME_PZS_PATH", Path("/nonexistent/home.pzs")):
            bv._update_home_pzs("0.5.2", "0.6.0")

    def test_skips_when_version_not_in_content(self, tmp_path):
        """Scenario: Old version not found in file skips update"""
        path = tmp_path / "home.pzs"
        path.write_text("no version here\n", encoding="utf-8")
        with mock.patch.object(bv, "HOME_PZS_PATH", path):
            bv._update_home_pzs("0.5.2", "0.6.0")
            assert path.read_text(encoding="utf-8") == "no version here\n"

    def test_skips_when_no_pattern_matched(self, tmp_path):
        """Scenario: No StringMediaObject pattern matched skips update"""
        path = tmp_path / "home.pzs"
        path.write_text(
            "-5.0\t620.0 350.0\nTiledMediaObject\tdynamic:fern\n",
            encoding="utf-8",
        )
        with mock.patch.object(bv, "HOME_PZS_PATH", path):
            bv._update_home_pzs("0.5.2", "0.6.0")
            content = path.read_text(encoding="utf-8")
            assert "0.6.0" not in content


class TestWritePyprojectVersion:
    """Feature: Updating version in pyproject.toml"""

    def test_updates_version(self, temp_pyproject_toml):
        """Scenario: pyproject.toml version is updated"""
        with mock.patch.object(bv, "PYPROJECT_PATH", temp_pyproject_toml):
            bv._write_pyproject_version("0.6.0")
            content = temp_pyproject_toml.read_text(encoding="utf-8")
            assert 'version = "0.6.0"' in content

    def test_skips_when_file_missing(self):
        """Scenario: Missing pyproject.toml is silently skipped"""
        with mock.patch.object(bv, "PYPROJECT_PATH", Path("/nonexistent/pyproject.toml")):
            bv._write_pyproject_version("0.6.0")


class TestValidateSemver:
    """Feature: SemVer validation"""

    def test_accepts_valid_semver(self):
        """Scenario: Valid SemVer strings are accepted"""
        bv._validate_semver("0.5.2")
        bv._validate_semver("1.0.0")
        bv._validate_semver("10.20.30")

    def test_rejects_invalid_semver(self):
        """Scenario: Invalid strings cause exit"""
        for bad in ["0.5", "1", "a.b.c", "", "0.5.2-beta"]:
            with pytest.raises(SystemExit):
                bv._validate_semver(bad)


class TestBumpForward:
    """Feature: Forward version bumps"""

    @pytest.fixture(autouse=True)
    def _mock_deps(self):
        """Mock screenshot and git tag for all bump tests."""
        with (
            mock.patch.object(bv, "_capture_home_screenshot"),
            mock.patch.object(bv, "_create_git_tag"),
        ):
            yield

    def _setup_files(self, tmp_path):
        """Set up temp files and patch all paths."""
        init = tmp_path / "zooui" / "__init__.py"
        init.parent.mkdir(parents=True, exist_ok=True)
        init.write_text('__version__ = "0.5.2"\n', encoding="utf-8")

        pzs = tmp_path / "data" / "home.pzs"
        pzs.parent.mkdir(parents=True, exist_ok=True)
        pzs.write_text(
            "-5.0\t620.0 350.0\n"
            'StringMediaObject\tstring:62AA27:0.5.2\t5.5\t14243.0\t7920.0\n',
            encoding="utf-8",
        )

        toml = tmp_path / "pyproject.toml"
        toml.write_text('[project]\nversion = "0.5.2"\n', encoding="utf-8")

        return init, pzs, toml

    def test_patch_bump(self, tmp_path):
        """Scenario: patch bump increments patch component"""
        init, pzs, toml = self._setup_files(tmp_path)
        with (
            mock.patch.object(bv, "INIT_PATH", init),
            mock.patch.object(bv, "HOME_PZS_PATH", pzs),
            mock.patch.object(bv, "PYPROJECT_PATH", toml),
        ):
            bv.bump("patch")
            assert '__version__ = "0.5.3"' in init.read_text(encoding="utf-8")
            assert "string:62AA27:0.5.3" in pzs.read_text(encoding="utf-8")
            assert 'version = "0.5.3"' in toml.read_text(encoding="utf-8")

    def test_minor_bump(self, tmp_path):
        """Scenario: minor bump increments minor and zeros patch"""
        init, pzs, toml = self._setup_files(tmp_path)
        with (
            mock.patch.object(bv, "INIT_PATH", init),
            mock.patch.object(bv, "HOME_PZS_PATH", pzs),
            mock.patch.object(bv, "PYPROJECT_PATH", toml),
        ):
            bv.bump("minor")
            assert '__version__ = "0.6.0"' in init.read_text(encoding="utf-8")
            assert "string:62AA27:0.6.0" in pzs.read_text(encoding="utf-8")
            assert 'version = "0.6.0"' in toml.read_text(encoding="utf-8")

    def test_major_bump(self, tmp_path):
        """Scenario: major bump increments major and zeros lower components"""
        init, pzs, toml = self._setup_files(tmp_path)
        with (
            mock.patch.object(bv, "INIT_PATH", init),
            mock.patch.object(bv, "HOME_PZS_PATH", pzs),
            mock.patch.object(bv, "PYPROJECT_PATH", toml),
        ):
            bv.bump("major")
            assert '__version__ = "1.0.0"' in init.read_text(encoding="utf-8")
            assert "string:62AA27:1.0.0" in pzs.read_text(encoding="utf-8")
            assert 'version = "1.0.0"' in toml.read_text(encoding="utf-8")

    def test_tag_flag_creates_tag(self, tmp_path):
        """Scenario: --tag flag creates a git tag via _create_git_tag"""
        init, pzs, toml = self._setup_files(tmp_path)
        with (
            mock.patch.object(bv, "INIT_PATH", init),
            mock.patch.object(bv, "HOME_PZS_PATH", pzs),
            mock.patch.object(bv, "PYPROJECT_PATH", toml),
            mock.patch.object(bv, "_create_git_tag") as mock_tag,
            mock.patch.object(bv, "_capture_home_screenshot"),
        ):
            bv.bump("minor", tag=True)
            mock_tag.assert_called_once_with("0.6.0")


class TestBumpBackwards:
    """Feature: Backwards version bumps"""

    @pytest.fixture(autouse=True)
    def _mock_deps(self):
        with (
            mock.patch.object(bv, "_capture_home_screenshot"),
            mock.patch.object(bv, "_create_git_tag"),
        ):
            yield

    def _setup_files(self, tmp_path, version="0.5.2"):
        init = tmp_path / "zooui" / "__init__.py"
        init.parent.mkdir(parents=True, exist_ok=True)
        init.write_text(f'__version__ = "{version}"\n', encoding="utf-8")

        pzs = tmp_path / "data" / "home.pzs"
        pzs.parent.mkdir(parents=True, exist_ok=True)
        pzs.write_text(
            "-5.0\t620.0 350.0\n"
            f'StringMediaObject\tstring:62AA27:{version}\t5.5\t14243.0\t7920.0\n',
            encoding="utf-8",
        )

        toml = tmp_path / "pyproject.toml"
        toml.write_text(f'[project]\nversion = "{version}"\n', encoding="utf-8")

        return init, pzs, toml

    def test_patch_backwards(self, tmp_path):
        """Scenario: backwards patch decrements patch component"""
        init, pzs, toml = self._setup_files(tmp_path, "0.5.2")
        with (
            mock.patch.object(bv, "INIT_PATH", init),
            mock.patch.object(bv, "HOME_PZS_PATH", pzs),
            mock.patch.object(bv, "PYPROJECT_PATH", toml),
        ):
            bv.bump("patch", backwards=True)
            assert '__version__ = "0.5.1"' in init.read_text(encoding="utf-8")

    def test_minor_backwards(self, tmp_path):
        """Scenario: backwards minor decrements minor, leaves patch unchanged"""
        init, pzs, toml = self._setup_files(tmp_path, "0.5.2")
        with (
            mock.patch.object(bv, "INIT_PATH", init),
            mock.patch.object(bv, "HOME_PZS_PATH", pzs),
            mock.patch.object(bv, "PYPROJECT_PATH", toml),
        ):
            bv.bump("minor", backwards=True)
            assert '__version__ = "0.4.2"' in init.read_text(encoding="utf-8")

    def test_major_backwards(self, tmp_path):
        """Scenario: backwards major decrements major, leaves others unchanged"""
        init, pzs, toml = self._setup_files(tmp_path, "1.3.2")
        with (
            mock.patch.object(bv, "INIT_PATH", init),
            mock.patch.object(bv, "HOME_PZS_PATH", pzs),
            mock.patch.object(bv, "PYPROJECT_PATH", toml),
        ):
            bv.bump("major", backwards=True)
            assert '__version__ = "0.3.2"' in init.read_text(encoding="utf-8")

    def test_backwards_floor_at_zero(self, tmp_path):
        """Scenario: backwards patch at 0.0.0 stays at 0.0.0"""
        init, pzs, toml = self._setup_files(tmp_path, "0.0.0")
        with (
            mock.patch.object(bv, "INIT_PATH", init),
            mock.patch.object(bv, "HOME_PZS_PATH", pzs),
            mock.patch.object(bv, "PYPROJECT_PATH", toml),
        ):
            bv.bump("patch", backwards=True)
            assert '__version__ = "0.0.0"' in init.read_text(encoding="utf-8")
            bv.bump("minor", backwards=True)
            assert '__version__ = "0.0.0"' in init.read_text(encoding="utf-8")
            bv.bump("major", backwards=True)
            assert '__version__ = "0.0.0"' in init.read_text(encoding="utf-8")


class TestBumpCurrent:
    """Feature: Current version subcommand"""

    @pytest.fixture(autouse=True)
    def _mock_deps(self):
        with (
            mock.patch.object(bv, "_capture_home_screenshot"),
            mock.patch.object(bv, "_create_git_tag"),
        ):
            yield

    def test_current_prints_and_captures(self, tmp_path):
        """Scenario: current prints version and re-captures screenshot"""
        init = tmp_path / "zooui" / "__init__.py"
        init.parent.mkdir(parents=True, exist_ok=True)
        init.write_text('__version__ = "0.5.2"\n', encoding="utf-8")

        pzs = tmp_path / "data" / "home.pzs"
        pzs.parent.mkdir(parents=True, exist_ok=True)
        pzs.write_text(
            "-5.0\t620.0 350.0\n"
            'StringMediaObject\tstring:62AA27:0.5.2\t5.5\t14243.0\t7920.0\n',
            encoding="utf-8",
        )

        with (
            mock.patch.object(bv, "INIT_PATH", init),
            mock.patch.object(bv, "HOME_PZS_PATH", pzs),
            mock.patch.object(bv, "_capture_home_screenshot") as mock_shot,
        ):
            bv.bump("current")
            mock_shot.assert_called_once()
            # File should NOT be modified
            assert '__version__ = "0.5.2"' in init.read_text(encoding="utf-8")

    def test_current_does_not_create_tag(self, tmp_path):
        """Scenario: --tag is ignored when part=current"""
        init = tmp_path / "zooui" / "__init__.py"
        init.parent.mkdir(parents=True, exist_ok=True)
        init.write_text('__version__ = "0.5.2"\n', encoding="utf-8")

        with (
            mock.patch.object(bv, "INIT_PATH", init),
            mock.patch.object(bv, "_create_git_tag") as mock_tag,
            mock.patch.object(bv, "_capture_home_screenshot"),
        ):
            bv.bump("current", tag=True)
            mock_tag.assert_not_called()


class TestBumpFileIntegrity:
    """Feature: File integrity during bump operations"""

    @pytest.fixture(autouse=True)
    def _mock_deps(self):
        with (
            mock.patch.object(bv, "_capture_home_screenshot"),
            mock.patch.object(bv, "_create_git_tag"),
        ):
            yield

    def test_home_pzs_origin_zoom_preserved(self, tmp_path):
        """Scenario: home.pzs zoom/origin line is not modified by bump"""
        init = tmp_path / "zooui" / "__init__.py"
        init.parent.mkdir(parents=True, exist_ok=True)
        init.write_text('__version__ = "0.5.2"\n', encoding="utf-8")

        pzs = tmp_path / "data" / "home.pzs"
        pzs.parent.mkdir(parents=True, exist_ok=True)
        pzs.write_text(
            "-5.0\t620.0 350.0\n"
            'StringMediaObject\tstring:62AA27:0.5.2\t5.5\t14243.0\t7920.0\n',
            encoding="utf-8",
        )

        toml = tmp_path / "pyproject.toml"
        toml.write_text('[project]\nversion = "0.5.2"\n', encoding="utf-8")

        with (
            mock.patch.object(bv, "INIT_PATH", init),
            mock.patch.object(bv, "HOME_PZS_PATH", pzs),
            mock.patch.object(bv, "PYPROJECT_PATH", toml),
        ):
            bv.bump("minor")
            content = pzs.read_text(encoding="utf-8")
            first_line = content.split("\n")[0]
            assert first_line == "-5.0\t620.0 350.0"
