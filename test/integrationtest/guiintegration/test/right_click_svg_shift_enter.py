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

"""Step: Right-click SVG to open modify dialog with Ctrl+Enter accept."""

from __future__ import annotations

from typing import TYPE_CHECKING

from guiintegration.conf import DEFAULT_DELAY_MS
from guiintegration.utilities.qt_simulation import simulate_mouse_click, wait
from guiintegration.utilities.scene_helpers import accept_open_dialog_via_ctrl_enter, ensure_test_scene_loaded
from PySide6.QtCore import QPoint, Qt

if TYPE_CHECKING:
    from guiintegration.main import GUITestContext


def run(ctx: GUITestContext) -> None:
    ctx.log.section("MOUSE RIGHT-CLICK - SVG MODIFICATION (Ctrl+Enter ACCEPT)")
    ensure_test_scene_loaded(ctx)
    zui = ctx.window.zui
    svg_center = QPoint(int(zui.width() * 0.22), int(zui.height() * 0.70))
    ctx.log.action("Right-click on SVG, accepting modify dialog with Ctrl+Enter")
    accept_open_dialog_via_ctrl_enter(ctx)
    simulate_mouse_click(ctx, svg_center, Qt.RightButton)
    wait(ctx, DEFAULT_DELAY_MS, "Observe: SVG modification dialog accepted via Ctrl+Enter")
    ctx.log.success("SVG modification dialog accepted with Ctrl+Enter")
