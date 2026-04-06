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

"""Geschäftslogik zum Lesen von Kioskdaten."""

from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Final

from loguru import logger
from openpyxl import Workbook  # pyright: ignore[reportMissingModuleSource]

from kiosk.config import excel_enabled
from kiosk.repository import (
    Pageable,
    KioskRepository,
    Session,
    Slice,
)
from kiosk.security import Role, User
from kiosk.service.exceptions import ForbiddenError, NotFoundError
from kiosk.service.kiosk_dto import KioskDTO

__all__ = ["KioskService"]


class KioskService:
    """Service-Klasse mit Geschäftslogik für Kioske."""

    def __init__(self, repo: KioskRepository) -> None:
        """Konstruktor mit abhängigem KioskRepository."""
        self.repo: KioskRepository = repo

    def find_by_id(self, kiosk_id: int, user: User) -> KioskDTO:
        """Suche mit der Kiosk-ID.

        :param kiosk_id: ID für die Suche
        :param user: User aus dem Token
        :return: Der gefundene Kiosk
        :rtype: KioskDTO
        :raises NotFoundError: Falls kein Kiosk gefunden
        :raises ForbiddenError: Falls die Kioskdaten nicht gelesen werden dürfen
        """
        logger.debug("kiosk_id={}, user={}", kiosk_id, user)

        # Session-Objekt ist die Schnittstelle zur DB, nutzt intern ein Transaktionsobj.
        # implizites "autobegin()" bei einem with-Block
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#opening-and-closing-a-session
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#using-a-sessionmaker
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#auto-begin
        # durch "with" erhaelt man einen "Context Manager", der die Ressource/Session
        # am Endes des Blocks schliesst
        with Session() as session:
            user_is_admin: Final = Role.ADMIN in user.roles

            if (
                kiosk := self.repo.find_by_id(kiosk_id=kiosk_id, session=session)
            ) is None:
                if user_is_admin:
                    message: Final = f"Kein Kiosk mit der ID {kiosk_id}"
                    logger.debug("NotFoundError: {}", message)
                    # "Throw Exceptions Instead of Returning Errors"
                    raise NotFoundError(kiosk_id=kiosk_id)
                logger.debug("nicht admin")
                raise ForbiddenError

            if kiosk.username != user.username and not user_is_admin:
                logger.debug(
                    "kiosk.username={}, user.username={}, user.roles={}",
                    kiosk.username,
                    user.username,
                    user.roles,
                )
                raise ForbiddenError

            kiosk_dto: Final = KioskDTO(kiosk)
            session.commit()

        logger.debug("{}", kiosk_dto)
        return kiosk_dto

    # ab Python 3.9 (2019) ist der Element-Type in eckigen Klammern und
    # der Name von eingebauten Collections ist kleingeschrieben.
    def find(
        self,
        suchparameter: Mapping[str, str],
        pageable: Pageable,
    ) -> Slice[KioskDTO]:
        """Suche mit Suchparameter.

        :param suchparameter: Suchparameter
        :return: Liste der gefundenen Kioske
        :rtype: Slice[KioskDTO]
        :raises NotFoundError: Falls keine Kioske gefunden wurden
        """
        logger.debug("{}", suchparameter)
        with Session() as session:
            kiosk_slice: Final = self.repo.find(
                suchparameter=suchparameter, pageable=pageable, session=session
            )
            if len(kiosk_slice.content) == 0:
                raise NotFoundError(suchparameter=suchparameter)

            # tuple mit einem "Generator"-Ausdruck
            # vgl. List Comprehension ab Python 2.0 (2000) https://peps.python.org/pep-0202
            kioske_dto: Final = tuple(
                KioskDTO(kiosk) for kiosk in kiosk_slice.content
            )
            session.commit()

        if excel_enabled:
            self._create_excelsheet(kioske_dto)
        kioske_dto_slice = Slice(
            content=kioske_dto, total_elements=kiosk_slice.total_elements
        )
        logger.debug("{}", kioske_dto_slice)
        return kioske_dto_slice

    def find_namen(self, teil: str) -> Sequence[str]:
        """Suche Namen zu einem Teilstring.

        :param teil: Teilstring der gesuchten Namen
        :return: Liste der gefundenen Namen oder eine leere Liste
        :rtype: list[str]
        :raises NotFoundError: Falls keine Namen gefunden wurden
        """
        logger.debug("teil={}", teil)
        with Session() as session:
            namen: Final = self.repo.find_namen(teil=teil, session=session)
            session.commit()

        logger.debug("{}", namen)
        if len(namen) == 0:
            raise NotFoundError
        return namen

    def _create_excelsheet(self, kioske: tuple[KioskDTO, ...]) -> None:
        """Ein Excelsheet mit den gefundenen Kioske erstellen.

        :param kioske: Kioskdaten für das Excelsheet
        """
        # https://automatetheboringstuff.com/2e/chapter13
        workbook: Final = Workbook()
        worksheet: Final = workbook.active
        if worksheet is None:
            return

        worksheet.append(["Name", "Emailadresse"])
        for kiosk in kioske:
            worksheet.append((
                kiosk.name,
                kiosk.email,
            ))

        timestamp: Final = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        workbook.save(f"kioske-{timestamp}.xlsx")
