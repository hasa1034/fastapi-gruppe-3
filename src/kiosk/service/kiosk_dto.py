# Copyright (C) 2022 - present Juergen Zimmermann, Hochschule Karlsruhe
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

"""DTO-Klasse für Kioskdaten, insbesondere ohne Decorators für SQLAlchemy."""

from dataclasses import dataclass

import strawberry

from kiosk.entity import Kiosk
from kiosk.service.betreiber_dto import BetreiberDTO

__all__ = ["KioskDTO"]


# Mit der Funktion asdict() kann ein Objekt einfach in ein dict konvertiert werden
# init=True (default): __init__ fuer die "member variables" wird generiert
# eq=True (default): __eq__ wird generiert
# unsafe_hash=False (default): __hash__ passend zu __eq__ wird generiert
# repr=True (default): __repr__ wird generiert
# frozen=False (default): mutable
# kw_only=False (default): Initialisierungs-Fkt auch ohne "Keyword Arguments" aufrufen
# slots=False (default): __dict__ zur Speicherung statt slots
# slots: schnellerer Zugriff, kompakte Speicherung
# https://stackoverflow.com/questions/472000/usage-of-slots
@dataclass(eq=False, slots=True, kw_only=True)
# Strawberry konvertiert automatisch zwischen snake_case (Python) und camelCase (Schema)
@strawberry.type
class KioskDTO:
    """DTO-Klasse für aus gelesene oder gespeicherte Kioskdaten: ohne Decorators."""

    id: int
    version: int
    name: str
    email: str
    ist_geoeffnet: bool
    homepage: str | None
    betreiber: BetreiberDTO
    username: str | None

    # asdict kann nicht verwendet werden: Rueckwaertsverweise Kiosk - Betreiber
    # https://github.com/python/cpython/issues/94345
    def __init__(self, kiosk: Kiosk):
        """Initialisierung von KioskDTO durch ein Entity-Objekt von Kiosk.

        :param kiosk: Kiosk-Objekt mit Decorators zu SQLAlchemy
        """
        kiosk_id = kiosk.id
        self.id = kiosk_id if kiosk_id is not None else -1
        self.version = kiosk.version
        self.name = kiosk.name
        self.email = kiosk.email
        self.ist_geoeffnet = kiosk.ist_geoeffnet
        self.homepage = kiosk.homepage
        self.betreiber = BetreiberDTO(kiosk.betreiber)
        self.username = kiosk.username if kiosk.username is not None else "N/A"
