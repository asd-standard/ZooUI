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

"""Step: PDF page navigation - forward, backward, go-to-page dialog."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING
from unittest.mock import patch

from guiintegration.conf import DEFAULT_DELAY_MS, SHORT_DELAY_MS
from guiintegration.utilities.qt_simulation import (
    simulate_key,
    simulate_mouse_click,
    trigger_action,
    wait,
    wait_for_image_load,
)
from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QFileDialog

if TYPE_CHECKING:
    from guiintegration.main import GUITestContext


def run(ctx: GUITestContext) -> None:
    ctx.log.section("PDF PAGE NAVIGATION")

    test_pdf_path = os.path.join(ctx.project_root, "data", "test_pdf.pdf")
    if not os.path.exists(test_pdf_path):
        ctx.log.warning(f"Test PDF not found: {test_pdf_path}")
        return

    zui = ctx.window.zui
    scene = zui.scene

    # Clear previous content and start fresh
    trigger_action(ctx, "new_scene")
    wait(ctx, SHORT_DELAY_MS, "Starting with blank scene")

    # Place a position marker (small red rectangle SVG) at the top-left
    # of the viewport as a visual anchor to verify no accidental dragging
    ctx.log.action("Adding position marker (red square) as visual anchor")
    marker_svg = os.path.join(ctx.temp_dir, "__pdf_nav_marker.svg")
    with open(marker_svg, "w") as f:
        f.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32">\n'
            '  <rect x="0" y="0" width="32" height="32" fill="red" stroke="white" stroke-width="4"/>\n'
            '  <line x1="4" y1="16" x2="28" y2="16" stroke="white" stroke-width="2"/>\n'
            '  <line x1="16" y1="4" x2="16" y2="28" stroke="white" stroke-width="2"/>\n'
            "</svg>"
        )

    from zooui.objects.mediaobjects.svgmediaobject import SVGMediaObject

    marker = SVGMediaObject(marker_svg, scene)
    marker.fit((5, 5, 35, 35))
    scene.add(marker)
    ctx.app.processEvents()
    wait(ctx, DEFAULT_DELAY_MS, "Position marker placed at top-left")

    # Open the test PDF
    ctx.log.action("Opening test PDF (3 pages)")
    with patch.object(QFileDialog, "getOpenFileName", return_value=(test_pdf_path, "")):
        trigger_action(ctx, "open_media_local")

    # Wait for PDF conversion + tiling
    ctx.log.action("Waiting for PDF to convert and tile...")
    pdf_load_total = SHORT_DELAY_MS * 5  # 10 seconds for conversion + tiling
    elapsed = 0
    chunk = 1000
    while elapsed < pdf_load_total:
        wait(ctx, chunk, f"PDF loading... ({elapsed}ms / {pdf_load_total}ms)")
        elapsed += chunk
    wait_for_image_load(ctx, "PDF first page loaded and tiled")

    ctx.log.success("PDF loaded - Page 1 should be visible")
    wait(ctx, SHORT_DELAY_MS, "Observe: PDF Page 1 ('Page 1 - PDF Navigation') with red marker at top-left")

    # Click on the PDF to select it so keyboard shortcuts reach the PdfMediaObject
    ctx.log.action("Clicking the PDF to select it")
    centre = QPoint(zui.width() // 2, zui.height() // 2)
    simulate_mouse_click(ctx, centre)
    wait(ctx, DEFAULT_DELAY_MS, "PDF is now selected")

    # Navigate forward: Ctrl+Down
    ctx.log.action("Pressing Ctrl+Down to go to next page")
    simulate_key(ctx, Qt.Key_Down, Qt.ControlModifier)
    wait_for_image_load(ctx, "Page 2 tiling")
    wait(ctx, SHORT_DELAY_MS, "Observe: PDF Page 2 ('Page 2 - Second Page') - top-left should align with viewport, marker still at top-left")

    # Navigate forward again: Ctrl+Down
    ctx.log.action("Pressing Ctrl+Down to go to page 3")
    simulate_key(ctx, Qt.Key_Down, Qt.ControlModifier)
    wait_for_image_load(ctx, "Page 3 tiling")
    wait(ctx, SHORT_DELAY_MS, "Observe: PDF Page 3 ('Page 3 - Final Page') - top-left aligned, marker at top-left")

    # Navigate backward: Ctrl+Up
    ctx.log.action("Pressing Ctrl+Up to go back to page 2")
    simulate_key(ctx, Qt.Key_Up, Qt.ControlModifier)
    wait_for_image_load(ctx, "Page 2 loaded")
    wait(ctx, SHORT_DELAY_MS, "Observe: PDF Page 2 - bottom-right should align with viewport (going backward)")

    # Navigate backward again: Ctrl+Up
    ctx.log.action("Pressing Ctrl+Up to go back to page 1")
    simulate_key(ctx, Qt.Key_Up, Qt.ControlModifier)
    wait_for_image_load(ctx, "Page 1 loaded")
    wait(ctx, SHORT_DELAY_MS, "Observe: PDF Page 1 - bottom-right aligned (going backward)")

    # Go-to-page dialog: Ctrl+Alt+G
    ctx.log.action("Pressing Ctrl+Alt+G to open go-to-page dialog")
    # Schedule the dialog to be accepted (select page 3)
    from PySide6 import QtCore as _QtCore
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication, QInputDialog, QSpinBox

    def _select_page_3():
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QInputDialog) and widget.isVisible():
                ctx.log.detail(f"Found go-to-page dialog: {widget.windowTitle()}")
                # Find the spinbox and set it to page 3
                for child in widget.findChildren(QSpinBox):
                    child.setValue(3)
                    break
                widget.accept()
                break

    _QtCore.QTimer.singleShot(SHORT_DELAY_MS, _select_page_3)
    simulate_key(ctx, Qt.Key_G, Qt.ControlModifier | Qt.AltModifier)
    wait_for_image_load(ctx, "Jumped to page 3")
    wait(ctx, SHORT_DELAY_MS, "Observe: PDF Page 3 - jumped via go-to-page dialog, top-left aligned")

    ctx.log.success("PDF page navigation test completed")
