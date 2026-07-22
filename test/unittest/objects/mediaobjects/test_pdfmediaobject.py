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

from unittest.mock import MagicMock, Mock, patch

from PySide6 import QtCore

from zooui.objects.mediaobjects.pdfmediaobject import PdfMediaObject, _BlockingConverter


class TestPdfMediaObject:
    """
    Feature: PDF Media Object Management

    The PdfMediaObject class handles multi-page PDF documents by converting
    each page to a separate PPM, tiling them independently, and providing
    keyboard-driven page navigation with smart alignment.
    """

    @patch("tempfile.mkdtemp")
    @patch("zooui.objects.mediaobjects.pdfmediaobject.converterrunner.ConversionHandle")
    @patch("zooui.objects.mediaobjects.pdfmediaobject.converterrunner.submit_pdf_conversion")
    def test_init_sets_up_deferred_state(self, mock_submit, mock_handle_cls, mock_mkdtemp):
        """
        Scenario: Initialize with valid PDF sets up deferred state

        Given a PDF file "doc.pdf"
        When PdfMediaObject is created with a mock scene
        Then it should submit a PDF conversion
        And page_count should be 0 until conversion completes
        And current_page should be 0
        """
        mock_mkdtemp.return_value = "/tmp/zooui_pdf_test"
        mock_future = Mock()
        mock_submit.return_value = mock_future
        mock_handle = Mock()
        mock_handle_cls.return_value = mock_handle

        scene = Mock()
        obj = PdfMediaObject("doc.pdf", scene)

        assert obj is not None
        assert obj._page_count == 0
        assert obj._current_page == 0
        assert obj._pdf_path == "doc.pdf"
        assert obj._pending_nav_direction is None
        mock_submit.assert_called_once_with("doc.pdf", "/tmp/zooui_pdf_test")

    @patch("tempfile.mkdtemp")
    @patch("zooui.objects.mediaobjects.pdfmediaobject.converterrunner.ConversionHandle")
    @patch("zooui.objects.mediaobjects.pdfmediaobject.converterrunner.submit_pdf_conversion")
    def test_init_with_custom_start_page(self, mock_submit, mock_handle_cls, mock_mkdtemp):
        """
        Scenario: Initialize with a custom start page

        Given a PDF file "doc.pdf" and start_page=5
        When PdfMediaObject is created
        Then _start_page should be stored as 5
        """
        mock_mkdtemp.return_value = "/tmp/zooui_pdf_test"
        mock_submit.return_value = Mock()
        mock_handle_cls.return_value = Mock()

        scene = Mock()
        obj = PdfMediaObject("doc.pdf", scene, start_page=5)

        assert obj._start_page == 5

    @patch("tempfile.mkdtemp")
    @patch("zooui.objects.mediaobjects.pdfmediaobject.converterrunner.ConversionHandle")
    @patch("zooui.objects.mediaobjects.pdfmediaobject.converterrunner.submit_pdf_conversion")
    def test_page_count_zero_before_conversion(self, mock_submit, mock_handle_cls, mock_mkdtemp):
        """
        Scenario: page_count property returns zero while conversion is running

        Given a newly created PdfMediaObject
        When accessing the page_count property
        Then it should return 0 (conversion not yet complete)
        """
        mock_mkdtemp.return_value = "/tmp/zooui_pdf_test"
        mock_submit.return_value = Mock()
        mock_handle_cls.return_value = Mock()

        obj = PdfMediaObject("doc.pdf", Mock())
        assert obj.page_count == 0

    @patch("tempfile.mkdtemp")
    @patch("zooui.objects.mediaobjects.pdfmediaobject.converterrunner.ConversionHandle")
    @patch("zooui.objects.mediaobjects.pdfmediaobject.converterrunner.submit_pdf_conversion")
    def test_current_page_label_loading(self, mock_submit, mock_handle_cls, mock_mkdtemp):
        """
        Scenario: current_page_label shows loading when conversion is running

        Given a PdfMediaObject with page_count==0
        When accessing current_page_label
        Then it should return "Loading..."
        """
        mock_mkdtemp.return_value = "/tmp/zooui_pdf_test"
        mock_submit.return_value = Mock()
        mock_handle_cls.return_value = Mock()

        obj = PdfMediaObject("doc.pdf", Mock())
        assert obj.current_page_label == "Loading..."

    def test_current_page_label_after_conversion(self):
        """
        Scenario: current_page_label shows page info after conversion

        Given a PdfMediaObject with 5 pages and current page 2
        When accessing current_page_label
        Then it should return "Page 3/5"
        """
        obj = _make_pdf_with_pages(page_count=5, current_page=2)
        assert obj.current_page_label == "Page 3/5"

    def test_change_page_does_nothing_when_page_count_le_one(self):
        """
        Scenario: change_page is a no-op when there is only one page

        Given a PdfMediaObject with page_count==1
        When change_page is called with delta=+1
        Then _current_page should remain 0
        """
        obj = _make_pdf_with_pages(page_count=1, current_page=0)
        obj.change_page(1)
        assert obj._current_page == 0

    def test_change_page_navigates_forward(self):
        """
        Scenario: change_page navigates forward by one page

        Given a PdfMediaObject with 10 pages on page 0
        When change_page(+1) is called
        Then _current_page should become 1
        And _pending_nav_direction should be 1
        """
        obj = _make_pdf_with_pages(page_count=10, current_page=0)
        obj.change_page(1)
        assert obj._current_page == 1
        assert obj._pending_nav_direction == 1

    def test_change_page_navigates_backward(self):
        """
        Scenario: change_page navigates backward by one page

        Given a PdfMediaObject with 10 pages on page 5
        When change_page(-1) is called
        Then _current_page should become 4
        And _pending_nav_direction should be -1
        """
        obj = _make_pdf_with_pages(page_count=10, current_page=5)
        obj.change_page(-1)
        assert obj._current_page == 4
        assert obj._pending_nav_direction == -1

    def test_change_page_clamps_at_upper_bound(self):
        """
        Scenario: change_page does not navigate past the last page

        Given a PdfMediaObject with 3 pages on page 2 (last page)
        When change_page(+1) is called
        Then _current_page should remain 2
        """
        obj = _make_pdf_with_pages(page_count=3, current_page=2)
        obj.change_page(1)
        assert obj._current_page == 2

    def test_change_page_clamps_at_lower_bound(self):
        """
        Scenario: change_page does not navigate past the first page

        Given a PdfMediaObject with 3 pages on page 0 (first page)
        When change_page(-1) is called
        Then _current_page should remain 0
        """
        obj = _make_pdf_with_pages(page_count=3, current_page=0)
        obj.change_page(-1)
        assert obj._current_page == 0

    def test_go_to_page_valid(self):
        """
        Scenario: go_to_page navigates to a valid page number

        Given a PdfMediaObject with 10 pages on page 0
        When go_to_page(5) is called (1-indexed)
        Then _current_page should become 4 (0-indexed)
        And _pending_nav_direction should be 1
        """
        obj = _make_pdf_with_pages(page_count=10, current_page=0)
        obj.go_to_page(5)
        assert obj._current_page == 4
        assert obj._pending_nav_direction == 1

    def test_go_to_page_backward(self):
        """
        Scenario: go_to_page navigates backward to a lower page

        Given a PdfMediaObject with 10 pages on page 8
        When go_to_page(3) is called (1-indexed)
        Then _current_page should become 2 (0-indexed)
        And _pending_nav_direction should be -1
        """
        obj = _make_pdf_with_pages(page_count=10, current_page=8)
        obj.go_to_page(3)
        assert obj._current_page == 2
        assert obj._pending_nav_direction == -1

    def test_go_to_page_invalid_zero(self):
        """
        Scenario: go_to_page ignores page number 0

        Given a PdfMediaObject with 10 pages
        When go_to_page(0) is called
        Then _current_page should remain unchanged
        """
        obj = _make_pdf_with_pages(page_count=10, current_page=3)
        obj.go_to_page(0)
        assert obj._current_page == 3

    def test_go_to_page_invalid_beyond_count(self):
        """
        Scenario: go_to_page ignores page number beyond page_count

        Given a PdfMediaObject with 10 pages
        When go_to_page(11) is called
        Then _current_page should remain unchanged
        """
        obj = _make_pdf_with_pages(page_count=10, current_page=3)
        obj.go_to_page(11)
        assert obj._current_page == 3

    def test_handle_key_ctrl_up(self):
        """
        Scenario: Ctrl+Up triggers page decrement

        Given a PdfMediaObject with 10 pages
        When handle_key is called with Key_Up + ControlModifier
        Then it should return True and decrement current_page
        """
        obj = _make_pdf_with_pages(page_count=10, current_page=3)
        result = obj.handle_key(QtCore.Qt.Key_Up, QtCore.Qt.ControlModifier)
        assert result is True
        assert obj._current_page == 2

    def test_handle_key_ctrl_down(self):
        """
        Scenario: Ctrl+Down triggers page increment

        Given a PdfMediaObject with 10 pages
        When handle_key is called with Key_Down + ControlModifier
        Then it should return True and increment current_page
        """
        obj = _make_pdf_with_pages(page_count=10, current_page=3)
        result = obj.handle_key(QtCore.Qt.Key_Down, QtCore.Qt.ControlModifier)
        assert result is True
        assert obj._current_page == 4

    def test_handle_key_ctrl_alt_g(self):
        """
        Scenario: Ctrl+Alt+G triggers go-to-page dialog

        Given a PdfMediaObject with pages loaded
        When handle_key is called with Key_G + ControlModifier + AltModifier
        Then it should return True
        """
        obj = _make_pdf_with_pages(page_count=10, current_page=0)
        with patch.object(obj, "_show_go_to_page_dialog") as mock_dialog:
            result = obj.handle_key(
                QtCore.Qt.Key_G, QtCore.Qt.ControlModifier | QtCore.Qt.AltModifier
            )
        assert result is True
        mock_dialog.assert_called_once()

    def test_handle_key_ctrl_g_without_alt(self):
        """
        Scenario: Ctrl+G without Alt is ignored

        Given a PdfMediaObject with pages loaded
        When handle_key is called with Key_G + ControlModifier (no Alt)
        Then it should return False
        """
        obj = _make_pdf_with_pages(page_count=10, current_page=0)
        result = obj.handle_key(QtCore.Qt.Key_G, QtCore.Qt.ControlModifier)
        assert result is False

    def test_handle_key_irrelevant_key(self):
        """
        Scenario: Non-navigation keys are ignored

        Given a PdfMediaObject with pages loaded
        When handle_key is called with Key_A and no modifiers
        Then it should return False
        """
        obj = _make_pdf_with_pages(page_count=10, current_page=0)
        result = obj.handle_key(QtCore.Qt.Key_A, QtCore.Qt.NoModifier)
        assert result is False

    def test_handle_key_no_pages_loaded(self):
        """
        Scenario: Key handling returns False when conversion is still running

        Given a PdfMediaObject with page_count==0
        When handle_key is called with any navigation key
        Then it should return False
        """
        obj = _make_pdf_with_pages(page_count=0, current_page=0)
        result = obj.handle_key(QtCore.Qt.Key_Up, QtCore.Qt.ControlModifier)
        assert result is False

    @patch("zooui.objects.mediaobjects.pdfmediaobject._glob.glob")
    def test_on_conversion_complete_discovers_pages(self, mock_glob):
        """
        Scenario: _on_conversion_complete discovers page count from PPM files

        Given a PdfMediaObject with conversion finished
        And the output directory contains 3 page PPMs
        When _on_conversion_complete is called
        Then _page_count should be 3
        And _page_ppm_paths should contain 3 paths
        And _start_page should become _current_page
        """
        obj = _make_pdf_with_pages(page_count=0, current_page=0)
        obj._start_page = 0
        mock_glob.return_value = [
            "/tmp/out/page_0000.ppm",
            "/tmp/out/page_0001.ppm",
            "/tmp/out/page_0002.ppm",
        ]
        obj._on_conversion_complete()
        assert obj._page_count == 3
        assert len(obj._page_ppm_paths) == 3
        assert obj._current_page == 0

    def test_on_conversion_complete_clamps_start_page(self):
        """
        Scenario: _on_conversion_complete clamps _start_page to valid range

        Given a PdfMediaObject with 3 discovered pages and _start_page==5
        When _on_conversion_complete is called
        Then _start_page should be reset to 0
        """
        obj = _make_pdf_with_pages(page_count=0, current_page=0)
        obj._start_page = 5
        with patch("zooui.objects.mediaobjects.pdfmediaobject._glob.glob") as mock_glob:
            mock_glob.return_value = [
                "/tmp/out/page_0000.ppm",
                "/tmp/out/page_0001.ppm",
                "/tmp/out/page_0002.ppm",
            ]
            obj._on_conversion_complete()
        assert obj._start_page == 0
        assert obj._current_page == 0

    @patch("zooui.objects.mediaobjects.pdfmediaobject._glob.glob")
    def test_on_conversion_complete_no_ppms(self, mock_glob):
        """
        Scenario: _on_conversion_complete handles empty output directory

        Given a PdfMediaObject with conversion finished
        And the output directory contains no page PPMs
        When _on_conversion_complete is called
        Then an error should be logged
        And _page_count should remain 0
        """
        obj = _make_pdf_with_pages(page_count=0, current_page=0)
        mock_glob.return_value = []
        obj._on_conversion_complete()
        assert obj._page_count == 0

    def test_check_conversion_complete_sets_page_count(self):
        """
        Scenario: _check_conversion_complete calls _on_conversion_complete when ready

        Given a PdfMediaObject with conversion progress == 1.0
        When _check_conversion_complete is called
        Then _on_conversion_complete should be invoked
        """
        obj = _make_pdf_with_pages(page_count=0, current_page=0)
        mock_converter = Mock()
        mock_converter.progress = 1.0
        mock_converter.error = None
        obj._PdfMediaObject__pdf_converter = mock_converter

        with patch.object(obj, "_on_conversion_complete") as mock_on_complete, \
             patch("zooui.objects.mediaobjects.pdfmediaobject._glob.glob") as mock_glob:
            mock_glob.return_value = [
                "/tmp/out/page_0000.ppm",
                "/tmp/out/page_0001.ppm",
            ]
            obj._check_conversion_complete()
        mock_on_complete.assert_called_once()

    def test_check_conversion_complete_skips_if_already_done(self):
        """
        Scenario: _check_conversion_complete is a no-op when page_count > 0

        Given a PdfMediaObject with page_count==5 (already discovered)
        When _check_conversion_complete is called
        Then _on_conversion_complete should not be invoked
        """
        obj = _make_pdf_with_pages(page_count=5, current_page=0)
        with patch.object(obj, "_on_conversion_complete") as mock_on_complete:
            obj._check_conversion_complete()
        mock_on_complete.assert_not_called()

    def test_check_conversion_complete_handles_error(self):
        """
        Scenario: _check_conversion_complete handles conversion errors

        Given a PdfMediaObject with conversion progress == 1.0 but an error
        When _check_conversion_complete is called
        Then an error should be logged and _on_conversion_complete NOT called
        """
        obj = _make_pdf_with_pages(page_count=0, current_page=0)
        mock_converter = Mock()
        mock_converter.progress = 1.0
        mock_converter.error = "something went wrong"
        obj._PdfMediaObject__pdf_converter = mock_converter

        with patch.object(obj, "_on_conversion_complete") as mock_on_complete:
            obj._check_conversion_complete()
        mock_on_complete.assert_not_called()

    @patch("zooui.objects.mediaobjects.pdfmediaobject.TileManager.tiled")
    def test_check_page_tiling_marks_page_as_tiled(self, mock_tiled):
        """
        Scenario: _check_page_tiling marks a page as tiled when its tiling completes

        Given a page being actively tiled (tiler present with progress 1.0)
        And TileManager.tiled returns True
        When _check_page_tiling is called
        Then the page should be added to _page_tiled
        And removed from _page_tilers and _page_tiling
        """
        obj = _make_pdf_with_pages(page_count=5, current_page=2)
        mock_tiler = Mock()
        mock_tiler.progress = 1.0
        obj._page_tilers = {2: mock_tiler}
        obj._page_tiling = {2}
        mock_tiled.return_value = True

        obj._check_page_tiling()

        assert 2 in obj._page_tiled
        assert 2 not in obj._page_tiling
        assert 2 not in obj._page_tilers

    @patch("zooui.objects.mediaobjects.pdfmediaobject.TileManager.tiled")
    def test_check_page_tiling_does_not_mark_if_not_tiled(self, mock_tiled):
        """
        Scenario: _check_page_tiling does not mark page if tiles not on disk yet

        Given a page whose tiling process reports 1.0
        But TileManager.tiled returns False (tiles not yet written)
        When _check_page_tiling is called
        Then the page should remain in _page_tiling
        """
        obj = _make_pdf_with_pages(page_count=5, current_page=2)
        mock_tiler = Mock()
        mock_tiler.progress = 1.0
        obj._page_tilers = {2: mock_tiler}
        obj._page_tiling = {2}
        mock_tiled.return_value = False

        obj._check_page_tiling()

        assert 2 not in obj._page_tiled
        assert 2 in obj._page_tiling
        assert 2 in obj._page_tilers

    @patch("zooui.objects.mediaobjects.pdfmediaobject.submit_tiling")
    @patch("zooui.objects.mediaobjects.pdfmediaobject.TileManager.tiled")
    def test_ensure_page_tiling_starts_tiling_for_untiled_page(self, mock_tiled, mock_submit):
        """
        Scenario: _ensure_page_tiling submits tiling for an untiled page

        Given a PdfMediaObject with 5 pages and page 3 not yet tiled or being tiled
        When _ensure_page_tiling(3) is called
        Then submit_tiling should be called
        And page 3 should be added to _page_tiling
        """
        obj = _make_pdf_with_pages(page_count=5, current_page=0)
        obj._page_ppm_paths = ["p0.ppm", "p1.ppm", "p2.ppm", "p3.ppm", "p4.ppm"]
        mock_tiled.return_value = False
        mock_future = Mock()
        mock_submit.return_value = mock_future

        with patch("zooui.objects.mediaobjects.pdfmediaobject.TilingHandle") as mock_handle_cls:
            mock_handle = Mock()
            mock_handle_cls.return_value = mock_handle
            obj._ensure_page_tiling(3)

        mock_submit.assert_called_once_with("p3.ppm", "doc.pdf:page:3", "png")
        assert 3 in obj._page_tiling

    @patch("zooui.objects.mediaobjects.pdfmediaobject.TileManager.tiled")
    def test_ensure_page_tiling_already_tiled(self, mock_tiled):
        """
        Scenario: _ensure_page_tiling skips pages already in tilestore

        Given page 2 is already tiled on disk
        When _ensure_page_tiling(2) is called
        Then it should add it to _page_tiled without submitting tiling
        """
        obj = _make_pdf_with_pages(page_count=5, current_page=0)
        mock_tiled.return_value = True
        obj._ensure_page_tiling(2)
        assert 2 in obj._page_tiled

    def test_ensure_page_tiling_already_being_tiled(self):
        """
        Scenario: _ensure_page_tiling skips pages already being tiled

        Given page 3 is already in _page_tiling
        When _ensure_page_tiling(3) is called
        Then no new tiling job should be submitted
        """
        obj = _make_pdf_with_pages(page_count=5, current_page=0)
        obj._page_tiling.add(3)
        with patch("zooui.objects.mediaobjects.pdfmediaobject.submit_tiling") as mock_submit:
            obj._ensure_page_tiling(3)
        mock_submit.assert_not_called()

    def test_ensure_page_tiling_out_of_range(self):
        """
        Scenario: _ensure_page_tiling ignores out-of-range page indices

        Given a PdfMediaObject with 5 pages
        When _ensure_page_tiling(5) or (-1) is called
        Then no tiling job should be submitted
        """
        obj = _make_pdf_with_pages(page_count=5, current_page=0)
        with patch("zooui.objects.mediaobjects.pdfmediaobject.submit_tiling") as mock_submit:
            obj._ensure_page_tiling(5)
            obj._ensure_page_tiling(-1)
        mock_submit.assert_not_called()

    def test_maintain_buffer_tiles_current_and_next(self):
        """
        Scenario: _maintain_buffer submits tiling for current page and next page

        Given a PdfMediaObject on page 2 with 5 pages total
        When _maintain_buffer is called
        Then _ensure_page_tiling should be called for page 2 and page 3
        """
        obj = _make_pdf_with_pages(page_count=5, current_page=2)
        calls = []

        def track(page_idx):
            calls.append(page_idx)

        with patch.object(obj, "_ensure_page_tiling", side_effect=track):
            obj._maintain_buffer()
        assert 2 in calls
        assert 3 in calls

    def test_maintain_buffer_clamps_at_last_page(self):
        """
        Scenario: _maintain_buffer does not tile past the last page

        Given a PdfMediaObject on the last page (4) with 5 pages total
        When _maintain_buffer is called
        Then _ensure_page_tiling should only be called for page 4
        """
        obj = _make_pdf_with_pages(page_count=5, current_page=4)
        calls = []

        def track(page_idx):
            calls.append(page_idx)

        with patch.object(obj, "_ensure_page_tiling", side_effect=track):
            obj._maintain_buffer()
        assert calls == [4]

    def test_current_page_property(self):
        """
        Scenario: current_page property returns the zero-based page index

        Given a PdfMediaObject on page 3
        When accessing current_page
        Then it should return 3
        """
        obj = _make_pdf_with_pages(page_count=10, current_page=3)
        assert obj.current_page == 3

    def test_page_count_property_returns_count(self):
        """
        Scenario: page_count property returns the total page count

        Given a PdfMediaObject with 7 discovered pages
        When accessing page_count
        Then it should return 7
        """
        obj = _make_pdf_with_pages(page_count=7, current_page=0)
        assert obj.page_count == 7

    def test_BlockingConverter_progress(self):
        """
        Scenario: _BlockingConverter always has progress 0.0

        Given the _BlockingConverter class
        When accessing its progress attribute
        Then it should be 0.0
        """
        bc = _BlockingConverter()
        assert bc.progress == 0.0

    def test_try_load_aligns_top_left_on_forward(self):
        """
        Scenario: _try_load aligns page top-left to viewport top-left on forward nav

        Given _pending_nav_direction == 1 and topleft at (100, 200)
        When _try_load is called (page finishes loading)
        Then move should be called with (-100, -200)
        And _pending_nav_direction should be cleared to None
        """
        obj = _make_pdf_with_pages(page_count=10, current_page=0)
        obj._pending_nav_direction = 1
        obj._loaded = False

        with patch.object(obj, "move") as mock_move, \
             patch.object(obj.__class__, "topleft", new_callable=lambda: property(lambda s: (100.0, 200.0))), \
             patch("zooui.objects.mediaobjects.pdfmediaobject.TiledMediaObject._try_load") as mock_super_load:
            mock_super_load.side_effect = _make_loaded(obj)
            obj._try_load()

        mock_move.assert_called_once_with(-100.0, -200.0)
        assert obj._pending_nav_direction is None

    def test_try_load_aligns_bottom_right_on_backward(self):
        """
        Scenario: _try_load aligns page bottom-right to viewport bottom-right on backward nav

        Given _pending_nav_direction == -1, bottomright at (400, 500), viewport (800, 600)
        When _try_load is called
        Then move should be called with (400, 100)
        And _pending_nav_direction should be cleared to None
        """
        obj = _make_pdf_with_pages(page_count=10, current_page=5)
        obj._pending_nav_direction = -1
        obj._loaded = False

        with patch.object(obj, "move") as mock_move, \
             patch.object(obj.__class__, "bottomright", new_callable=lambda: property(lambda s: (400.0, 500.0))), \
             patch("zooui.objects.mediaobjects.pdfmediaobject.TiledMediaObject._try_load") as mock_super_load:
            mock_super_load.side_effect = _make_loaded(obj)
            obj._try_load()

        mock_move.assert_called_once_with(400.0, 100.0)
        assert obj._pending_nav_direction is None

    def test_try_load_clears_pending_direction(self):
        """
        Scenario: _try_load clears _pending_nav_direction after applying alignment

        Given _pending_nav_direction == 1
        When _try_load completes
        Then _pending_nav_direction should be None
        """
        obj = _make_pdf_with_pages(page_count=10, current_page=0)
        obj._pending_nav_direction = 1
        obj._loaded = False

        with patch.object(obj, "move"), \
             patch.object(obj.__class__, "topleft", new_callable=lambda: property(lambda s: (50.0, 50.0))), \
             patch("zooui.objects.mediaobjects.pdfmediaobject.TiledMediaObject._try_load") as mock_super_load:
            mock_super_load.side_effect = _make_loaded(obj)
            obj._try_load()

        assert obj._pending_nav_direction is None


def _make_loaded(obj):
    """Side-effect that marks the object as loaded."""
    def _side_effect():
        obj._loaded = True
    return _side_effect


def _make_pdf_with_pages(page_count: int, current_page: int, **kwargs) -> PdfMediaObject:
    """Create a PdfMediaObject with pre-set internal state for testing.

    Bypasses the full __init__ pipeline (conversion, tiling, etc.).
    """
    with patch("zooui.objects.mediaobjects.pdfmediaobject.tempfile.mkdtemp", return_value="/tmp/test_out"), \
         patch("zooui.objects.mediaobjects.pdfmediaobject.converterrunner.submit_pdf_conversion", return_value=Mock()), \
         patch("zooui.objects.mediaobjects.pdfmediaobject.converterrunner.ConversionHandle", return_value=Mock()):
        obj = PdfMediaObject("doc.pdf", MagicMock(), **kwargs)

    obj._page_count = page_count
    obj._current_page = current_page if current_page < page_count else 0
    obj._page_ppm_paths = [f"/tmp/p{i}.ppm" for i in range(page_count)]
    obj._pdf_path = "doc.pdf"
    obj._scene.viewport_size = (800, 600)

    return obj
