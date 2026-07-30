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

"""Step: OCR screenshot - select PDF area, extract text, create string media object."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING
from unittest.mock import patch

from guiintegration.conf import DEFAULT_DELAY_MS, SHORT_DELAY_MS
from guiintegration.utilities.qt_simulation import (
    simulate_key,
    simulate_mouse_click,
    simulate_mouse_drag,
    trigger_action,
    wait,
    wait_for_image_load,
)
from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QApplication, QDialog, QFileDialog

if TYPE_CHECKING:
    from guiintegration.main import GUITestContext


def run(ctx: GUITestContext) -> None:
    ctx.log.section("OCR SCREENSHOT")

    try:
        import pytesseract  # noqa: F401
    except ImportError:
        ctx.log.warning("pytesseract not installed - skipping OCR screenshot test")
        return

    try:
        pytesseract.get_tesseract_version()
    except Exception:
        ctx.log.warning(
            "Tesseract OCR engine not found on system PATH - skipping OCR screenshot test"
        )
        return

    test_pdf_path = os.path.join(ctx.project_root, "zooui", "data", "test_pdf.pdf")
    if not os.path.exists(test_pdf_path):
        ctx.log.warning(f"Test PDF not found: {test_pdf_path}")
        return

    zui = ctx.window.zui

    # Clear previous content and start fresh
    trigger_action(ctx, "new_scene")
    wait(ctx, SHORT_DELAY_MS, "Starting with blank scene")

    # Open the test PDF
    ctx.log.action("Opening test PDF for OCR extraction")
    with patch.object(QFileDialog, "getOpenFileName", return_value=(test_pdf_path, "")):
        trigger_action(ctx, "open_media_local")

    # Wait for PDF conversion + tiling
    ctx.log.action("Waiting for PDF to convert and tile...")
    pdf_load_total = SHORT_DELAY_MS * 2
    elapsed = 0
    chunk = 1000
    while elapsed < pdf_load_total:
        wait(ctx, chunk, f"PDF loading... ({elapsed}ms / {pdf_load_total}ms)")
        elapsed += chunk
    wait_for_image_load(ctx, "PDF first page loaded and tiled")

    ctx.log.success("PDF loaded - Page 1 should be visible")

    # Click on the PDF to select it and set mouse position
    ctx.log.action("Clicking the PDF to set mouse position")
    centre = QPoint(zui.width() // 2, zui.height() // 2)
    simulate_mouse_click(ctx, centre)
    wait(ctx, DEFAULT_DELAY_MS, "PDF selected, mouse position set")

    # Zoom in to make text readable by tesseract
    ctx.log.action("Zooming in for readable text")
    for _ in range(12):
        simulate_key(ctx, Qt.Key_PageUp)
        wait(ctx, DEFAULT_DELAY_MS, "Zoom")
    for _ in range(5):
        simulate_key(ctx, Qt.Key_Left)
        wait(ctx, DEFAULT_DELAY_MS, "Pan left")
    for _ in range(12):
        simulate_key(ctx, Qt.Key_Down)
        wait(ctx, DEFAULT_DELAY_MS, "Pan down")

    # Let the rendering pipeline settle before attempting grab()
    zui.repaint()
    ctx.app.processEvents()
    wait(ctx, SHORT_DELAY_MS, "Warming paint engine before OCR")

    ctx.log.success("PDF loaded and zoomed")

    # Enter OCR screenshot mode
    ctx.log.action("Activating OCR screenshot mode")
    trigger_action(ctx, "ocr_screenshot")
    wait(ctx, DEFAULT_DELAY_MS, "OCR mode active (crosshair cursor)")

    # Repeating timer to auto-accept the string input dialog when it opens
    from PySide6 import QtCore as _QtCore

    def _accept_dialog():
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QDialog) and widget.isVisible():
                if widget.windowTitle() == "String input:":
                    ctx.log.detail("Auto-accepting string input dialog")
                    widget.accept()
                    break

    dialog_timer = _QtCore.QTimer()
    dialog_timer.timeout.connect(_accept_dialog)
    dialog_timer.start(1000)

    # Drag-select the top-left area of the viewport for OCR
    ctx.log.action("Drag-selecting top-left area for OCR")
    w = zui.width()
    h = zui.height()
    start = QPoint(w // 8, h // 8)
    end = QPoint(w // 2, h // 2)
    simulate_mouse_drag(ctx, start, end)
    wait(ctx, SHORT_DELAY_MS * 5, "OCR capture + dialog")
    dialog_timer.stop()

    # Drain pending paint events to settle before subsequent steps
    zui.repaint()
    ctx.app.processEvents()
    wait(ctx, SHORT_DELAY_MS, "Settling paint state")