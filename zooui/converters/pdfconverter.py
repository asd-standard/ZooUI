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

"""PDF rasterizer based upon either Xpdf or Poppler."""

import os
import shutil
import subprocess
import tempfile

from .converter import Converter


class PDFConverter(Converter):
    """
    Constructor :
        PDFConverter(infile, outdir)
    Parameters :
        infile : str
        outdir : str

    PDFConverter(infile, outdir) --> None

    PDFConverter objects are used for rasterizing PDFs to per-page PPM files.

    Each page is rasterized as a separate PPM file in the output directory:
    ``outdir/page_0000.ppm``, ``outdir/page_0001.ppm``, etc.

    The output format will always be PPM irrespective of the file extension of
    the output file. If another output format is required then :class:`PDFConverter`
    should be used in conjunction with :class:`VipsConverter`.
    """

    def __init__(self, infile: str, outdir: str) -> None:
        """
        Constructor :
            PDFConverter(infile, outdir)
        Parameters :
            infile : str
            outdir : str

        PDFConverter(infile, outdir) --> None

        Create a new PDFConverter for rasterizing PDF files.

        The infile parameter is the path to the source PDF file.
        The outdir parameter is the directory where per-page PPM files will
        be written. The default resolution is 300 DPI.
        """
        Converter.__init__(self, infile, outdir)

        self.resolution = 300
        self.page_count = 0
        self.page_paths: list[str] = []

    def run(self) -> None:
        """
        Method :
            PDFConverter.run()
        Parameters :
            None

        PDFConverter.run() --> None

        Run the PDF conversion using pdftoppm. Creates a temporary directory,
        calls pdftoppm to rasterize the PDF into individual PPM pages, then
        copies each page to the output directory with predictable filenames.

        If any errors are encountered then :attr:`self.error` will be set to a
        string describing the error.
        """
        tmpdir = tempfile.mkdtemp()
        self._logger.info("calling pdftoppm")
        process = subprocess.Popen(
            ["pdftoppm", "-r", str(self.resolution), self._infile, os.path.join(tmpdir, "page")],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        stdout = process.communicate()[0]

        if process.returncode == 0:
            try:
                self._logger.info("organizing per-page PPMs")
                self._progress = 0.5

                outdir = self._outfile
                os.makedirs(outdir, exist_ok=True)

                page_files: dict[int, str] = {}
                for filename in os.listdir(tmpdir):
                    if not filename.startswith("page-"):
                        continue
                    try:
                        page_num = int(filename[5:-4])
                    except ValueError:
                        continue
                    page_files[page_num] = filename

                num_pages = len(page_files)
                self.page_paths = []

                for i in range(num_pages):
                    src = os.path.join(tmpdir, page_files[i + 1])
                    dst = os.path.join(outdir, f"page_{i:04d}.ppm")
                    shutil.copy2(src, dst)
                    self.page_paths.append(dst)

                self.page_count = num_pages
                self._logger.info(f"converted {num_pages} pages")

            except Exception as e:
                self.error = "Error organizing per-page PPMs\n" + str(e)
                self._logger.error(self.error)

        else:
            self.error = f"conversion failed with return code {process.returncode}:\n{stdout!r}"
            self._logger.error(self.error)

        shutil.rmtree(tmpdir, ignore_errors=True)
        self._progress = 1.0

    def __str__(self) -> str:
        """
        Method :
            PDFConverter.__str__()
        Parameters :
            None

        PDFConverter.__str__() --> str

        Return a human-readable string representation of the PDFConverter.
        """
        return f"PDFConverter({self._infile}, {self._outfile})"

    def __repr__(self) -> str:
        """
        Method :
            PDFConverter.__repr__()
        Parameters :
            None

        PDFConverter.__repr__() --> str

        Return a formal string representation of the PDFConverter.
        """
        return f"PDFConverter({self._infile!r}, {self._outfile!r})"
