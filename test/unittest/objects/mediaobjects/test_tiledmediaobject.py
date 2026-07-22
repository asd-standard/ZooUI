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

from unittest.mock import Mock, patch

from zooui.objects.mediaobjects.tiledmediaobject import TiledMediaObject


class TestTiledMediaObject:
    """
    Feature: Tiled Media Object Management

    The TiledMediaObject class handles large images by breaking them into tiles
    for efficient zooming and panning. It manages tile generation, caching, and
    on-demand loading of image tiles at different zoom levels.
    """

    @patch("zooui.objects.mediaobjects.tiledmediaobject.TileManager.tiled")
    @patch("zooui.objects.mediaobjects.tiledmediaobject.TileManager.load_tile")
    def test_init_already_tiled(self, mock_load, mock_tiled):
        """
        Scenario: Initialize with pre-tiled media

        Given a media file "test.jpg" that is already tiled
        When TiledMediaObject is created
        Then the object should initialize successfully
        And use existing tiles without re-tiling
        """
        mock_tiled.return_value = True
        scene = Mock()
        obj = TiledMediaObject("test.jpg", scene)
        assert obj is not None

    @patch("zooui.objects.mediaobjects.tiledmediaobject.converterrunner.submit_vips_conversion")
    @patch("zooui.objects.mediaobjects.tiledmediaobject.TileManager.tiled")
    @patch("tempfile.mkstemp")
    @patch("os.close")
    def test_init_needs_tiling(self, mock_close, mock_mkstemp, mock_tiled, mock_submit):
        """
        Scenario: Initialize media that requires tiling

        Given a media file "test.jpg" that hasn't been tiled yet
        When TiledMediaObject is created
        Then temporary files should be created for tiling
        And the object should initialize successfully
        """
        mock_tiled.return_value = False
        mock_mkstemp.return_value = (1, "/tmp/test.ppm")
        scene = Mock()
        obj = TiledMediaObject("test.jpg", scene)
        assert obj is not None

    def test_transparent_attribute(self):
        """
        Scenario: Check transparency support

        Given the TiledMediaObject class
        When accessing the transparent attribute
        Then it should be False (tiled images are opaque)
        """
        assert TiledMediaObject.transparent is False

    def test_default_size_attribute(self):
        """
        Scenario: Check default tile size

        Given the TiledMediaObject class
        When accessing the default_size attribute
        Then it should be (256, 256)
        """
        assert TiledMediaObject.default_size == (256, 256)

    def test_tempcache_attribute(self):
        """
        Scenario: Check temporary cache setting

        Given the TiledMediaObject class
        When accessing the tempcache attribute
        Then it should be 5 (cache size for temporary tiles)
        """
        assert TiledMediaObject.tempcache == 5

    @patch("zooui.objects.mediaobjects.tiledmediaobject.TileManager.tiled")
    def test_inherits_from_mediaobject(self, mock_tiled):
        """
        Scenario: Verify inheritance from MediaObject

        Given a TiledMediaObject instance
        When checking its type
        Then it should be an instance of MediaObject
        """
        from zooui.objects.mediaobjects.mediaobject import MediaObject

        mock_tiled.return_value = True
        with patch("zooui.objects.mediaobjects.tiledmediaobject.TileManager.load_tile"):
            scene = Mock()
            obj = TiledMediaObject("test.jpg", scene)
            assert isinstance(obj, MediaObject)

    @patch("zooui.objects.mediaobjects.tiledmediaobject.TileManager.tiled")
    def test_onscreen_size_property(self, mock_tiled):
        """
        Scenario: Calculate on-screen size at zoom level

        Given a TiledMediaObject at zoom level 0
        When accessing the onscreen_size property
        Then it should return a tuple with (width, height)
        """
        mock_tiled.return_value = True
        with patch("zooui.objects.mediaobjects.tiledmediaobject.TileManager.load_tile"):
            scene = Mock()
            scene.zoomlevel = 0
            obj = TiledMediaObject("test.jpg", scene)
            obj.zoomlevel = 0
            size = obj.onscreen_size
            assert isinstance(size, tuple)
            assert len(size) == 2

    @patch("zooui.objects.mediaobjects.tiledmediaobject.TileManager.tiled")
    def test_deferred_init_skips_tiling_setup(self, mock_tiled):
        """
        Scenario: Deferred initialization skips conversion and tiling setup

        Given a media file "test.jpg" and deferred=True
        When TiledMediaObject is created
        Then no temp file or conversion should be created
        And _loaded should remain False
        """
        mock_tiled.return_value = False

        with patch("tempfile.mkstemp") as mock_mkstemp:
            scene = Mock()
            obj = TiledMediaObject("test.jpg", scene, deferred=True)
            mock_mkstemp.assert_not_called()
        assert not obj._loaded

    @patch("zooui.objects.mediaobjects.tiledmediaobject.TileManager.tiled")
    def test_deferred_init_with_autofit(self, mock_tiled):
        """
        Scenario: Deferred initialization preserves autofit parameter

        Given a PDF file with autofit=True and deferred=True
        When TiledMediaObject is created
        Then it should initialize without errors
        """
        mock_tiled.return_value = False
        scene = Mock()
        obj = TiledMediaObject("doc.pdf", scene, autofit=True, deferred=True)
        assert obj is not None

    @patch("zooui.objects.mediaobjects.tiledmediaobject.TileManager.load_tile")
    @patch("zooui.objects.mediaobjects.tiledmediaobject.TileManager.tiled")
    def test_reset_for_page_changes_media_id(self, mock_tiled, mock_load):
        """
        Scenario: _reset_for_page changes media_id and resets caches

        Given a TiledMediaObject with loaded state
        When _reset_for_page("new:media:id") is called
        Then _media_id should be "new:media:id"
        And _loaded should be False
        And tileblock cache should be cleared
        """
        mock_tiled.return_value = False
        scene = Mock()
        obj = TiledMediaObject("test.jpg", scene, deferred=True)
        obj._loaded = True
        obj._TiledMediaObject__tileblock = object()
        obj._TiledMediaObject__tileblock_id = (0, 0, 0, 0, 0)

        obj._reset_for_page("new:media:id")

        assert obj._media_id == "new:media:id"
        assert not obj._loaded
        assert obj._TiledMediaObject__tileblock is None
        assert obj._TiledMediaObject__tileblock_id is None

    @patch("zooui.objects.mediaobjects.tiledmediaobject.TileManager.load_tile")
    @patch("zooui.objects.mediaobjects.tiledmediaobject.TileManager.tiled")
    def test_reset_for_page_keeps_dimensions(self, mock_tiled, mock_load):
        """
        Scenario: _reset_for_page does not reset dimensions

        Given a TiledMediaObject with custom dimensions loaded
        When _reset_for_page is called
        Then dimensions should be preserved for autofit bounding box calculation
        """
        mock_tiled.return_value = False
        scene = Mock()
        obj = TiledMediaObject("test.jpg", scene, deferred=True)
        obj._TiledMediaObject__width = 1000
        obj._TiledMediaObject__height = 2000
        obj._TiledMediaObject__aspect_ratio = 0.5
        obj._TiledMediaObject__maxtilelevel = 5

        obj._reset_for_page("new:media:id")

        assert obj._TiledMediaObject__width == 1000
        assert obj._TiledMediaObject__height == 2000
        assert obj._TiledMediaObject__aspect_ratio == 0.5
        assert obj._TiledMediaObject__maxtilelevel == 5

    @patch("zooui.objects.mediaobjects.tiledmediaobject.TileManager.load_tile")
    @patch("zooui.objects.mediaobjects.tiledmediaobject.TileManager.tiled")
    def test_reset_for_page_loads_root_tile_if_tiled(self, mock_tiled, mock_load):
        """
        Scenario: _reset_for_page requests root tile when media is tiled

        Given a new media_id that is already tiled in the tilestore
        When _reset_for_page is called
        Then load_tile should be called with (new_media_id, 0, 0, 0)
        """
        mock_tiled.return_value = True
        scene = Mock()
        obj = TiledMediaObject("test.jpg", scene, deferred=True)

        obj._reset_for_page("already:tiled:media")

        mock_load.assert_called_once_with(("already:tiled:media", 0, 0, 0))
