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
Feature: Usage Instructions Dialog

Provides a read-only dialog that displays the user interface usage
instructions from the reStructuredText documentation file.
"""

from pathlib import Path
from unittest.mock import patch

from zooui.windows.dialogwindows.usagedialog import UsageDialog


class TestUsageDialog:
    """
    Feature: Usage Dialog Operations

    The UsageDialog reads the user interface RST documentation, converts
    it to HTML via docutils, and displays it in a QTextBrowser.
    """

    def test_rst_path_resolves_to_existing_file(self):
        """
        Scenario: RST path resolves to an existing file

        Given the UsageDialog class constant
        When _RST_PATH is resolved
        Then it should point to an existing .rst file
        """
        assert Path(UsageDialog._RST_PATH).exists()
        assert Path(UsageDialog._RST_PATH).suffix == ".rst"

    def test_load_html_returns_html_content(self):
        """
        Scenario: Load HTML content from the RST file

        Given the RST file exists and docutils is available
        When _load_html() is called
        Then it should return a non-empty HTML string
        """
        dialog = UsageDialog.__new__(UsageDialog)
        html = dialog._load_html()

        assert isinstance(html, str)
        assert len(html) > 0
        assert "<h" in html or "<li>" in html or "<p>" in html

    def test_load_html_strips_header_and_image(self):
        """
        Scenario: HTML output has heading and image stripped

        Given the RST file is converted to HTML
        When _load_html() is called
        Then the output should start with menu actions, not the header or image
        """
        dialog = UsageDialog.__new__(UsageDialog)
        html = dialog._load_html()

        assert "User Interface" not in html or html.strip().startswith(
            '<div class="section" id="the-menus-provide-the-following-actions">'
        )
        assert "<img " not in html

    def test_load_html_file_not_found(self):
        """
        Scenario: RST file is missing

        Given the RST file does not exist at the expected path
        When _load_html() is called
        Then it should return a file-not-found message
        """
        dialog = UsageDialog.__new__(UsageDialog)

        with patch.object(dialog, "_RST_PATH", "/nonexistent/path/file.rst"):
            html = dialog._load_html()

        assert html == "<p>Usage instructions file not found.</p>"

    def test_load_html_docutils_unavailable(self):
        """
        Scenario: docutils is not installed

        Given the RST file exists but docutils cannot be imported
        When _load_html() is called
        Then it should return raw RST content wrapped in <pre> tags
        """
        dialog = UsageDialog.__new__(UsageDialog)

        rst_mock = "Sample RST content"
        with (
            patch.object(Path, "read_text", return_value=rst_mock),
            patch("builtins.__import__", side_effect=ImportError("docutils missing")),
        ):
            html = dialog._load_html()

        assert html == f"<pre>{rst_mock}</pre>"

    def test_load_html_resolves_relative_image_src(self):
        """
        Scenario: Relative src paths are resolved to absolute paths

        Given docutils outputs HTML containing a relative src attribute
        When _load_html() processes the HTML
        Then relative src paths should be resolved to absolute file paths
        """
        dialog = UsageDialog.__new__(UsageDialog)

        fake_rst = "Some RST content"
        fake_rst_path = str(Path(__file__).parent / "test.rst")
        mock_html = '<p>Section.</p>\n<source src="relative/path/test.png" />\n<p>Text.</p>'

        with (
            patch.object(Path, "read_text", return_value=fake_rst),
            patch.object(UsageDialog, "_RST_PATH", fake_rst_path),
            patch("docutils.core.publish_parts", return_value={"html_body": mock_html}),
        ):
            html = dialog._load_html()

        assert 'src="relative/path/test.png"' not in html
        assert 'src="' + str(Path(fake_rst_path).parent / "relative/path/test.png") + '"' in html
