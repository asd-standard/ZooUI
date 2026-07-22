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

"""Multi-page PDF rendered as individually tiled pages with page navigation."""

import glob as _glob
import os
import tempfile
from typing import Any

from PySide6 import QtCore, QtWidgets

from zooui.converters import converterrunner
from zooui.logger import get_logger
from zooui.tilesystem import tilemanager as TileManager
from zooui.tilesystem.tiler.tilerrunner import TilingHandle, submit_tiling

from .tiledmediaobject import TiledMediaObject


class _BlockingConverter:
    """Dummy converter whose progress never reaches 1.0.

    Used to prevent TiledMediaObject.render() from calling __run_tiler()
    while PdfMediaObject manages page-specific tiling externally.
    """

    progress: float = 0.0


class PdfMediaObject(TiledMediaObject):
    """
    Constructor :
        PdfMediaObject(pdf_path, scene, autofit, start_page)
    Parameters :
        pdf_path : str
        scene : Scene
        autofit : bool (default=True)
        start_page : int (default=0)

    PdfMediaObject(pdf_path, scene, autofit, start_page) --> None

    A multi-page PDF rendered as individually tiled pages in the ZUI.

    Each page is rasterized as a separate PPM and tiled independently.
    Page navigation is controlled via Ctrl+Up/Down and Ctrl+Alt+G (go to page).

    A lazy 2-page tiling buffer tiles the current page and the next page,
    providing instant display on forward navigation.
    """

    def __init__(self, pdf_path: str, scene: Any, autofit: bool = True, start_page: int = 0) -> None:
        """
        Constructor :
            PdfMediaObject(pdf_path, scene, autofit, start_page)
        Parameters :
            pdf_path : str
            scene : Scene
            autofit : bool (default=True)
            start_page : int (default=0)

        PdfMediaObject(pdf_path, scene, autofit, start_page) --> None

        Initialize a new PdfMediaObject from the PDF at pdf_path.

        Sets up deferred initialization — the PDF is converted in a background
        process, then pages are tiled lazily with a 2-page buffer.
        """
        TiledMediaObject.__init__(self, pdf_path, scene, autofit, deferred=True)

        self._pdf_path: str = pdf_path
        self._start_page: int = max(0, start_page)
        self._page_count: int = 0
        self._current_page: int = 0
        self._page_ppm_paths: list[str] = []
        self._page_tilers: dict[int, TilingHandle] = {}
        self._page_tiling: set[int] = set()
        self._page_tiled: set[int] = set()
        self._pending_nav_direction: int | None = None
        self._logger = get_logger(f"PdfMediaObject.{pdf_path}")

        self._outdir: str = tempfile.mkdtemp(prefix="zooui_pdf_")

        future = converterrunner.submit_pdf_conversion(pdf_path, self._outdir)
        self.__pdf_converter = converterrunner.ConversionHandle(future, pdf_path, self._outdir)

        self._dummy_converter = _BlockingConverter()

        self._media_id = f"{pdf_path}:page:{self._current_page}"

    @property
    def current_page(self) -> int:
        """Zero-based index of the current page."""
        return self._current_page

    @property
    def page_count(self) -> int:
        """Total number of pages in the PDF (0 while loading)."""
        return self._page_count

    @property
    def current_page_label(self) -> str:
        """Human-readable page label, e.g. 'Page 3/42'."""
        if self._page_count:
            return f"Page {self._current_page + 1}/{self._page_count}"
        return "Loading..."

    def change_page(self, delta: int) -> None:
        """Navigate by delta pages (-1 = previous, +1 = next)."""
        if self._page_count <= 1:
            return
        new_page = max(0, min(self._page_count - 1, self._current_page + delta))
        if new_page == self._current_page:
            return
        self._pending_nav_direction = 1 if delta > 0 else -1
        self._current_page = new_page
        new_media_id = f"{self._pdf_path}:page:{new_page}"
        self._reset_for_page(new_media_id)
        self._ensure_page_tiling(new_page)
        self._maintain_buffer()

    def _try_load(self) -> None:
        """Override to apply smart positioning when a page finishes loading."""
        was_loaded = self._loaded
        super()._try_load()
        if not was_loaded and self._loaded and self._pending_nav_direction is not None:
            direction = self._pending_nav_direction
            self._pending_nav_direction = None
            viewport_w, viewport_h = self._scene.viewport_size
            if direction > 0:
                current_tl = self.topleft
                self.move(-current_tl[0], -current_tl[1])
            else:
                current_br = self.bottomright
                self.move(viewport_w - current_br[0], viewport_h - current_br[1])

    def go_to_page(self, page_number: int) -> None:
        """Jump directly to a page (1-indexed)."""
        if not 1 <= page_number <= self._page_count:
            return
        page_idx = page_number - 1
        delta = page_idx - self._current_page
        self.change_page(delta)

    def handle_key(self, key: int, modifiers: QtCore.Qt.KeyboardModifier) -> bool:
        """Handle page navigation keys. Returns True if consumed."""
        if self._page_count <= 0:
            return False
        if modifiers & QtCore.Qt.ControlModifier:
            if key == QtCore.Qt.Key_Up:
                self.change_page(-1)
                return True
            elif key == QtCore.Qt.Key_Down:
                self.change_page(1)
                return True
            elif key == QtCore.Qt.Key_G and (modifiers & QtCore.Qt.AltModifier):
                self._show_go_to_page_dialog()
                return True
        return False

    def render(self, painter: Any, mode: int) -> None:
        """Override render to manage page lifecycle and prevent premature tiling."""
        self._check_conversion_complete()

        if not self._page_count:
            self._TiledMediaObject__converter = self._dummy_converter
            super().render(painter, mode)
            return

        self._check_page_tiling()

        page_media_id = f"{self._pdf_path}:page:{self._current_page}"

        if not TileManager.tiled(page_media_id) and self._current_page not in self._page_tiled:
            self._ensure_page_tiling(self._current_page)
            self._maintain_buffer()
            self._TiledMediaObject__converter = self._dummy_converter
        elif self._TiledMediaObject__converter is self._dummy_converter:
            self._TiledMediaObject__converter = None  # type: ignore[assignment]

        super().render(painter, mode)

    def _on_conversion_complete(self) -> None:
        """Handle PDF conversion completion: discover pages and start tiling."""
        ppm_files = sorted(_glob.glob(os.path.join(self._outdir, "page_*.ppm")))
        if not ppm_files:
            self._logger.error("PDF conversion produced no pages")
            self._TiledMediaObject__converter = None  # type: ignore[assignment]
            return

        self._page_count = len(ppm_files)
        self._page_ppm_paths = ppm_files
        self._logger.info("PDF converted: %d pages", self._page_count)

        if self._start_page >= self._page_count:
            self._start_page = 0
        self._current_page = self._start_page

        new_media_id = f"{self._pdf_path}:page:{self._current_page}"
        self._reset_for_page(new_media_id)
        self._ensure_page_tiling(self._current_page)
        self._maintain_buffer()
        self._TiledMediaObject__converter = None  # type: ignore[assignment]

    def _check_conversion_complete(self) -> None:
        """Check if the PDF conversion process has finished."""
        if self._page_count > 0:
            return
        if self.__pdf_converter and self.__pdf_converter.progress == 1.0:
            if self.__pdf_converter.error:
                self._logger.error("PDF conversion failed: %s", self.__pdf_converter.error)
                self._TiledMediaObject__converter = None  # type: ignore[assignment]
                return
            self._on_conversion_complete()

    def _check_page_tiling(self) -> None:
        """Check if the current page's tiling process has finished."""
        page = self._current_page
        tiler = self._page_tilers.get(page)
        if tiler is not None and tiler.progress == 1.0:
            page_media_id = f"{self._pdf_path}:page:{page}"
            if TileManager.tiled(page_media_id):
                self._page_tiled.add(page)
                self._page_tiling.discard(page)
                del self._page_tilers[page]

    def _ensure_page_tiling(self, page_idx: int) -> None:
        """Ensure that a page has been submitted for tiling, unless already done."""
        if page_idx < 0 or page_idx >= self._page_count:
            return
        page_media_id = f"{self._pdf_path}:page:{page_idx}"
        if TileManager.tiled(page_media_id):
            self._page_tiled.add(page_idx)
            return
        if page_idx in self._page_tiling or page_idx in self._page_tiled:
            return
        self._start_tiling_page(page_idx)

    def _maintain_buffer(self) -> None:
        """Maintain 2-page lazy buffer: current page + next page."""
        for p in (self._current_page, self._current_page + 1):
            if 0 <= p < self._page_count:
                self._ensure_page_tiling(p)

    def _start_tiling_page(self, page_idx: int) -> None:
        """Submit a tiling job for a specific page's PPM."""
        ppm_path = self._page_ppm_paths[page_idx]
        page_media_id = f"{self._pdf_path}:page:{page_idx}"
        try:
            future = submit_tiling(ppm_path, page_media_id, "png")
            self._page_tilers[page_idx] = TilingHandle(future, ppm_path, page_media_id)
            self._page_tiling.add(page_idx)
        except Exception as e:
            self._logger.error("Failed to start tiling for page %d: %s", page_idx, e)

    def _show_go_to_page_dialog(self) -> None:
        """Show a dialog to jump to a specific page number."""
        page_num, ok = QtWidgets.QInputDialog.getInt(
            None,
            "Go to Page",
            f"Enter page number (1\u2013{self._page_count}):",
            self._current_page + 1,
            1,
            self._page_count,
        )
        if ok:
            self.go_to_page(page_num)
