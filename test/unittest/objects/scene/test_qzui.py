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

import time
from unittest.mock import MagicMock, patch

import pytest
from PySide6 import QtCore, QtGui, QtWidgets

from zooui.objects.scene.qzui import QZUI


class TestQZUI:
    """
    Feature: QZUI Module

    This class tests the QZUI module to ensure it exists and the QZUI class is properly
    defined within the ZooUI scene system.
    """

    def test_module_exists(self):
        """
        Scenario: Verify qzui module exists

        Given the ZooUI scene system
        When importing the qzui module
        Then the module should be successfully imported
        """
        import zooui.objects.scene.qzui

        assert zooui.objects.scene.qzui is not None

    def test_qzui_class_exists(self):
        """
        Scenario: Verify QZUI class exists

        Given the qzui module
        When checking for the QZUI class
        Then the class should be defined
        """
        from zooui.objects.scene.qzui import QZUI

        assert QZUI is not None

    def test_placeholder(self):
        """
        Scenario: Placeholder test for future implementation

        Given the test suite structure
        When running placeholder tests
        Then they should pass to maintain test suite integrity
        """
        assert True


class TestQZUIHomePoint:
    """
    Feature: Home Point Navigation

    The QZUI widget supports saving and restoring a home point consisting
    of the current scene origin and zoom level. A visual pulse marker is
    drawn at the viewport centre for 0.8 seconds after setting the home point.
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
            return zui

    def test_set_home_point_saves_origin_and_zoomlevel(self, qzui, mock_scene):
        """
        Scenario: Set home point saves current view

        Given a scene with origin (100.0, 200.0) and zoomlevel 3.5
        When set_home_point is called
        Then the home point should store ((100.0, 200.0), 3.5)
        """
        mock_scene.origin = (100.0, 200.0)
        mock_scene.zoomlevel = 3.5
        qzui.set_home_point()
        assert qzui._home_point == ((100.0, 200.0), 3.5)

    def test_set_home_point_updates_timestamp(self, qzui):
        """
        Scenario: Set home point updates the marker timestamp

        Given a QZUI instance
        When set_home_point is called
        Then the timestamp should be set to the current time
        """
        before = time.time()
        qzui.set_home_point()
        after = time.time()
        assert before <= qzui._home_point_timestamp <= after + 0.1

    def test_go_to_home_point_restores_view(self, qzui, mock_scene):
        """
        Scenario: Go to home point restores saved view

        Given a saved home point at origin (42.0, 99.0) and zoomlevel 7.0
        When go_to_home_point is called
        Then scene.zoomlevel should be 7.0 and scene.origin should be (42.0, 99.0)
        """
        qzui._home_point = ((42.0, 99.0), 7.0)
        qzui.go_to_home_point()
        assert mock_scene.zoomlevel == 7.0
        assert mock_scene.origin == (42.0, 99.0)

    def test_go_to_home_point_noop_when_none(self, qzui, mock_scene):
        """
        Scenario: Go to home point does nothing when no home point set

        Given _home_point is None
        And the scene is at some origin and zoomlevel
        When go_to_home_point is called
        Then the scene origin and zoomlevel should remain unchanged
        """
        qzui._home_point = None
        mock_scene.origin = (88.0, 77.0)
        mock_scene.zoomlevel = 2.0
        qzui.go_to_home_point()
        assert mock_scene.zoomlevel == 2.0
        assert mock_scene.origin == (88.0, 77.0)

    def test_keypress_shift_home_sets_home_point(self, qzui, mock_scene):
        """
        Scenario: Shift+Home key press sets home point

        Given a scene at origin (30.0, 40.0) with zoomlevel 1.0
        When a keyPressEvent with Key_Home + ShiftModifier is received
        Then the home point should be saved
        """
        mock_scene.origin = (30.0, 40.0)
        mock_scene.zoomlevel = 1.0
        event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Home, QtCore.Qt.ShiftModifier)
        qzui.keyPressEvent(event)
        assert qzui._home_point == ((30.0, 40.0), 1.0)

    def test_keypress_home_goes_to_home_point(self, qzui, mock_scene):
        """
        Scenario: Home key press goes to home point

        Given a saved home point and a different current view
        When a keyPressEvent with Key_Home (no modifier) is received
        Then the view should be restored to the home point
        """
        qzui._home_point = ((10.0, 20.0), 5.0)
        event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Home, QtCore.Qt.NoModifier)
        qzui.keyPressEvent(event)
        assert mock_scene.zoomlevel == 5.0
        assert mock_scene.origin == (10.0, 20.0)

    def test_pulse_marker_not_drawn_when_none(self, qzui, qapp):
        """
        Scenario: No pulse marker drawn when home point is None

        Given _home_point is None
        When paintEvent is triggered
        Then no pulse marker draw calls should be made
        """
        qzui._home_point = None
        mock_painter = MagicMock()
        with patch("zooui.objects.scene.qzui.QtGui.QPainter", return_value=mock_painter):
            qzui.paintEvent(QtGui.QPaintEvent(qzui.rect()))
        mock_painter.drawLine.assert_not_called()
        mock_painter.drawEllipse.assert_not_called()

    def test_pulse_marker_drawn_within_time_window(self, qzui, qapp):
        """
        Scenario: Pulse marker is drawn within the 0.8s window

        Given a home point was just set (timestamp = now)
        When paintEvent is triggered
        Then drawLine and drawEllipse should be called for the pulse marker
        """
        qzui._home_point = ((0.0, 0.0), 0.0)
        qzui._home_point_timestamp = time.time()
        qzui.resize(800, 600)
        mock_painter = MagicMock()
        with patch("zooui.objects.scene.qzui.QtGui.QPainter", return_value=mock_painter):
            with patch.object(qzui, "update"):
                qzui.paintEvent(QtGui.QPaintEvent(qzui.rect()))
        assert mock_painter.drawLine.call_count >= 1
        assert mock_painter.drawEllipse.call_count >= 1

    def test_pulse_marker_not_drawn_after_timeout(self, qzui, qapp):
        """
        Scenario: Pulse marker is not drawn after the 0.8s window

        Given a home point was set more than 0.8s ago
        When paintEvent is triggered
        Then no pulse marker draw calls should be made
        """
        qzui._home_point = ((0.0, 0.0), 0.0)
        qzui._home_point_timestamp = time.time() - 1.0
        mock_painter = MagicMock()
        with patch("zooui.objects.scene.qzui.QtGui.QPainter", return_value=mock_painter):
            qzui.paintEvent(QtGui.QPaintEvent(qzui.rect()))
        mock_painter.drawLine.assert_not_called()
        mock_painter.drawEllipse.assert_not_called()
