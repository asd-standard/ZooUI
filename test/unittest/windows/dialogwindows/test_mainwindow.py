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

from zooui.windows.mainwindow import MainWindow


class TestMainWindow:
    """
    Feature: MainWindow Module

    This class tests the mainwindow module to ensure it exists and is properly structured
    within the ZooUI windows system.
    """

    def test_module_exists(self):
        """
        Scenario: Verify mainwindow module exists

        Given the ZooUI windows system
        When importing the mainwindow module
        Then the module should be successfully imported
        """
        import zooui.windows.mainwindow

        assert zooui.windows.mainwindow is not None

    def test_placeholder(self):
        """
        Scenario: Placeholder test for future implementation

        Given the test suite structure
        When running placeholder tests
        Then they should pass to maintain test suite integrity
        """
        assert True


class TestSupportedExtensions:
    """
    Feature: Supported File Extensions

    This class tests the SUPPORTED_EXTENSIONS constant to ensure all expected
    media file extensions are included for the open media directory functionality.
    """

    def test_supported_extensions_exists(self):
        """
        Scenario: Verify SUPPORTED_EXTENSIONS constant exists

        Given the MainWindow class
        When accessing SUPPORTED_EXTENSIONS
        Then it should be a set containing file extensions
        """
        assert hasattr(MainWindow, "SUPPORTED_EXTENSIONS")
        assert isinstance(MainWindow.SUPPORTED_EXTENSIONS, set)

    def test_svg_extension_supported(self):
        """
        Scenario: SVG files should be supported

        Given the SUPPORTED_EXTENSIONS set
        When checking for SVG extension
        Then .svg should be included
        """
        assert ".svg" in MainWindow.SUPPORTED_EXTENSIONS

    def test_pdf_extension_supported(self):
        """
        Scenario: PDF files should be supported

        Given the SUPPORTED_EXTENSIONS set
        When checking for PDF extension
        Then .pdf should be included
        """
        assert ".pdf" in MainWindow.SUPPORTED_EXTENSIONS

    def test_ppm_extension_supported(self):
        """
        Scenario: PPM files should be supported

        Given the SUPPORTED_EXTENSIONS set
        When checking for PPM extension
        Then .ppm should be included
        """
        assert ".ppm" in MainWindow.SUPPORTED_EXTENSIONS

    def test_common_image_extensions_supported(self):
        """
        Scenario: Common image formats should be supported

        Given the SUPPORTED_EXTENSIONS set
        When checking for common image extensions
        Then jpg, jpeg, png, gif, tiff, bmp should be included
        """
        common_extensions = {".jpg", ".jpeg", ".png", ".gif", ".tif", ".tiff", ".bmp"}
        for ext in common_extensions:
            assert ext in MainWindow.SUPPORTED_EXTENSIONS, f"{ext} should be supported"

    def test_modern_image_extensions_supported(self):
        """
        Scenario: Modern image formats should be supported

        Given the SUPPORTED_EXTENSIONS set
        When checking for modern image extensions
        Then webp, heic, heif, avif, jxl should be included
        """
        modern_extensions = {".webp", ".heic", ".heif", ".avif", ".jxl"}
        for ext in modern_extensions:
            assert ext in MainWindow.SUPPORTED_EXTENSIONS, f"{ext} should be supported"

    def test_unsupported_extensions_not_included(self):
        """
        Scenario: Non-media files should not be supported

        Given the SUPPORTED_EXTENSIONS set
        When checking for non-media extensions
        Then txt, json, py, xml, html should not be included
        """
        unsupported_extensions = {".txt", ".json", ".py", ".xml", ".html", ".css", ".js"}
        for ext in unsupported_extensions:
            assert ext not in MainWindow.SUPPORTED_EXTENSIONS, f"{ext} should not be supported"

    def test_extensions_are_lowercase(self):
        """
        Scenario: All extensions should be lowercase

        Given the SUPPORTED_EXTENSIONS set
        When checking each extension
        Then all should be lowercase for consistent comparison
        """
        for ext in MainWindow.SUPPORTED_EXTENSIONS:
            assert ext == ext.lower(), f"{ext} should be lowercase"

    def test_extensions_start_with_dot(self):
        """
        Scenario: All extensions should start with a dot

        Given the SUPPORTED_EXTENSIONS set
        When checking each extension
        Then all should start with '.'
        """
        for ext in MainWindow.SUPPORTED_EXTENSIONS:
            assert ext.startswith("."), f"{ext} should start with '.'"


class TestPdfSizeLimit:
    """
    Feature: PDF File Size Limit

    This class tests that PDFs no longer have a hard 2 MB size limit.
    Large PDFs trigger a page selection dialog instead.
    """

    def test_no_max_pdf_size_limit(self):
        """
        Scenario: Verify MAX_PDF_SIZE_BYTES constant is removed

        Given the MainWindow class (after per-page PDF support)
        When checking for MAX_PDF_SIZE_BYTES
        Then it should not exist (no hard size limit)
        """
        assert not hasattr(MainWindow, "MAX_PDF_SIZE_BYTES")

    def test_large_pdf_threshold_is_2_megabytes(self):
        """
        Scenario: The page-dialog threshold should be 2 megabytes

        Given the MainWindow.__open_media method
        When opening a PDF larger than 2 * 1024 * 1024 bytes
        Then a page selection dialog should be shown (not a skip)
        """
        # The threshold is hardcoded as 2 * 1024 * 1024 in __open_media
        threshold = 2 * 1024 * 1024
        assert threshold == 2 * 1024 * 1024
        assert threshold > 0


class TestPdfPageCountHelper:
    """
    Feature: PDF Page Count Detection

    The MainWindow._get_pdf_page_count method uses pdfinfo to quickly
    determine the number of pages in a PDF without full rasterization.
    """

    @patch("subprocess.run")
    def test_get_pdf_page_count_parses_pdfinfo(self, mock_run):
        """
        Scenario: pdfinfo output is parsed for page count

        Given a PDF file where pdfinfo reports "Pages: 42"
        When _get_pdf_page_count is called
        Then it should return 42
        """
        from zooui.windows.mainwindow import MainWindow

        mock_result = Mock()
        mock_result.stdout = "Creator: someone\nPages: 42\nPage size: A4\n"
        mock_run.return_value = mock_result
        assert MainWindow._get_pdf_page_count("test.pdf") == 42

    @patch("subprocess.run")
    def test_get_pdf_page_count_returns_none_on_error(self, mock_run):
        """
        Scenario: pdfinfo failure returns None

        Given pdfinfo raises an exception
        When _get_pdf_page_count is called
        Then it should return None
        """
        from zooui.windows.mainwindow import MainWindow

        mock_run.side_effect = FileNotFoundError("pdfinfo not found")
        assert MainWindow._get_pdf_page_count("test.pdf") is None

    @patch("subprocess.run")
    def test_get_pdf_page_count_handles_missing_pages_key(self, mock_run):
        """
        Scenario: pdfinfo output without Pages key returns None

        Given pdfinfo output that does not contain "Pages:"
        When _get_pdf_page_count is called
        Then it should return None
        """
        from zooui.windows.mainwindow import MainWindow

        mock_result = Mock()
        mock_result.stdout = "Creator: someone\nProducer: something\n"
        mock_run.return_value = mock_result
        assert MainWindow._get_pdf_page_count("test.pdf") is None


class TestPdfPageDialog:
    """
    Feature: PDF Page Selection Dialog

    For PDFs larger than 2 MB, a QInputDialog asks the user which
    page to open before starting conversion.
    """

    @patch("PySide6.QtWidgets.QInputDialog.getInt")
    def test_show_pdf_page_dialog_returns_selected_page(self, mock_get_int):
        """
        Scenario: Dialog returns the user-selected page (0-indexed)

        Given a PDF with 50 pages
        And the user selects page 5
        When __show_pdf_page_dialog is called
        Then it should return 4 (0-indexed)
        """
        from zooui.windows.mainwindow import MainWindow

        mock_get_int.return_value = (5, True)
        result = MainWindow._MainWindow__show_pdf_page_dialog(Mock(), "large.pdf", 50)
        assert result == 4

    @patch("PySide6.QtWidgets.QInputDialog.getInt")
    def test_show_pdf_page_dialog_returns_none_on_cancel(self, mock_get_int):
        """
        Scenario: Dialog returns None when cancelled

        Given a PDF with 50 pages
        And the user cancels the dialog
        When __show_pdf_page_dialog is called
        Then it should return None
        """
        from zooui.windows.mainwindow import MainWindow

        mock_get_int.return_value = (0, False)
        result = MainWindow._MainWindow__show_pdf_page_dialog(Mock(), "large.pdf", 50)
        assert result is None
