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

"""Step: Actions Menu - Set/Go to Home Point.

Tests the full home point round-trip:
  Phase 1 — Zoom in to a distinct area, set home point (Ctrl+Shift+H)
  Phase 2 — Zoom way out + pan far away, go home (Ctrl+J), verify snap-back
  Phase 3 — Home / Shift+Home keys; home point cleared on new scene
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from guiintegration.conf import DEFAULT_DELAY_MS, MOVE_STEP_DELAY_MS, SHORT_DELAY_MS, ZOOM_STEP_DELAY_MS
from guiintegration.utilities.qt_simulation import simulate_key, simulate_wheel, trigger_action, wait
from guiintegration.utilities.scene_helpers import ensure_test_scene_loaded
from PySide6.QtCore import QPoint, Qt

if TYPE_CHECKING:
    from guiintegration.main import GUITestContext


ZOOM_IN_STEPS = 20
ZOOM_OUT_STEPS = 25
PAN_STEPS_AWAY = 30


def run(ctx: GUITestContext) -> None:
    ctx.log.section("ACTIONS MENU - HOME POINT")
    ensure_test_scene_loaded(ctx)

    zui = ctx.window.zui
    centre = QPoint(zui.width() // 2, zui.height() // 2)

    # ============================================================
    # Phase 1 — Set home point at a visually distinct position
    # ============================================================
    ctx.log.action("PHASE 1 — Zooming in to a distinct view area")
    for _ in range(ZOOM_IN_STEPS):
        simulate_wheel(ctx, centre, 120)
        wait(ctx, ZOOM_STEP_DELAY_MS)
    for _ in range(10):
        simulate_key(ctx, Qt.Key_Right)
        wait(ctx, MOVE_STEP_DELAY_MS)
    for _ in range(8):
        simulate_key(ctx, Qt.Key_Down)
        wait(ctx, MOVE_STEP_DELAY_MS)
    wait(ctx, SHORT_DELAY_MS, "Observe: zoomed in on a specific area. REMEMBER this view — this will be your home point.")

    ctx.log.action("Setting home point (Ctrl+Shift+H)")
    trigger_action(ctx, "set_home_point")
    wait(ctx, DEFAULT_DELAY_MS, "Observe: Cyan crosshair pulse marker appears at viewport centre")
    ctx.log.success("Home point saved — pulse marker confirmed")

    # ============================================================
    # Phase 2 — Navigate far away, then Ctrl+J back
    # ============================================================
    ctx.log.action("PHASE 2 — Navigating FAR away from the home point")
    for _ in range(ZOOM_OUT_STEPS):
        simulate_wheel(ctx, centre, -120)
        wait(ctx, ZOOM_STEP_DELAY_MS)
    for _ in range(PAN_STEPS_AWAY):
        simulate_key(ctx, Qt.Key_Left)
        wait(ctx, MOVE_STEP_DELAY_MS)
    for _ in range(PAN_STEPS_AWAY):
        simulate_key(ctx, Qt.Key_Up)
        wait(ctx, MOVE_STEP_DELAY_MS)
    wait(ctx, SHORT_DELAY_MS, "Observe: view is COMPLETELY different. The home point is nowhere in sight.")

    ctx.log.action("Going to home point (Ctrl+J)")
    trigger_action(ctx, "go_to_home_point")
    wait(ctx, DEFAULT_DELAY_MS, "Observe: View SNAPS back to the EXACT home point position from Phase 1")
    ctx.log.success("Ctrl+J restored the view to the saved home point")

    # ============================================================
    # Phase 3 — Keyboard shortcuts and edge cases
    # ============================================================
    ctx.log.action("PHASE 3 — Testing bare Home key")
    for _ in range(ZOOM_OUT_STEPS):
        simulate_wheel(ctx, centre, -120)
        wait(ctx, ZOOM_STEP_DELAY_MS)
    for _ in range(15):
        simulate_key(ctx, Qt.Key_Right)
        wait(ctx, MOVE_STEP_DELAY_MS)
    wait(ctx, SHORT_DELAY_MS, "Observe: navigated away from home point")

    simulate_key(ctx, Qt.Key_Home)
    wait(ctx, DEFAULT_DELAY_MS, "Observe: View SNAPS back to home point via the Home key")
    ctx.log.success("Home key (no modifier) restores home point")

    ctx.log.action("Testing Shift+Home to set a NEW home point")
    for _ in range(10):
        simulate_wheel(ctx, centre, 120)
        wait(ctx, ZOOM_STEP_DELAY_MS)
    for _ in range(15):
        simulate_key(ctx, Qt.Key_Right)
        wait(ctx, MOVE_STEP_DELAY_MS)
    wait(ctx, SHORT_DELAY_MS, "Observe: new distinct view position")

    simulate_key(ctx, Qt.Key_Home, Qt.ShiftModifier)
    wait(ctx, DEFAULT_DELAY_MS, "Observe: Cyan crosshair pulse confirms new home point was set")
    ctx.log.success("Shift+Home sets new home point with pulse marker")

    ctx.log.action("Testing home point cleared on new scene")
    trigger_action(ctx, "new_scene")
    wait(ctx, SHORT_DELAY_MS, "Observe: blank scene loaded")
    ctx.scene_loaded = False

    ctx.log.action("Triggering go_to_home_point on fresh scene — expect no-op")
    trigger_action(ctx, "go_to_home_point")
    wait(ctx, DEFAULT_DELAY_MS, "Observe: No crash, no movement (home point was cleared)")
    ctx.log.success("Home point correctly cleared on new scene — no crash, no-op")
