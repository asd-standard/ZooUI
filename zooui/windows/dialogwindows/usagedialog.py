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

"""Usage Instructions Dialog

Provides a read-only dialog that displays the user interface instructions
from the embedded reStructuredText content.
"""

import re

from PySide6 import QtWidgets

from zooui.resources._usage_rst import USAGE_RST


class UsageDialog(QtWidgets.QDialog):
    """
    Constructor :
        UsageDialog(parent=None)
    Parameters :
        parent : Optional[QtWidgets.QWidget]
            Parent widget

    UsageDialog(parent=None) --> None

    Dialog that displays the user interface usage instructions
    from the embedded reStructuredText source.
    """

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Usage Instructions")
        self.setModal(True)
        self.resize(860, 640)

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)

        browser = QtWidgets.QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(self._load_html())

        layout.addWidget(browser)

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _load_html(self) -> str:
        rst_content = USAGE_RST

        try:
            from docutils.core import publish_parts

            parts = publish_parts(
                source=rst_content,
                writer_name="html",
                settings_overrides={
                    "output_encoding": "unicode",
                },
            )
            html = str(parts["html_body"])
        except ImportError:
            return f"<pre>{rst_content}</pre>"

        # Strip the first <img> tag (home.png screenshot reference)
        html = re.sub(r"^.*?<img[^>]*>", "", html, count=1, flags=re.DOTALL)

        return html
