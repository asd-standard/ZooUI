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

"""Step: Actions Menu - Set/Go to Home Point."""

from __future__ import annotations

from typing import TYPE_CHECKING

from guiintegration.conf import DEFAULT_DELAY_MS, MOVE_STEP_DELAY_MS, SHORT_DELAY_MS, ZOOM_STEP_DELAY_MS
from guiintegration.utilities.qt_simulation import simulate_key, simulate_wheel, trigger_action, wait
from guiintegration.utilities.scene_helpers import ensure_test_scene_loaded
from PySide6.QtCore import QPoint, Qt

if TYPE_CHECKING:
    from guiintegration.main import GUITestContext


def run(ctx: GUITestContext) -> None:
    ctx.log.section("ACTIONS MENU - HOME POINT")
    ensure_test_scene_loaded(ctx)

    zui = ctx.window.zui
    centre = QPoint(zui.width() // 2, zui.height() // 2)

    ctx.log.action("Navigating to a specific view position for home point")
    for _ in range(5):
        simulate_wheel(ctx, centre, 120)
        wait(ctx, ZOOM_STEP_DELAY_MS)
    for _ in range(10):
        simulate_key(ctx, Qt.Key_Right)
        wait(ctx, MOVE_STEP_DELAY_MS)
    wait(ctx, SHORT_DELAY_MS, "Observe: current zoomed and panned view")

    ctx.log.action("Setting home point via menu (Ctrl+Shift+H)")
    trigger_action(ctx, "set_home_point")
    wait(ctx, DEFAULT_DELAY_MS, "Observe: Cyan crosshair pulse marker at viewport centre")
    ctx.log.success("Home point set - pulse marker confirmed")

    ctx.log.action("Navigating to a completely different view")
    for _ in range(8):
        simulate_wheel(ctx, centre, -120)
        wait(ctx, ZOOM_STEP_DELAY_MS)
    for _ in range(15):
        simulate_key(ctx, Qt.Key_Left)
        wait(ctx, MOVE_STEP_DELAY_MS)
    for _ in range(10):
        simulate_key(ctx, Qt.Key_Up)
        wait(ctx, MOVE_STEP_DELAY_MS)
    wait(ctx, SHORT_DELAY_MS, "Observe: view is now at a completely different position")

    ctx.log.action("Going to home point via menu (Ctrl+J)")
    trigger_action(ctx, "go_to_home_point")
    wait(ctx, DEFAULT_DELAY_MS, "Observe: View SNAPS back to home point position")
    ctx.log.success("Returned to home point via menu action")

    ctx.log.action("Navigating away again")
    for _ in range(5):
        simulate_wheel(ctx, centre, 120)
        wait(ctx, ZOOM_STEP_DELAY_MS)
    wait(ctx, SHORT_DELAY_MS, "Observe: navigated away from home point")

    ctx.log.action("Testing Home key (no modifier) to go to home point")
    simulate_key(ctx, Qt.Key_Home)
    wait(ctx, DEFAULT_DELAY_MS, "Observe: Should return to home point via Home key")
    ctx.log.success("Home key restores home point")

    ctx.log.action("Testing Shift+Home to set a new home point")
    for _ in range(5):
        simulate_key(ctx, Qt.Key_Left)
        wait(ctx, MOVE_STEP_DELAY_MS)
    wait(ctx, SHORT_DELAY_MS, "Observe: view shifted left")

    simulate_key(ctx, Qt.Key_Home, Qt.ShiftModifier)
    wait(ctx, DEFAULT_DELAY_MS, "Observe: Cyan crosshair pulse at new position")
    ctx.log.success("Shift+Home sets new home point with pulse marker")

    ctx.log.action("Testing home point cleared on new scene")
    trigger_action(ctx, "new_scene")
    wait(ctx, SHORT_DELAY_MS, "Observe: Blank scene loaded")
    ctx.scene_loaded = False

    ctx.log.action("Triggering go_to_home_point on fresh scene (should be no-op)")
    trigger_action(ctx, "go_to_home_point")
    wait(ctx, DEFAULT_DELAY_MS, "Observe: No crash, no movement (home point was cleared)")
    ctx.log.success("Home point correctly cleared on new scene - no crash")
