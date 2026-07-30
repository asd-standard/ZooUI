## ZooUI - Zooming User Interface
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

"""Unit tests for OpenNewStringInputDialog with initial_text support."""

from unittest.mock import Mock, patch

import pytest
from PySide6 import QtWidgets


class TestOpenNewStringInputDialog:
    """
    Feature: OpenNewStringInputDialog with OCR initial_text

    The dialog accepts an optional initial_text parameter to pre-fill
    the text edit widget, used by the OCR screenshot feature to seed
    the dialog with tesseract output.
    """

    @pytest.fixture(scope="class")
    def qapp(self):
        app = QtWidgets.QApplication.instance()
        if app is None:
            app = QtWidgets.QApplication([])
        yield app

    def test_init_without_initial_text(self, qapp):
        """
        Scenario: Default constructor has empty initial_text

        Given an OpenNewStringInputDialog created with no arguments
        Then _initial_text should be an empty string
        """
        from zooui.windows.dialogwindows.stringinputdialog import (
            OpenNewStringInputDialog,
        )

        dialog = OpenNewStringInputDialog()
        assert dialog._initial_text == ""

    def test_init_with_initial_text(self, qapp):
        """
        Scenario: Constructor stores initial_text parameter

        Given a dialog created with initial_text="hello world"
        Then _initial_text should be "hello world"
        """
        from zooui.windows.dialogwindows.stringinputdialog import (
            OpenNewStringInputDialog,
        )

        dialog = OpenNewStringInputDialog(initial_text="hello world")
        assert dialog._initial_text == "hello world"

    def test_init_with_multiline_initial_text(self, qapp):
        """
        Scenario: Constructor handles multiline initial_text

        Given a dialog created with multiline initial_text
        Then _initial_text should preserve newlines
        """
        from zooui.windows.dialogwindows.stringinputdialog import (
            OpenNewStringInputDialog,
        )

        text = "line one\nline two\nline three"
        dialog = OpenNewStringInputDialog(initial_text=text)
        assert dialog._initial_text == text
        assert "\n" in dialog._initial_text

    def test_main_dialog_prefills_text_edit(self, qapp):
        """
        Scenario: _main_dialog pre-fills text_edit with initial_text

        Given a dialog with initial_text="prefilled content"
        When _main_dialog is called
        Then the text_edit should contain "prefilled content"
        """
        from zooui.windows.dialogwindows.stringinputdialog import (
            OpenNewStringInputDialog,
        )

        dialog = OpenNewStringInputDialog(initial_text="prefilled content")
        qt_dialog = dialog._main_dialog()
        assert dialog.text_edit.toPlainText() == "prefilled content"

    def test_main_dialog_no_prefill_when_empty(self, qapp):
        """
        Scenario: _main_dialog does not pre-fill when initial_text is empty

        Given a dialog with initial_text=""
        When _main_dialog is called
        Then the text_edit should be empty
        """
        from zooui.windows.dialogwindows.stringinputdialog import (
            OpenNewStringInputDialog,
        )

        dialog = OpenNewStringInputDialog(initial_text="")
        qt_dialog = dialog._main_dialog()
        assert dialog.text_edit.toPlainText() == ""

    def test_run_dialog_accepted_with_initial_text(self, qapp):
        """
        Scenario: _run_dialog returns URI with pre-filled text on accept

        Given a dialog with initial_text="ocr result"
        When the dialog is accepted
        Then the returned URI should contain "ocr result"
        """
        from zooui.windows.dialogwindows.stringinputdialog import (
            OpenNewStringInputDialog,
        )

        dialog = OpenNewStringInputDialog(initial_text="ocr result")
        with patch.object(dialog.__class__, "_main_dialog") as mock_main_dialog:
            mock_qt_dialog = Mock()
            mock_qt_dialog.exec.return_value = QtWidgets.QDialog.Accepted
            mock_main_dialog.return_value = mock_qt_dialog

            dialog.string_color = "ff0000"
            dialog.text_edit = Mock()
            dialog.text_edit.toPlainText.return_value = "ocr result"

            result = dialog._run_dialog()
            assert result == (True, "string:ff0000:ocr result")

    def test_run_dialog_rejected(self, qapp):
        """
        Scenario: _run_dialog returns (False, "") when cancelled

        Given a dialog with initial_text
        When the dialog is rejected
        Then the result should be (False, "")
        """
        from zooui.windows.dialogwindows.stringinputdialog import (
            OpenNewStringInputDialog,
        )

        dialog = OpenNewStringInputDialog(initial_text="some text")
        with patch.object(dialog.__class__, "_main_dialog") as mock_main_dialog:
            mock_qt_dialog = Mock()
            mock_qt_dialog.exec.return_value = QtWidgets.QDialog.Rejected
            mock_main_dialog.return_value = mock_qt_dialog

            result = dialog._run_dialog()
            assert result == (False, "")

    def test_run_dialog_accepted_with_modified_text(self, qapp):
        """
        Scenario: _run_dialog captures user-edited text, not initial_text

        Given a dialog with initial_text="initial"
        And the user edits the text to "modified"
        When the dialog is accepted
        Then the URI should contain "modified"
        """
        from zooui.windows.dialogwindows.stringinputdialog import (
            OpenNewStringInputDialog,
        )

        dialog = OpenNewStringInputDialog(initial_text="initial")
        with patch.object(dialog.__class__, "_main_dialog") as mock_main_dialog:
            mock_qt_dialog = Mock()
            mock_qt_dialog.exec.return_value = QtWidgets.QDialog.Accepted
            mock_main_dialog.return_value = mock_qt_dialog

            dialog.string_color = "00ff00"
            dialog.text_edit = Mock()
            dialog.text_edit.toPlainText.return_value = "modified"

            result = dialog._run_dialog()
            assert result == (True, "string:00ff00:modified")
