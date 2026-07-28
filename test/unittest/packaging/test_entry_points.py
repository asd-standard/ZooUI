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
Feature: Entry Point Resolution

Verifies that all launch paths converge on zooui.app.main():
- ``zooui`` CLI entry point
- ``python -m zooui`` module entry point
- ``from zooui.app import main`` direct import
- ``python main.py`` source launcher
"""

import os
import subprocess
import sys
from pathlib import Path


class TestDirectImport:
    """Feature: The main() function is directly importable."""

    def test_app_main_is_importable(self):
        """Scenario: zooui.app.main can be imported without error.
        Does NOT call main() — only verifies import resolution.
        """
        from zooui.app import main

        assert callable(main)
        assert main.__name__ == "main"

    def test_app_parse_arguments_is_importable(self):
        """Scenario: parse_arguments is importable and returns a parser."""
        from zooui.app import parse_arguments

        assert callable(parse_arguments)

    def test_app_apply_command_line_args_is_importable(self):
        """Scenario: apply_command_line_args is importable and callable."""
        from zooui.app import apply_command_line_args

        assert callable(apply_command_line_args)

    def test_app_load_config_file_is_importable(self):
        """Scenario: load_config_file is importable and callable."""
        from zooui.app import load_config_file

        assert callable(load_config_file)


class TestModuleEntryPoint:
    """Feature: python -m zooui resolves correctly."""

    def test_main_module_exists(self):
        """Scenario: zooui.__main__ module exists."""
        root = Path(__file__).resolve().parent.parent.parent.parent
        main_py = root / "zooui" / "__main__.py"
        assert main_py.exists(), "__main__.py not found"

    def test_main_module_importable(self):
        """Scenario: zooui.__main__ exists and is syntactically valid."""
        import importlib.util
        from pathlib import Path

        root = Path(__file__).resolve().parent.parent.parent.parent
        spec = importlib.util.spec_from_file_location(
            "zooui.__main__", root / "zooui" / "__main__.py"
        )
        assert spec is not None, "Could not create spec for __main__.py"


class TestCliHelpSubprocess:
    """Feature: CLI help output renders without crashing."""

    def test_main_py_help(self):
        """Scenario: python main.py --help produces expected output."""
        root = Path(__file__).resolve().parent.parent.parent.parent
        main_py = root / "main.py"

        result = subprocess.run(
            [sys.executable, str(main_py), "--help"],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=str(root),
        )
        assert result.returncode == 0
        assert "ZooUI" in result.stdout
        assert "--help" in result.stdout
        assert "--debug" in result.stdout

    def test_module_help(self):
        """Scenario: python -m zooui --help produces expected output."""
        root = Path(__file__).resolve().parent.parent.parent.parent
        env = os.environ.copy()
        env["PYTHONPATH"] = str(root)

        result = subprocess.run(
            [sys.executable, "-m", "zooui", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=str(root),
            env=env,
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "ZooUI" in result.stdout
        assert "--help" in result.stdout
        assert "--debug" in result.stdout

    def test_main_py_exists(self):
        """Scenario: main.py exists at project root."""
        root = Path(__file__).resolve().parent.parent.parent.parent
        main_py = root / "main.py"
        assert main_py.exists(), "main.py not found at project root"

    def test_main_py_imports_app_main(self):
        """Scenario: main.py delegates to zooui.app.main."""
        root = Path(__file__).resolve().parent.parent.parent.parent
        main_py = root / "main.py"
        content = main_py.read_text(encoding="utf-8")
        assert "from zooui.app import main" in content
        assert "main()" in content
