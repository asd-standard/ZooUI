## PyZUI - Python Zooming User Interface
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

"""Step: Help > Usage — open and close the Usage Instructions dialog."""

from __future__ import annotations

from typing import TYPE_CHECKING

from guiintegration.utilities.qt_simulation import trigger_action, wait
from guiintegration.utilities.scene_helpers import close_open_dialog

if TYPE_CHECKING:
    from guiintegration.main import GUITestContext


def run(ctx: GUITestContext) -> None:
    ctx.log.section("HELP MENU - USAGE")
    ctx.log.action("Showing Usage Instructions dialog")
    close_open_dialog(ctx)
    trigger_action(ctx, "usage")
    wait(ctx, 500, "Wait for Usage dialog to appear and close")
    ctx.log.success("Usage Instructions dialog opened and closed")
