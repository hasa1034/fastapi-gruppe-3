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

"""Pydantic-Model für die Betreiber."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

from kiosk.entity import Betreiber, Geschlecht

__all__: list[str] = ["BetreiberModel"]


class BetreiberModel(BaseModel):
    """Pydantic-Model für die Betreiber."""

    vorname: str = Field(..., min_length=2)
    """Der Vorname."""

    nachname: str = Field(..., min_length=2)
    """Der Nachname."""

    geschlecht: Optional[Geschlecht] = None
    """Das Geschlecht als Enum."""

    model_config = ConfigDict(
        # Beispiel für OpenAPI / Swagger Dokumentation
        json_schema_extra={
            "example": {
                "vorname": "Max",
                "nachname": "Mustermann",
                "geschlecht": "M",
            },
        }
    )

    def to_betreiber(self) -> Betreiber:
        """Konvertierung in ein Betreiber-Objekt für SQLAlchemy.

        :return: Betreiber-Objekt für SQLAlchemy
        :rtype: Betreiber
        """
        # Model von Pydantic in ein Dictionary konvertieren
        betreiber_dict = self.model_dump()

        # Felder, die in der Datenbank automatisch gesetzt werden oder
        # erst später verknüpft werden, auf None setzen
        betreiber_dict["id"] = None
        betreiber_dict["kiosk_id"] = None
        betreiber_dict["kiosk"] = None

        # Double Star Operator packt das Dict als Argumente für den Konstruktor aus
        return Betreiber(**betreiber_dict)
