# Copyright (C) 2023 - present Juergen Zimmermann, Hochschule Karlsruhe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""Modul für die REST-Schnittstelle einschließlich Validierung."""

from collections.abc import Sequence

from kiosk.router.health_router import liveness, readiness
from kiosk.router.health_router import router as health_router
from kiosk.router.kiosk_router import get, get_by_id, get_namen, kiosk_router
from kiosk.router.kiosk_write_router import (
    delete_by_id,
    kiosk_write_router,
    post,
    put,
)
from kiosk.router.shutdown_router import router as shutdown_router
from kiosk.router.shutdown_router import shutdown

__all__: Sequence[str] = [
    "delete_by_id",
    "get",
    "get_by_id",
    "get_namen",
    "health_router",
    "kiosk_router",
    "kiosk_write_router",
    "liveness",
    "post",
    "put",
    "readiness",
    "shutdown",
    "shutdown_router",
]
