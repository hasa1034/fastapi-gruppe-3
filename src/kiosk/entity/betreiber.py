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

"""Entity-Klasse für die Betreiber."""

from sqlalchemy import ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from kiosk.entity.base import Base
from patient.entity.geschlecht import Geschlecht


class Betreiber(Base):
    """Entity-Klasse für den Betreiber."""

    __tablename__ = "betreiber"

    vorname: Mapped[str]
    """Der Vorname."""

    nachname: Mapped[str]
    """Der Nachname."""

    # https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#orm-declarative-mapped-column-enums
    geschlecht: Mapped[Geschlecht | None]
    """Das optionale Geschlecht."""

    id: Mapped[int] = mapped_column(
        Identity(start=1000),
        primary_key=True,
    )
    """Die generierte ID gemäß der zugehörigen IDENTITY-Spalte."""

    kiosk_id: Mapped[int] = mapped_column(ForeignKey("kiosk.id"))
    """ID des zugehörigen Kiosks als Fremdschlüssel in der DB-Tabelle."""

    kiosk: Mapped[Kiosk] = relationship(  # noqa: F821 # ty: ignore[unresolved-reference] # pyright: ignore[reportUndefinedVariable]
        back_populates="betreiber",
    )
    """Das zugehörige transiente Kiosk-Objekt."""

    # __repr__ fuer Entwickler/innen, __str__ fuer User
    def __repr__(self) -> str:
        """Ausgabe eines Betreibers als String ohne die Kioskdaten."""
        return f"Betreiber(id={self.id}, vorname={self.vorname}, nachname={self.nachname}, geschlecht={self.geschlecht})"
