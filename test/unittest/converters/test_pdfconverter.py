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

from zooui.converters.pdfconverter import PDFConverter


class TestPDFConverter:
    """
    Feature: PDF Converter

    This test suite validates the PDFConverter class which converts PDF files
    to per-page PPM files using the pdftoppm command-line tool.
    """

    def test_init(self):
        """
        Scenario: Initialize PDF converter

        Given input PDF path and output directory path
        When a PDFConverter is instantiated
        Then it should store the file paths
        And resolution should default to 300
        And page_count should be 0
        """
        converter = PDFConverter("input.pdf", "/tmp/outdir")
        assert converter._infile == "input.pdf"
        assert converter._outfile == "/tmp/outdir"
        assert converter.resolution == 300
        assert converter.page_count == 0
        assert converter.page_paths == []

    def test_inherits_from_converter(self):
        """
        Scenario: Verify inheritance from Converter

        Given a PDFConverter instance
        When checking its type
        Then it should be an instance of Converter
        """
        from zooui.converters.converter import Converter

        converter = PDFConverter("input.pdf", "/tmp/outdir")
        assert isinstance(converter, Converter)

    def test_resolution_attribute(self):
        """
        Scenario: Verify default resolution setting

        Given a newly created PDFConverter
        When checking the resolution attribute
        Then it should be 300 DPI
        """
        converter = PDFConverter("input.pdf", "/tmp/outdir")
        assert converter.resolution == 300

    def test_resolution_can_be_changed(self):
        """
        Scenario: Modify resolution setting

        Given a PDFConverter instance
        When the resolution attribute is changed
        Then it should store the new value
        """
        converter = PDFConverter("input.pdf", "/tmp/outdir")
        converter.resolution = 150
        assert converter.resolution == 150

    @patch("os.listdir")
    @patch("os.makedirs")
    @patch("shutil.copy2")
    @patch("subprocess.Popen")
    @patch("tempfile.mkdtemp")
    @patch("shutil.rmtree")
    def test_run_success(self, mock_rmtree, mock_mkdtemp, mock_popen, mock_copy2, mock_makedirs, mock_listdir):
        """
        Scenario: Successfully convert PDF to per-page PPMs

        Given a PDFConverter with mocked subprocess
        When run is called and pdftoppm succeeds
        Then progress should be set to 1.0
        And no error should be set
        And page_count should reflect number of pages
        """
        mock_mkdtemp.return_value = "/tmp/test"
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b"", b"")
        mock_popen.return_value = mock_process
        mock_listdir.return_value = ["page-0001.ppm", "page-0002.ppm", "page-0003.ppm"]

        converter = PDFConverter("input.pdf", "/tmp/outdir")
        converter.run()

        assert converter._progress == 1.0
        assert converter.error is None
        assert converter.page_count == 3
        assert len(converter.page_paths) == 3
        assert mock_copy2.call_count == 3

    @patch("subprocess.Popen")
    @patch("tempfile.mkdtemp")
    @patch("shutil.rmtree")
    def test_run_pdftoppm_failure(self, mock_rmtree, mock_mkdtemp, mock_popen):
        """
        Scenario: Handle pdftoppm conversion failure

        Given a PDFConverter with mocked subprocess
        When run is called and pdftoppm fails with non-zero exit code
        Then error should be set with failure message
        And progress should be set to 1.0
        """
        mock_mkdtemp.return_value = "/tmp/test"
        mock_process = Mock()
        mock_process.returncode = 1
        mock_process.communicate.return_value = (b"Error", b"")
        mock_popen.return_value = mock_process

        converter = PDFConverter("input.pdf", "/tmp/outdir")
        converter.run()

        assert converter.error is not None
        assert "conversion failed" in converter.error
        assert converter._progress == 1.0

    @patch("os.listdir")
    @patch("os.makedirs")
    @patch("shutil.copy2")
    @patch("subprocess.Popen")
    @patch("tempfile.mkdtemp")
    @patch("shutil.rmtree")
    def test_run_cleans_tmpdir(self, mock_rmtree, mock_mkdtemp, mock_popen, mock_copy2, mock_makedirs, mock_listdir):
        """
        Scenario: Clean up temporary directory after conversion

        Given a PDFConverter with mocked subprocess
        When run is called
        Then the temporary directory should be removed after conversion
        """
        mock_mkdtemp.return_value = "/tmp/test"
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b"", b"")
        mock_popen.return_value = mock_process
        mock_listdir.return_value = ["page-0001.ppm"]

        converter = PDFConverter("input.pdf", "/tmp/outdir")
        converter.run()
        mock_rmtree.assert_called_once_with("/tmp/test", ignore_errors=True)

    def test_str_representation(self):
        """
        Scenario: Get string representation

        Given a PDFConverter instance
        When str() is called
        Then it should return the expected format
        """
        converter = PDFConverter("input.pdf", "/tmp/outdir")
        assert str(converter) == "PDFConverter(input.pdf, /tmp/outdir)"

    def test_repr_representation(self):
        """
        Scenario: Get repr representation

        Given a PDFConverter instance
        When repr() is called
        Then it should return the expected format
        """
        converter = PDFConverter("input.pdf", "/tmp/outdir")
        assert repr(converter) == "PDFConverter('input.pdf', '/tmp/outdir')"

    @patch("subprocess.Popen")
    def test_run_calls_pdftoppm_with_resolution(self, mock_popen):
        """
        Scenario: Verify pdftoppm is called with correct resolution

        Given a PDFConverter with custom resolution
        When run is called
        Then pdftoppm should be invoked with the -r flag and resolution value
        """
        mock_process = Mock()
        mock_process.returncode = 1
        mock_process.communicate.return_value = (b"", b"")
        mock_popen.return_value = mock_process

        converter = PDFConverter("input.pdf", "/tmp/outdir")
        converter.resolution = 200

        with patch("tempfile.mkdtemp", return_value="/tmp/test"), patch("shutil.rmtree"):
            converter.run()

        call_args = mock_popen.call_args[0][0]
        assert "-r" in call_args
        assert "200" in call_args

    @patch("os.listdir")
    @patch("os.makedirs")
    @patch("shutil.copy2")
    @patch("subprocess.Popen")
    @patch("tempfile.mkdtemp")
    @patch("shutil.rmtree")
    def test_run_organizes_per_page_ppms(
        self, mock_rmtree, mock_mkdtemp, mock_popen, mock_copy2, mock_makedirs, mock_listdir
    ):
        """
        Scenario: Organize per-page PPMs with predictable filenames

        Given a PDFConverter with mocked subprocess that produced per-page PPMs
        When run is called
        Then each page should be copied to outdir as page_0000.ppm, page_0001.ppm, etc.
        """
        mock_mkdtemp.return_value = "/tmp/test"
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b"", b"")
        mock_popen.return_value = mock_process
        mock_listdir.return_value = ["page-0001.ppm", "page-0002.ppm"]

        converter = PDFConverter("input.pdf", "/tmp/outdir")
        converter.run()

        assert converter.page_count == 2
        assert converter.page_paths[0] == "/tmp/outdir/page_0000.ppm"
        assert converter.page_paths[1] == "/tmp/outdir/page_0001.ppm"
        mock_makedirs.assert_called_once_with("/tmp/outdir", exist_ok=True)

    @patch("os.listdir")
    @patch("os.makedirs")
    @patch("shutil.copy2")
    @patch("subprocess.Popen")
    @patch("tempfile.mkdtemp")
    @patch("shutil.rmtree")
    def test_run_handles_organize_exception(
        self, mock_rmtree, mock_mkdtemp, mock_popen, mock_copy2, mock_makedirs, mock_listdir
    ):
        """
        Scenario: Handle exception during per-page organization

        Given a PDFConverter where os.listdir raises an exception
        When run is called
        Then the error should be caught and stored
        """
        mock_mkdtemp.return_value = "/tmp/test"
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b"", b"")
        mock_popen.return_value = mock_process
        mock_listdir.side_effect = OSError("Permission denied")

        converter = PDFConverter("input.pdf", "/tmp/outdir")
        converter.run()

        assert converter.error is not None
        assert "Error organizing per-page PPMs" in converter.error
        assert converter._progress == 1.0
