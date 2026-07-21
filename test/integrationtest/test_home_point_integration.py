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
Feature: Home Point Integration

Integration tests for the home point feature covering QZUI round-trip
with real Scene objects.
"""

import pytest
from PySide6 import QtWidgets

from zooui.objects.objectsutils import ZoomManager
from zooui.objects.physicalobject import PhysicalObject
from zooui.objects.scene.qzui import QZUI
from zooui.objects.scene import scene as Scene


@pytest.fixture(scope="session")
def qapp_session():
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    yield app


class TestQZUIHomePointIntegration:
    """
    Feature: QZUI Home Point with Real Scene

    Tests home point set/restore using real Scene objects
    and a QZUI widget.
    """

    def setup_method(self):
        config = {"min_zoomlevel": -10.0, "max_zoomlevel": 12.0, "clamp_enabled": True}
        self.zoom_manager = ZoomManager(config)
        PhysicalObject.set_zoom_manager(self.zoom_manager)

    def teardown_method(self):
        PhysicalObject.set_zoom_manager(None)

    def test_set_and_go_home_point_round_trip(self, qapp_session):
        """
        Scenario: Set and go to home point restores exact view

        Given a QZUI with a real Scene at origin (100, 200) and zoomlevel 3.0
        When set_home_point is called
        And the scene is moved to a different position
        Then go_to_home_point should restore the exact original view
        """
        zui = QZUI(parent=None, framerate=0)
        zui.resize(800, 600)

        scene = Scene.new()
        zui.scene = scene

        scene.origin = (100.0, 200.0)
        scene.zoomlevel = 3.0

        zui.set_home_point()
        assert zui._home_point == ((100.0, 200.0), 3.0)

        scene.origin = (500.0, 600.0)
        scene.zoomlevel = -5.0

        zui.go_to_home_point()
        assert scene.origin == (100.0, 200.0)
        assert scene.zoomlevel == 3.0

    def test_go_to_home_point_noop_when_unset(self, qapp_session):
        """
        Scenario: Go to home point does nothing when not set

        Given a QZUI with no home point set
        When go_to_home_point is called
        Then the scene should remain unchanged and no error should occur
        """
        zui = QZUI(parent=None, framerate=0)
        zui.resize(800, 600)

        scene = Scene.new()
        zui.scene = scene

        scene.origin = (50.0, 60.0)
        scene.zoomlevel = 2.0

        zui.go_to_home_point()
        assert scene.origin == (50.0, 60.0)
        assert scene.zoomlevel == 2.0

    def test_home_point_cleared_on_new_scene(self, qapp_session):
        """
        Scenario: Home point cleared when loading a new scene

        Given a home point has been set
        When a new scene is assigned to the QZUI
        Then the home point should be cleared to None
        """
        zui = QZUI(parent=None, framerate=0)
        zui.resize(800, 600)

        scene = Scene.new()
        zui.scene = scene
        zui.set_home_point()
        assert zui._home_point is not None

        new_scene = Scene.new()
        zui.scene = new_scene
        assert zui._home_point is None

    def test_home_point_with_extreme_zoomlevels(self, qapp_session):
        """
        Scenario: Home point works correctly with extreme zoom levels

        Given a scene at the maximum allowed zoom level
        When the home point is set and the view is moved far away
        Then go_to_home_point should restore the exact zoom level
        """
        zui = QZUI(parent=None, framerate=0)
        zui.resize(800, 600)

        scene = Scene.new()
        zui.scene = scene

        scene.origin = (0.0, 0.0)
        scene.zoomlevel = self.zoom_manager.get_limits()[1]

        zui.set_home_point()
        scene.origin = (10000.0, -5000.0)
        scene.zoomlevel = self.zoom_manager.get_limits()[0]

        zui.go_to_home_point()
        assert scene.zoomlevel == self.zoom_manager.get_limits()[1]
        assert scene.origin == (0.0, 0.0)
