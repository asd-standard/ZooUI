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
Feature: Wheel Build Validation

End-to-end test that builds a wheel from source and verifies its
contents, metadata, and structure.  This is the closest approximation
to a PyPI publish without actually uploading.
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

import pytest


ROOT = Path(__file__).resolve().parent.parent.parent.parent
DIST = ROOT / "dist"


@pytest.fixture(scope="module")
def wheel_path():
    """Build the wheel and return its path.  Cached across tests in this module."""
    # Clean previous builds
    if DIST.exists():
        for f in DIST.glob("*.whl"):
            f.unlink()

    # Build
    result = subprocess.run(
        [sys.executable, "-m", "build", "--wheel", "--outdir", str(DIST)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Build failed:\n{result.stdout}\n{result.stderr}"

    # Find the wheel
    wheels = list(DIST.glob("zooui-*-py3-none-any.whl"))
    assert len(wheels) == 1, f"Expected 1 wheel, found {len(wheels)}"
    return wheels[0]


class TestWheelFileStructure:
    """Feature: Wheel has the correct filename and is a valid zip."""

    def test_wheel_filename_matches_convention(self, wheel_path):
        """Scenario: Wheel filename follows PEP 427 naming convention."""
        name = wheel_path.name
        assert name.startswith("zooui-")
        assert "py3-none-any.whl" in name

        # Should contain version: zooui-0.6.2-py3-none-any.whl
        m = re.match(r"zooui-(\d+\.\d+\.\d+)-py3-none-any\.whl", name)
        assert m is not None, f"Bad wheel name: {name}"

    def test_wheel_is_valid_zip(self, wheel_path):
        """Scenario: Wheel file is a valid zip archive."""
        with ZipFile(wheel_path) as zf:
            assert zf.testzip() is None, "Wheel zip is corrupted"

    def test_wheel_contains_top_level_package(self, wheel_path):
        """Scenario: Wheel contains the zooui package directory."""
        with ZipFile(wheel_path) as zf:
            names = {n.split("/")[0] for n in zf.namelist() if "/" in n}
            assert "zooui" in names, f"zooui/ not found in wheel. Found: {sorted(names)}"

    def test_wheel_contains_dist_info(self, wheel_path):
        """Scenario: Wheel contains a .dist-info directory."""
        with ZipFile(wheel_path) as zf:
            dist_infos = [n for n in zf.namelist() if ".dist-info/" in n]
            assert len(dist_infos) > 0, "No .dist-info directory in wheel"


class TestWheelRequiredEntries:
    """Feature: Critical files are present in the wheel."""

    REQUIRED = [
        "zooui/__init__.py",
        "zooui/__main__.py",
        "zooui/app.py",
        "zooui/utils/_packaging.py",
        "zooui/utils/_xdg.py",
        "zooui/data/icon.png",
        "zooui/data/home.pzs",
        "zooui/data/SVG/square.svg",
        "zooui/resources/__init__.py",
        "zooui/resources/_usage_rst.py",
    ]

    @pytest.mark.parametrize("entry", REQUIRED)
    def test_required_entry_present(self, wheel_path, entry):
        """Scenario: Required file {entry} is in the wheel."""
        with ZipFile(wheel_path) as zf:
            names = zf.namelist()
            assert entry in names, f"Missing: {entry}"

    def test_data_directory_is_populated(self, wheel_path):
        """Scenario: data/ directory contains multiple files (not empty)."""
        with ZipFile(wheel_path) as zf:
            data_entries = [n for n in zf.namelist() if n.startswith("zooui/data/") and n != "zooui/data/"]
            assert len(data_entries) >= 10, f"Only {len(data_entries)} files in data/"


class TestWheelExcludesNonPackageFiles:
    """Feature: Non-package directories are NOT in the wheel."""

    FORBIDDEN_DIRS = ["test/", "docs/", "scripts/"]

    @pytest.mark.parametrize("forbidden", FORBIDDEN_DIRS)
    def test_forbidden_dir_not_in_wheel(self, wheel_path, forbidden):
        """Scenario: {forbidden} directory is excluded from the wheel."""
        with ZipFile(wheel_path) as zf:
            for name in zf.namelist():
                assert not name.startswith(forbidden), f"Forbidden entry in wheel: {name}"

    def test_no_pycache_in_wheel(self, wheel_path):
        """Scenario: No __pycache__ directories in the wheel."""
        with ZipFile(wheel_path) as zf:
            for name in zf.namelist():
                assert "__pycache__" not in name, f"Found __pycache__ in wheel: {name}"

    def test_no_pyc_files_in_wheel(self, wheel_path):
        """Scenario: No .pyc files in the wheel."""
        with ZipFile(wheel_path) as zf:
            for name in zf.namelist():
                assert not name.endswith(".pyc"), f".pyc file in wheel: {name}"


class TestWheelMetadata:
    """Feature: Wheel metadata (METADATA, entry_points.txt) is correct."""

    def test_metadata_contains_name_and_version(self, wheel_path):
        """Scenario: METADATA file contains Name and Version fields."""
        with ZipFile(wheel_path) as zf:
            meta_entries = [n for n in zf.namelist() if n.endswith(".dist-info/METADATA")]
            assert len(meta_entries) == 1

            content = zf.read(meta_entries[0]).decode("utf-8")
            assert "Name: zooui" in content
            assert "Version:" in content

    def test_metadata_contains_classifiers(self, wheel_path):
        """Scenario: METADATA contains GPLv3 and Python classifiers."""
        with ZipFile(wheel_path) as zf:
            meta = [n for n in zf.namelist() if n.endswith(".dist-info/METADATA")][0]
            content = zf.read(meta).decode("utf-8")
            assert "License :: OSI Approved :: GNU General Public License v3 (GPLv3)" in content
            assert "Programming Language :: Python :: 3.12" in content

    def test_metadata_contains_dependencies(self, wheel_path):
        """Scenario: METADATA lists all four core dependencies (normalized names)."""
        with ZipFile(wheel_path) as zf:
            meta = [n for n in zf.namelist() if n.endswith(".dist-info/METADATA")][0]
            content = zf.read(meta).decode("utf-8")
            # hatchling normalizes package names to lowercase in Requires-Dist
            for dep in ["pyside6", "pillow", "pyvips", "platformdirs"]:
                assert f"Requires-Dist: {dep}" in content, f"Missing dependency: {dep}"

    def test_entry_points_txt_is_correct(self, wheel_path):
        """Scenario: entry_points.txt declares both zooui and zooui-gui."""
        with ZipFile(wheel_path) as zf:
            ep_file = [n for n in zf.namelist() if n.endswith(".dist-info/entry_points.txt")]
            assert len(ep_file) == 1

            content = zf.read(ep_file[0]).decode("utf-8")
            assert "zooui = zooui.app:main" in content
            assert "zooui-gui = zooui.app:main" in content
            assert "[console_scripts]" in content
            assert "[gui_scripts]" in content


class TestTwineCheck:
    """Feature: twine check passes on the built wheel."""

    def test_twine_check_passes(self, wheel_path):
        """Scenario: twine check reports no errors or warnings on the wheel."""
        # Filter out the test directory from PYTHONPATH to avoid shadowing
        # the 'packaging' PyPI library with test/unittest/packaging/.
        env = os.environ.copy()
        clean_path = [p for p in sys.path if "test" not in str(p)]
        env["PYTHONPATH"] = os.pathsep.join(clean_path)

        result = subprocess.run(
            [sys.executable, "-m", "twine", "check", str(wheel_path)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(ROOT),
            env=env,
        )
        output = result.stdout + result.stderr
        assert "PASSED" in output, f"twine check failed:\n{output}"
        assert result.returncode in (0, None), f"twine check exit code: {result.returncode}"
