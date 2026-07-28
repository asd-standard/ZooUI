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
Feature: Package Metadata Validation

The pyproject.toml file defines the project metadata, dependencies,
build system, and entry points required for PyPI publication.
"""

import os
import tomllib
from pathlib import Path

import pytest

import zooui


@pytest.fixture(scope="module")
def pyproject_data():
    """Load pyproject.toml from the project root."""
    root = Path(__file__).resolve().parent.parent.parent.parent
    path = root / "pyproject.toml"
    assert path.exists(), f"pyproject.toml not found at {path}"
    with open(path, "rb") as f:
        return tomllib.load(f)


class TestBuildSystem:
    """Feature: Build system configuration."""

    def test_build_backend_is_hatchling(self, pyproject_data):
        """Scenario: Build backend is hatchling."""
        bs = pyproject_data["build-system"]
        assert bs["build-backend"] == "hatchling.build"
        assert "hatchling" in bs["requires"]

    def test_build_system_requires_hatchling(self, pyproject_data):
        """Scenario: Build system requires hatchling."""
        assert "hatchling" in pyproject_data["build-system"]["requires"]


class TestProjectMetadata:
    """Feature: Project metadata completeness."""

    def test_name_is_zooui(self, pyproject_data):
        """Scenario: Project name is zooui."""
        assert pyproject_data["project"]["name"] == "zooui"

    def test_version_matches_package(self, pyproject_data):
        """Scenario: pyproject.toml version matches zooui.__version__."""
        assert pyproject_data["project"]["version"] == zooui.__version__

    def test_requires_python(self, pyproject_data):
        """Scenario: Python version requirement is set."""
        assert pyproject_data["project"]["requires-python"] == ">=3.12"

    def test_description_present(self, pyproject_data):
        """Scenario: Description is present and non-empty."""
        desc = pyproject_data["project"]["description"]
        assert isinstance(desc, str)
        assert len(desc) > 0

    def test_readme_points_to_file(self, pyproject_data):
        """Scenario: README file reference is valid."""
        readme = pyproject_data["project"]["readme"]
        root = Path(__file__).resolve().parent.parent.parent.parent
        assert (root / readme).exists(), f"{readme} not found"

    def test_license_is_gplv3(self, pyproject_data):
        """Scenario: License is GPL-3.0-or-later."""
        lic = pyproject_data["project"]["license"]
        assert "GPL-3.0" in lic.get("text", "") or "GPL-3.0" in str(lic)

    def test_authors_populated(self, pyproject_data):
        """Scenario: Authors list is non-empty."""
        authors = pyproject_data["project"]["authors"]
        assert len(authors) > 0
        assert "name" in authors[0]

    def test_classifiers_present(self, pyproject_data):
        """Scenario: Classifiers list is present and includes required entries."""
        classifiers = pyproject_data["project"]["classifiers"]
        required = [
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Programming Language :: Python :: 3.12",
        ]
        for r in required:
            assert r in classifiers, f"Missing classifier: {r}"

    def test_keywords_present(self, pyproject_data):
        """Scenario: Keywords list is non-empty."""
        kw = pyproject_data["project"]["keywords"]
        assert len(kw) > 0

    def test_urls_present(self, pyproject_data):
        """Scenario: Project URLs include Homepage and Repository."""
        urls = pyproject_data["project"]["urls"]
        assert "Homepage" in urls
        assert "Repository" in urls


class TestDependencies:
    """Feature: Dependency declarations."""

    def test_all_required_deps_present(self, pyproject_data):
        """Scenario: All four core dependencies are declared."""
        deps = pyproject_data["project"]["dependencies"]
        dep_names = [d.split(">=")[0] for d in deps]
        assert "PySide6" in dep_names
        assert "Pillow" in dep_names
        assert "pyvips" in dep_names
        assert "platformdirs" in dep_names

    def test_dependencies_have_version_pins(self, pyproject_data):
        """Scenario: All dependencies have minimum version pins."""
        for dep in pyproject_data["project"]["dependencies"]:
            assert ">=" in dep, f"Dependency '{dep}' is missing version pin"

    def test_platformdirs_version_min_3(self, pyproject_data):
        """Scenario: platformdirs requires at least version 3."""
        for dep in pyproject_data["project"]["dependencies"]:
            if dep.startswith("platformdirs"):
                assert ">=3" in dep


class TestEntryPoints:
    """Feature: Console script and GUI script entry points."""

    def test_scripts_zooui_present(self, pyproject_data):
        """Scenario: zooui console script is declared."""
        scripts = pyproject_data["project"]["scripts"]
        assert "zooui" in scripts
        assert scripts["zooui"] == "zooui.app:main"

    def test_gui_scripts_zooui_gui_present(self, pyproject_data):
        """Scenario: zooui-gui GUI script is declared."""
        gui = pyproject_data["project"]["gui-scripts"]
        assert "zooui-gui" in gui
        assert gui["zooui-gui"] == "zooui.app:main"

    def test_entry_points_point_to_app_py(self, pyproject_data):
        """Feature: Entry points reference zooui.app:main."""
        assert pyproject_data["project"]["scripts"]["zooui"] == "zooui.app:main"
        assert pyproject_data["project"]["gui-scripts"]["zooui-gui"] == "zooui.app:main"


class TestManifest:
    """Feature: MANIFEST.in and project files."""

    def test_manifest_in_exists(self):
        """Scenario: MANIFEST.in exists in project root."""
        root = Path(__file__).resolve().parent.parent.parent.parent
        manifest = root / "MANIFEST.in"
        assert manifest.exists(), "MANIFEST.in not found"

    def test_manifest_includes_zooui(self):
        """Scenario: MANIFEST.in grafts the zooui package."""
        root = Path(__file__).resolve().parent.parent.parent.parent
        manifest = root / "MANIFEST.in"
        content = manifest.read_text(encoding="utf-8")
        assert "zooui" in content

    def test_manifest_excludes_pycache(self):
        """Scenario: MANIFEST.in excludes __pycache__ and .pyc."""
        root = Path(__file__).resolve().parent.parent.parent.parent
        manifest = root / "MANIFEST.in"
        content = manifest.read_text(encoding="utf-8")
        assert "__pycache__" in content
        assert "*.pyc" in content

    def test_license_file_exists(self):
        """Scenario: LICENSE file exists."""
        root = Path(__file__).resolve().parent.parent.parent.parent
        assert (root / "LICENSE").exists(), "LICENSE not found"

    def test_readme_not_empty(self):
        """Scenario: README.md is non-empty."""
        root = Path(__file__).resolve().parent.parent.parent.parent
        readme = root / "README.md"
        assert readme.exists(), "README.md not found"
        assert len(readme.read_text(encoding="utf-8")) > 100
