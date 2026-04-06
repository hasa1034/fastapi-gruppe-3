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

"""Schema für GraphQL."""

from decimal import Decimal

import strawberry

from kiosk.entity import Geschlecht

__all__ = [
    "BetreiberInput",
    "CreatePayload",
    "KioskInput",
    "ProduktInput",
    "Suchparameter",
]

# SDL (schema definition language):
# type Kiosk {
#     name: String!
# }
# type Query {
#     kiosk(kiosk_id: ID!): Kiosk!
#     kiosks(input: Suchparameter): [Kiosk!]
# }
# type Mutation {
#     create(kiosk_input: KioskInput!): CreatePayload!
# }


@strawberry.input
class Suchparameter:
    """Suchparameter für die Suche nach Kiosks."""

    name: str | None = None
    """Name als Suchkriterium."""

    email: str | None = None
    """Emailadresse als Suchkriterium."""


@strawberry.input
class BetreiberInput:
    """Betreiber eines neuen Kiosks."""

    vorname: str
    """Vorname eines neuen Betreibers."""

    nachname: str
    """Nachname eines neuen Betreibers."""

    geschlecht: Geschlecht
    """Geschlecht."""


@strawberry.input
class ProduktInput:
    """Produkt für einen neuen Kiosk."""

    preis: Decimal
    """Preis."""

    waehrung: str
    """Währung als 3-stellige Zeichenkette."""


@strawberry.input
class KioskInput:
    """Daten für einen neuen Kiosk."""

    name: str
    """Name des neuen Kiosks."""

    email: str
    """Emailadresse."""

    ist_geoeffnet: bool
    """Angabe, ob der Kiosk geöffnet ist."""

    homepage: str | None
    """Optionale Homepage."""

    betreiber: BetreiberInput
    """Betreiber."""

    produkte: list[ProduktInput]
    """Produkte."""


@strawberry.type
class CreatePayload:
    """Resultat-Typ, wenn ein neuer Kiosk angelegt wurde."""

    id: int
    """ID des neu angelegten Kiosks"""


@strawberry.type
class LoginResult:
    """Resultat-Typ, wenn ein Login erfolgreich war."""

    token: str
    """Token des eingeloggten Users."""
    expiresIn: str  # noqa: N815  # NOSONAR
    """Gültigkeitsdauer des Tokens."""
    roles: list[str]
    """Rollen des eingeloggten Users."""
