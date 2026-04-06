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

"""Entity-Klasse für Produkt."""

from decimal import Decimal

from sqlalchemy import ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from kiosk.entity.base import Base


class Produkt(Base):
    """Entity-Klasse für Produkt."""

    __tablename__ = "produkt"

    name: Mapped[str]
    """Der Name des Produkts."""

    # https://docs.python.org/3/library/decimal.html
    # Genauigkeit ("precision"): 28
    preis: Mapped[Decimal]
    """Der Preis."""

    waehrung: Mapped[str]
    """Die Währung"""

    id: Mapped[int] = mapped_column(
        Identity(start=1000),
        primary_key=True,
    )
    """Die generierte ID gemäß der zugehörigen IDENTITY-Spalte."""

    kiosk_id: Mapped[int] = mapped_column(ForeignKey("kiosk.id"))
    """ID des zugehörigen Kiosks als Fremdschlüssel in der DB-Tabelle."""

    kiosk: Mapped[Kiosk] = relationship(  # noqa: F821 # ty: ignore[unresolved-reference] # pyright: ignore[reportUndefinedVariable ]
        back_populates="produkte",
    )
    """Das zugehörige transiente Kiosk-Objekt."""

    # __repr__ fuer Entwickler/innen, __str__ fuer User
    def __repr__(self) -> str:
        """Ausgabe der Produkte als String ohne die Kioskdaten."""
        return (
            f"Produkt(id={self.id}, name={self.name}, preis={self.preis}, "
            + f"waehrung={self.waehrung})"
        )
