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
instructions from the embedded reStructuredText content.
"""

from unittest.mock import patch

from zooui.windows.dialogwindows.usagedialog import UsageDialog


class TestUsageDialog:
    """
    Feature: Usage Dialog Operations

    The UsageDialog loads the embedded RST content, converts it to HTML
    via docutils, and displays it in a QTextBrowser.
    """

    def test_usage_rst_is_non_empty_string(self):
        """
        Scenario: Embedded usage RST is available

        Given the USAGE_RST module constant
        When it is imported
        Then it should be a non-empty string
        """
        from zooui.resources._usage_rst import USAGE_RST

        assert isinstance(USAGE_RST, str)
        assert len(USAGE_RST) > 0
        assert "User Interface" in USAGE_RST

    def test_load_html_returns_html_content(self):
        """
        Scenario: Load HTML content from embedded RST

        Given the embedded RST content and docutils is available
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

        Given the embedded RST is converted to HTML
        When _load_html() is called
        Then the output should start with menu actions, not the header or image
        """
        dialog = UsageDialog.__new__(UsageDialog)
        html = dialog._load_html()

        assert "User Interface" not in html or html.strip().startswith(
            '<div class="section" id="the-menus-provide-the-following-actions">'
        )
        assert "<img " not in html

    def test_load_html_docutils_unavailable(self):
        """
        Scenario: docutils is not installed

        Given the embedded RST but docutils cannot be imported
        When _load_html() is called
        Then it should return raw RST content wrapped in <pre> tags
        """
        dialog = UsageDialog.__new__(UsageDialog)

        with patch("builtins.__import__", side_effect=ImportError("docutils missing")):
            html = dialog._load_html()

        assert html.startswith("<pre>")
        assert html.endswith("</pre>")
