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
Feature: Bundled Data and Resource Path Resolution

Verifies that all package data, bundled resources, and XDG paths
resolve correctly regardless of installation mode (source, pip, frozen).
"""

import os
from pathlib import Path


class TestPackagedDataFiles:
    """Feature: Critical data files are bundled in the package."""

    def test_data_dir_is_valid_path(self):
        """Scenario: data_dir() returns an existing directory."""
        from zooui.utils._packaging import data_dir

        d = data_dir()
        assert os.path.isdir(d), f"data_dir() is not a directory: {d}"

    def test_icon_exists(self):
        """Scenario: icon.png is bundled and accessible."""
        from zooui.utils._packaging import data_dir

        icon = os.path.join(data_dir(), "data", "icon.png")
        assert os.path.isfile(icon), f"icon.png not found at {icon}"

    def test_home_pzs_exists(self):
        """Scenario: home.pzs is bundled and accessible."""
        from zooui.utils._packaging import data_dir

        home = os.path.join(data_dir(), "data", "home.pzs")
        assert os.path.isfile(home), f"home.pzs not found at {home}"

    def test_svg_directory_is_present(self):
        """Scenario: SVG directory exists and contains shapes."""
        from zooui.utils._packaging import data_dir

        svg_dir = os.path.join(data_dir(), "data", "SVG")
        assert os.path.isdir(svg_dir), f"SVG directory not found at {svg_dir}"

        svg_files = [f for f in os.listdir(svg_dir) if f.endswith(".svg")]
        assert len(svg_files) > 0, "No SVG files found"

    def test_all_numbered_images_present(self):
        """Scenario: All numbered test images are bundled."""
        from zooui.utils._packaging import data_dir

        for i in range(1, 8):
            name = f"{i:02d}"
            found = False
            for ext in (".png", ".jpg", ".jpeg"):
                path = os.path.join(data_dir(), "data", name + "_" + ext)
                path = os.path.join(data_dir(), "data", f"{name}*")
            # Direct check for known filenames
            data_path = os.path.join(data_dir(), "data")
            for fname in os.listdir(data_path):
                if fname.startswith(name + "_"):
                    found = True
                    break
            assert found, f"No image for index {name} found in data directory"


class TestEmbeddedResources:
    """Feature: Embedded resource modules are present and valid."""

    def test_usage_rst_string_is_non_empty(self):
        """Scenario: Embedded usage RST is a valid non-empty string."""
        from zooui.resources._usage_rst import USAGE_RST

        assert isinstance(USAGE_RST, str)
        assert len(USAGE_RST) > 500, f"USAGE_RST is too short ({len(USAGE_RST)} chars)"
        assert "User Interface" in USAGE_RST
        assert "File menu" in USAGE_RST

    def test_usage_rst_has_no_sphinx_only_roles(self):
        """Scenario: Embedded RST contains no Sphinx-only roles."""
        from zooui.resources._usage_rst import USAGE_RST

        assert ":kbd:" not in USAGE_RST, "Sphinx-only :kbd: role in embedded RST"
        assert ":file:" not in USAGE_RST, "Sphinx-only :file: role in embedded RST"
        assert ":doc:" not in USAGE_RST, "Sphinx-only :doc: role in embedded RST"
        assert ":ref:" not in USAGE_RST, "Sphinx-only :ref: role in embedded RST"

    def test_resources_package_exists(self):
        """Scenario: zooui.resources package is a proper package."""
        from zooui.utils._packaging import data_dir

        res = Path(data_dir()) / "resources"
        assert res.is_dir(), "resources directory not found"
        init = res / "__init__.py"
        assert init.is_file(), "resources/__init__.py not found"
        rst = res / "_usage_rst.py"
        assert rst.is_file(), "resources/_usage_rst.py not found"


class TestXdgPaths:
    """Feature: XDG path resolution returns valid paths."""

    def test_get_config_file_returns_path(self):
        """Scenario: get_config_file returns a Path ending in config.json."""
        from zooui.utils._xdg import get_config_file

        p = get_config_file()
        assert p.name == "config.json"

    def test_get_data_dir_returns_path(self):
        """Scenario: get_data_dir returns a Path."""
        from zooui.utils._xdg import get_data_dir

        p = get_data_dir()
        assert isinstance(p, Path)

    def test_get_cache_dir_returns_path(self):
        """Scenario: get_cache_dir returns a Path."""
        from zooui.utils._xdg import get_cache_dir

        p = get_cache_dir()
        assert isinstance(p, Path)

    def test_get_state_dir_returns_path(self):
        """Scenario: get_state_dir returns a Path."""
        from zooui.utils._xdg import get_state_dir

        p = get_state_dir()
        assert isinstance(p, Path)

    def test_get_colorstore_dir_returns_path(self):
        """Scenario: get_colorstore_dir is a subdirectory of get_data_dir."""
        from zooui.utils._xdg import get_colorstore_dir, get_data_dir

        color = get_colorstore_dir()
        data = get_data_dir()
        assert color.name == "colorstore"
        assert str(data) in str(color)

    def test_all_xdg_paths_are_absolute(self):
        """Scenario: All XDG paths are absolute."""
        from zooui.utils._xdg import get_cache_dir, get_colorstore_dir, get_config_file, get_data_dir, get_state_dir

        for func in [get_config_file, get_data_dir, get_cache_dir, get_state_dir, get_colorstore_dir]:
            p = func()
            assert p.is_absolute(), f"{func.__name__} returned relative path: {p}"
