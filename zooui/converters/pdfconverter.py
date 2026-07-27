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
from typing import Any

from .converter import Converter


class _DummyFont:
    """Sentinel used when PIL is not available for page numbering."""

    pass


class PDFConverter(Converter):
    """
    Constructor :
        PDFConverter(infile, outdir, page_numbering)
    Parameters :
        infile : str
        outdir : str
        page_numbering : bool (default=True)

    PDFConverter(infile, outdir, page_numbering) --> None

    PDFConverter objects are used for rasterizing PDFs to per-page PPM files.

    Each page is rasterized as a separate PPM file in the output directory:
    ``outdir/page_0000.ppm``, ``outdir/page_0001.ppm``, etc.

    If ``page_numbering`` is True (default), a page number label
    (``"N / total"``) is drawn onto each PPM image in the bottom-right
    corner before copying to the output directory.

    The output format will always be PPM irrespective of the file extension of
    the output file. If another output format is required then :class:`PDFConverter`
    should be used in conjunction with :class:`VipsConverter`.
    """

    def __init__(self, infile: str, outdir: str, page_numbering: bool = True) -> None:
        """
        Constructor :
            PDFConverter(infile, outdir, page_numbering)
        Parameters :
            infile : str
            outdir : str
            page_numbering : bool (default=True)

        PDFConverter(infile, outdir, page_numbering) --> None

        Create a new PDFConverter for rasterizing PDF files.

        The infile parameter is the path to the source PDF file.
        The outdir parameter is the directory where per-page PPM files will
        be written. The default resolution is 300 DPI.

        If page_numbering is True, each page PPM will have a ``"N / total"``
        label drawn in the bottom-right corner.
        """
        Converter.__init__(self, infile, outdir)

        self.resolution = 300
        self.page_count = 0
        self.page_paths: list[str] = []
        self.page_numbering = page_numbering

    @staticmethod
    def _load_page_number_font(font_size: int) -> Any:
        """Load a font for drawing page numbers, falling back gracefully.

        Tries common system TrueType fonts first, then falls back to
        PIL's built-in default bitmap font.
        """
        try:
            from PIL import ImageFont
        except ImportError:
            return _DummyFont()

        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans.ttf",
            "/usr/share/fonts/TTF/DejaVuSans.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/HelveticaNeue.ttc",
            "C:\\Windows\\Fonts\\arial.ttf",
        ]
        for path in font_paths:
            if os.path.isfile(path):
                try:
                    return ImageFont.truetype(path, size=font_size)
                except OSError:
                    continue
        return ImageFont.load_default()

    def _draw_page_numbers(self, tmpdir: str, page_files: dict[int, str]) -> None:
        """Draw ``"N / total"`` labels onto each page PPM in-place.

        Parameters:
            tmpdir: Directory containing raw pdftoppm output.
            page_files: Mapping of 1-based page number → filename in tmpdir.
        """
        try:
            from PIL import Image, ImageDraw
        except ImportError:
            self._logger.warning("PIL not available — skipping page numbering")
            return

        num_pages = len(page_files)
        self._logger.info("drawing page numbers on %d pages", num_pages)

        for i in range(num_pages):
            src = os.path.join(tmpdir, page_files[i + 1])
            try:
                img = Image.open(src)
                if img.mode != "RGB":
                    img = img.convert("RGB")
                w, h = img.size

                font_size = int(min(w, h) * 0.03)
                font_size = max(24, min(font_size, 200))
                font = self._load_page_number_font(font_size)

                label = f"{i + 1} / {num_pages}"

                draw = ImageDraw.Draw(img)
                bbox = draw.textbbox((0, 0), label, font=font)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
                margin = max(1, font_size // 4)

                box_x1 = w - text_w - margin * 2
                box_y1 = h - text_h - margin * 2
                box_x2 = w
                box_y2 = h

                draw.rectangle(
                    [box_x1, box_y1, box_x2, box_y2],
                    fill=(32, 32, 32),
                )
                draw.text(
                    (box_x1 + margin, box_y1 + margin),
                    label,
                    fill=(255, 255, 255),
                    font=font,
                )

                img.save(src)
            except Exception as e:
                self._logger.warning("failed to number page %d: %s", i + 1, e)

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

        If page_numbering is True, a ``"N / total"`` label is drawn onto
        each page PPM before copying.

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
                self._progress = 0.5

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

                if self.page_numbering and num_pages > 0:
                    self._progress = 0.55
                    self._draw_page_numbers(tmpdir, page_files)

                self._logger.info("organizing per-page PPMs")
                self._progress = 0.7

                outdir = self._outfile
                os.makedirs(outdir, exist_ok=True)

                self.page_paths = []
                for i in range(num_pages):
                    src = os.path.join(tmpdir, page_files[i + 1])
                    dst = os.path.join(outdir, f"page_{i:04d}.ppm")
                    shutil.copy2(src, dst)
                    self.page_paths.append(dst)

                self.page_count = num_pages
                self._logger.info("converted %d pages", num_pages)

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
