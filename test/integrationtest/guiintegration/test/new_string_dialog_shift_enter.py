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

"""Step: File > Open New String Dialog with Ctrl+Enter accept after typing text."""

from __future__ import annotations

from typing import TYPE_CHECKING

from guiintegration.conf import DEFAULT_DELAY_MS, SHORT_DELAY_MS
from guiintegration.utilities.qt_simulation import trigger_action, wait
from guiintegration.utilities.scene_helpers import ensure_test_scene_loaded
from PySide6 import QtCore
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QDialog, QTextEdit

if TYPE_CHECKING:
    from guiintegration.main import GUITestContext


def run(ctx: GUITestContext) -> None:
    ctx.log.section("FILE MENU - OPEN NEW STRING DIALOG (Ctrl+Enter ACCEPT)")
    ensure_test_scene_loaded(ctx)

    def _type_text_and_accept() -> None:
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QDialog) and widget.isVisible():
                ctx.log.detail(f"Typing text and accepting: {widget.windowTitle()}")
                for child in widget.findChildren(QTextEdit):
                    QTest.keyClicks(child, "test string")
                    break
                QTest.qWait(500)
                QTest.keyClick(widget, QtCore.Qt.Key_Return, QtCore.Qt.ControlModifier)
                break

    ctx.log.action("Opening new string input dialog, typing text, accepting with Ctrl+Enter")
    QtCore.QTimer.singleShot(SHORT_DELAY_MS // 2, _type_text_and_accept)
    trigger_action(ctx, "open_media_string")
    wait(ctx, DEFAULT_DELAY_MS, "Observe: String inserted via Ctrl+Enter accept should be visible on canvas")
    ctx.log.success("New string dialog typed text and accepted with Ctrl+Enter")
