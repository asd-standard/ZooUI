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

"""Unit tests for QZUI OCR screenshot selection mode."""

from unittest.mock import MagicMock, patch

import pytest
from PySide6 import QtCore, QtGui, QtWidgets

from zooui.objects.scene.qzui import QZUI


def _mouse_event(event_type, pos, button, buttons, modifiers=QtCore.Qt.NoModifier):
    """Construct a non-deprecated QMouseEvent with globalPos and device."""
    return QtGui.QMouseEvent(
        event_type,
        QtCore.QPointF(pos[0], pos[1]),
        QtCore.QPointF(pos[0], pos[1]),
        button,
        buttons,
        modifiers,
        QtGui.QPointingDevice.primaryPointingDevice(),
    )


class TestQZUIOcrMode:
    """
    Feature: OCR Screenshot Selection Mode

    The QZUI widget supports an OCR screenshot selection mode activated
    by a keyboard shortcut. In this mode the cursor changes to crosshair,
    a blue rectangle is drawn during drag-selection, and on mouse release
    the selected region is captured and emitted as a signal.
    """

    @pytest.fixture(scope="class")
    def qapp(self):
        app = QtWidgets.QApplication.instance()
        if app is None:
            app = QtWidgets.QApplication([])
        yield app

    @pytest.fixture
    def mock_scene(self):
        scene = MagicMock()
        scene.origin = (0.0, 0.0)
        scene.zoomlevel = 0.0
        scene.selection = None
        scene.render.return_value = []
        scene.check_and_clear_repaint_flag.return_value = False
        return scene

    @pytest.fixture
    def qzui(self, qapp, mock_scene):
        with patch("zooui.objects.scene.scene.new", return_value=mock_scene):
            zui = QZUI(framerate=0)
            zui.resize(400, 300)
            return zui

    def test_set_ocr_mode_enables_state(self, qzui):
        """
        Scenario: Enable OCR mode sets internal state

        Given a QZUI instance with OCR mode disabled
        When set_ocr_mode(True) is called
        Then is_ocr_mode should return True
        """
        assert not qzui.is_ocr_mode()
        qzui.set_ocr_mode(True)
        assert qzui.is_ocr_mode()

    def test_set_ocr_mode_disables_state(self, qzui):
        """
        Scenario: Disable OCR mode clears internal state

        Given a QZUI instance with OCR mode enabled
        When set_ocr_mode(False) is called
        Then is_ocr_mode should return False
        """
        qzui.set_ocr_mode(True)
        qzui.set_ocr_mode(False)
        assert not qzui.is_ocr_mode()

    def test_set_ocr_mode_changes_cursor_to_crosshair(self, qzui):
        """
        Scenario: OCR mode sets crosshair cursor

        Given a QZUI instance
        When set_ocr_mode(True) is called
        Then the cursor should be CrossCursor
        """
        qzui.set_ocr_mode(True)
        assert qzui.cursor().shape() == QtCore.Qt.CursorShape.CrossCursor

    def test_set_ocr_mode_restores_default_cursor(self, qzui):
        """
        Scenario: Exiting OCR mode restores default cursor

        Given a QZUI in OCR mode with crosshair cursor
        When set_ocr_mode(False) is called
        Then the cursor should revert to ArrowCursor
        """
        qzui.set_ocr_mode(True)
        qzui.set_ocr_mode(False)
        assert qzui.cursor().shape() == QtCore.Qt.CursorShape.ArrowCursor

    def test_mouse_press_in_ocr_mode_starts_rect(self, qzui, mock_scene):
        """
        Scenario: Mouse press in OCR mode begins rectangle drawing

        Given a QZUI in OCR mode
        When a left mouse press occurs at (50, 60)
        Then drawing_rect should be True and rect_start/rect_end set
        """
        qzui.set_ocr_mode(True)
        event = _mouse_event(
            QtCore.QEvent.MouseButtonPress, (50, 60),
            QtCore.Qt.LeftButton, QtCore.Qt.LeftButton,
        )
        qzui.mousePressEvent(event)
        assert qzui._QZUI__mouse_left_down
        assert qzui._QZUI__drawing_rect
        assert qzui._QZUI__rect_start == (50, 60)
        assert qzui._QZUI__rect_end == (50, 60)

    def test_mouse_move_in_ocr_mode_updates_rect(self, qzui, mock_scene):
        """
        Scenario: Mouse move in OCR mode updates rectangle end

        Given a QZUI in OCR mode with an active drag
        When the mouse moves to (200, 150)
        Then rect_end should be updated
        """
        qzui.set_ocr_mode(True)
        press = _mouse_event(
            QtCore.QEvent.MouseButtonPress, (50, 60),
            QtCore.Qt.LeftButton, QtCore.Qt.LeftButton,
        )
        qzui.mousePressEvent(press)
        move = _mouse_event(
            QtCore.QEvent.MouseMove, (200, 150),
            QtCore.Qt.NoButton, QtCore.Qt.LeftButton,
        )
        qzui.mouseMoveEvent(move)
        assert qzui._QZUI__rect_end == (200, 150)

    def test_mouse_release_in_ocr_mode_emits_signal(self, qzui, mock_scene):
        """
        Scenario: Mouse release in OCR mode emits region signal

        Given a QZUI in OCR mode with a dragged rectangle
        When the left mouse button is released
        Then the ocr_region_selected signal should be emitted with a QImage
        And OCR mode should be disabled
        """
        qzui.set_ocr_mode(True)
        press = _mouse_event(
            QtCore.QEvent.MouseButtonPress, (10, 10),
            QtCore.Qt.LeftButton, QtCore.Qt.LeftButton,
        )
        qzui.mousePressEvent(press)
        move = _mouse_event(
            QtCore.QEvent.MouseMove, (100, 80),
            QtCore.Qt.NoButton, QtCore.Qt.LeftButton,
        )
        qzui.mouseMoveEvent(move)

        mock_handler = MagicMock()
        qzui.ocr_region_selected.connect(mock_handler)

        release = _mouse_event(
            QtCore.QEvent.MouseButtonRelease, (100, 80),
            QtCore.Qt.LeftButton, QtCore.Qt.LeftButton,
        )
        qzui.mouseReleaseEvent(release)
        QtWidgets.QApplication.processEvents()

        mock_handler.assert_called_once()
        captured = mock_handler.call_args[0][0]
        assert isinstance(captured, QtGui.QImage)
        assert not qzui.is_ocr_mode()

    def test_mouse_release_zero_width_rect_no_signal(self, qzui, mock_scene):
        """
        Scenario: Zero-width rectangle does not emit signal

        Given a QZUI in OCR mode with a degenerate (zero-width) rectangle
        When the left mouse button is released
        Then the ocr_region_selected signal should NOT be emitted
        And OCR mode should still be disabled
        """
        qzui.set_ocr_mode(True)
        press = _mouse_event(
            QtCore.QEvent.MouseButtonPress, (50, 10),
            QtCore.Qt.LeftButton, QtCore.Qt.LeftButton,
        )
        qzui.mousePressEvent(press)
        move = _mouse_event(
            QtCore.QEvent.MouseMove, (50, 80),
            QtCore.Qt.NoButton, QtCore.Qt.LeftButton,
        )
        qzui.mouseMoveEvent(move)

        mock_handler = MagicMock()
        qzui.ocr_region_selected.connect(mock_handler)

        release = _mouse_event(
            QtCore.QEvent.MouseButtonRelease, (50, 80),
            QtCore.Qt.LeftButton, QtCore.Qt.LeftButton,
        )
        qzui.mouseReleaseEvent(release)

        mock_handler.assert_not_called()
        assert not qzui.is_ocr_mode()

    def test_mouse_release_zero_height_rect_no_signal(self, qzui, mock_scene):
        """
        Scenario: Zero-height rectangle does not emit signal

        Given a QZUI in OCR mode with a degenerate (zero-height) rectangle
        When the left mouse button is released
        Then the ocr_region_selected signal should NOT be emitted
        """
        qzui.set_ocr_mode(True)
        press = _mouse_event(
            QtCore.QEvent.MouseButtonPress, (10, 50),
            QtCore.Qt.LeftButton, QtCore.Qt.LeftButton,
        )
        qzui.mousePressEvent(press)
        move = _mouse_event(
            QtCore.QEvent.MouseMove, (100, 50),
            QtCore.Qt.NoButton, QtCore.Qt.LeftButton,
        )
        qzui.mouseMoveEvent(move)

        mock_handler = MagicMock()
        qzui.ocr_region_selected.connect(mock_handler)

        release = _mouse_event(
            QtCore.QEvent.MouseButtonRelease, (100, 50),
            QtCore.Qt.LeftButton, QtCore.Qt.LeftButton,
        )
        qzui.mouseReleaseEvent(release)

        mock_handler.assert_not_called()
        assert not qzui.is_ocr_mode()

    def test_escape_in_ocr_mode_cancels(self, qzui, mock_scene):
        """
        Scenario: Escape key cancels OCR mode

        Given a QZUI in OCR mode
        When the Escape key is pressed
        Then OCR mode should be disabled
        And scene.selection should NOT be modified
        """
        qzui.set_ocr_mode(True)
        mock_scene.selection = MagicMock()
        event = QtGui.QKeyEvent(
            QtCore.QEvent.KeyPress,
            QtCore.Qt.Key_Escape,
            QtCore.Qt.NoModifier,
        )
        qzui.keyPressEvent(event)
        assert not qzui.is_ocr_mode()
        assert mock_scene.selection is not None

    def test_escape_not_in_ocr_mode_deselects(self, qzui, mock_scene):
        """
        Scenario: Escape when not in OCR mode still deselects

        Given a QZUI with OCR mode disabled and an active selection
        When the Escape key is pressed
        Then the selection should be cleared
        """
        mock_scene.selection = MagicMock()
        event = QtGui.QKeyEvent(
            QtCore.QEvent.KeyPress,
            QtCore.Qt.Key_Escape,
            QtCore.Qt.NoModifier,
        )
        qzui.keyPressEvent(event)
        assert mock_scene.selection is None

    def test_paint_event_ocr_blue_rect(self, qzui, mock_scene, qapp):
        """
        Scenario: Paint event draws blue rectangle in OCR mode

        Given a QZUI in OCR mode with an active drag rectangle
        When paintEvent is triggered
        Then action_draw_rect should be called with Qt.blue
        """
        qzui.set_ocr_mode(True)
        qzui._QZUI__drawing_rect = True
        qzui._QZUI__rect_start = (10, 10)
        qzui._QZUI__rect_end = (100, 80)
        mock_painter = MagicMock()
        with patch("zooui.objects.scene.qzui.QtGui.QPainter", return_value=mock_painter):
            qzui.paintEvent(QtGui.QPaintEvent(qzui.rect()))
        mock_scene.action_draw_rect.assert_called()
        args = mock_scene.action_draw_rect.call_args
        assert args[0][3] == QtCore.Qt.blue

    def test_paint_event_normal_green_rect(self, qzui, mock_scene, qapp):
        """
        Scenario: Paint event draws green rectangle when not in OCR mode

        Given a QZUI NOT in OCR mode with an active drag rectangle (Ctrl+Click)
        When paintEvent is triggered
        Then action_draw_rect should be called with Qt.green
        """
        qzui._QZUI__drawing_rect = True
        qzui._QZUI__rect_start = (10, 10)
        qzui._QZUI__rect_end = (100, 80)
        mock_painter = MagicMock()
        with patch("zooui.objects.scene.qzui.QtGui.QPainter", return_value=mock_painter):
            qzui.paintEvent(QtGui.QPaintEvent(qzui.rect()))
        mock_scene.action_draw_rect.assert_called()
        args = mock_scene.action_draw_rect.call_args
        assert args[0][3] == QtCore.Qt.green

    def test_ctrl_click_multiselect_still_works(self, qzui, mock_scene):
        """
        Scenario: Ctrl+Click multi-select still works when OCR mode is off

        Given a QZUI with OCR mode disabled and Ctrl held
        When Ctrl+LeftClick is pressed on an object
        Then rectangle drawing for multi-select should begin
        """
        qzui._QZUI__control_held = True
        press = _mouse_event(
            QtCore.QEvent.MouseButtonPress, (50, 50),
            QtCore.Qt.LeftButton, QtCore.Qt.LeftButton,
        )
        qzui.mousePressEvent(press)
        assert qzui._QZUI__drawing_rect
        assert qzui._QZUI__rect_start == (50, 50)

    def test_ocr_mode_does_not_interfere_with_right_click(self, qzui, mock_scene):
        """
        Scenario: Right-click selection still works in OCR mode

        Given a QZUI in OCR mode
        When a right mouse button press occurs
        Then right_selection should be set on the scene
        """
        qzui.set_ocr_mode(True)
        mock_obj = MagicMock()
        mock_scene.get.return_value = mock_obj
        event = _mouse_event(
            QtCore.QEvent.MouseButtonPress, (200, 200),
            QtCore.Qt.RightButton, QtCore.Qt.RightButton,
        )
        qzui.mousePressEvent(event)
        mock_scene.get.assert_called_with((200, 200))

    def test_mouse_release_in_ocr_mode_uses_qwidget_grab(self, qzui, mock_scene):
        """
        Scenario: Mouse release captures child pixel data

        Given a QZUI in OCR mode with a selected rectangle
        When the mouse button is released
        Then QWidget.grab() should be called and the resulting QImage
        should match the selected rectangle dimensions
        """
        qzui.set_ocr_mode(True)
        press = _mouse_event(
            QtCore.QEvent.MouseButtonPress, (30, 20),
            QtCore.Qt.LeftButton, QtCore.Qt.LeftButton,
        )
        qzui.mousePressEvent(press)
        move = _mouse_event(
            QtCore.QEvent.MouseMove, (130, 120),
            QtCore.Qt.NoButton, QtCore.Qt.LeftButton,
        )
        qzui.mouseMoveEvent(move)

        mock_handler = MagicMock()
        qzui.ocr_region_selected.connect(mock_handler)

        release = _mouse_event(
            QtCore.QEvent.MouseButtonRelease, (130, 120),
            QtCore.Qt.LeftButton, QtCore.Qt.LeftButton,
        )
        qzui.mouseReleaseEvent(release)
        QtWidgets.QApplication.processEvents()

        mock_handler.assert_called_once()
        captured = mock_handler.call_args[0][0]
        assert captured.width() == 100
        assert captured.height() == 100

    def test_mouse_release_supports_sw_drag_direction(self, qzui, mock_scene):
        """
        Scenario: Drag from bottom-right to top-left still works

        Given a QZUI in OCR mode
        When the mouse is dragged from bottom-right to top-left
        Then the ocr_region_selected signal should capture the correct area
        """
        qzui.set_ocr_mode(True)
        press = _mouse_event(
            QtCore.QEvent.MouseButtonPress, (150, 120),
            QtCore.Qt.LeftButton, QtCore.Qt.LeftButton,
        )
        qzui.mousePressEvent(press)
        move = _mouse_event(
            QtCore.QEvent.MouseMove, (30, 20),
            QtCore.Qt.NoButton, QtCore.Qt.LeftButton,
        )
        qzui.mouseMoveEvent(move)

        mock_handler = MagicMock()
        qzui.ocr_region_selected.connect(mock_handler)

        release = _mouse_event(
            QtCore.QEvent.MouseButtonRelease, (30, 20),
            QtCore.Qt.LeftButton, QtCore.Qt.LeftButton,
        )
        qzui.mouseReleaseEvent(release)
        QtWidgets.QApplication.processEvents()

        mock_handler.assert_called_once()
        captured = mock_handler.call_args[0][0]
        assert captured.width() == 120
        assert captured.height() == 100
