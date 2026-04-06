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

"""Geschäftslogik zum Schreiben von Kioskdaten."""

from typing import Final

from loguru import logger

from kiosk.entity import Kiosk
from kiosk.repository import KioskRepository, Session
from kiosk.security import User, UserService
from kiosk.service.exceptions import (
    EmailExistsError,
    NotFoundError,
    UsernameExistsError,
    VersionOutdatedError,
)
from kiosk.service.mailer import send_mail
from kiosk.service.kiosk_dto import KioskDTO

__all__ = ["KioskWriteService"]


class KioskWriteService:
    """Service-Klasse mit Geschäftslogik für Kiosk."""

    def __init__(self, repo: KioskRepository, user_service: UserService) -> None:
        """Konstruktor mit abhängigem KioskRepository und UserService."""
        self.repo: KioskRepository = repo
        self.user_service: UserService = user_service

    def create(self, kiosk: Kiosk) -> KioskDTO:
        """Einen neuen Kiosk anlegen.

        :param kiosk: Der neue Kiosk ohne ID
        :return: Der neu angelegte Kiosk mit generierter ID
        :rtype: KioskDTO
        :raises EmailExistsError: Falls die Emailadresse bereits existiert
        """
        logger.debug(
            "kiosk={}, betreiber={}, produkte={}",
            kiosk,
            kiosk.betreiber,
            kiosk.produkte,
        )

        username: Final = kiosk.username
        if username is None:
            raise ValueError

        # https://www.keycloak.org/docs-api/latest/rest-api:
        # GET /admin/realms/{realm}/users
        if self.user_service.username_exists(username):
            raise UsernameExistsError(username)

        email: Final = kiosk.email
        if self.user_service.email_exists(email):
            raise EmailExistsError(email=email)

        user: Final = User(
            username=username,
            email=kiosk.email,
            name=kiosk.name,
            password="p",  # noqa: S106 # NOSONAR
            roles=[],
        )
        user_id = self.user_service.create_user(user)
        logger.debug("user_id={}", user_id)

        # durch "with" erhaelt man einen "Context Manager", der die Ressource/Session
        # am Endes des Blocks schliesst
        with Session() as session:
            if self.repo.exists_email(email=email, session=session):
                raise EmailExistsError(email=email)

            kiosk_db: Final = self.repo.create(kiosk=kiosk, session=session)
            kiosk_dto: Final = KioskDTO(kiosk_db)
            session.commit()

        # TODO User aus Keycloak loeschen, falls die DB-Transaktion fehlschlaegt

        send_mail(kiosk_dto=kiosk_dto)
        logger.debug("kiosk_dto={}", kiosk_dto)
        return kiosk_dto

    def update(self, kiosk: Kiosk, kiosk_id: int, version: int) -> KioskDTO:
        """Daten eines Kiosks ändern.

        :param kiosk: Die neuen Daten
        :param kiosk_id: ID des zu aktualisierenden Kiosks
        :param version: Version für optimistische Synchronisation
        :return: Der aktualisierte Kiosk
        :rtype: KioskDTO
        :raises NotFoundError: Falls der zu aktualisierende Kiosk nicht existiert
        :raises VersionOutdatedError: Falls die Versionsnummer nicht aktuell ist
        :raises EmailExistsError: Falls die Emailadresse bereits existiert
        """
        logger.debug("kiosk_id={}, version={}, {}", kiosk_id, version, kiosk)

        with Session() as session:
            if (
                kiosk_db := self.repo.find_by_id(
                    kiosk_id=kiosk_id, session=session
                )
            ) is None:
                raise NotFoundError(kiosk_id)
            if kiosk_db.version > version:
                raise VersionOutdatedError(version)

            email: Final = kiosk.email
            if email != kiosk_db.email and self.repo.exists_email_other_id(
                kiosk_id=kiosk_id,
                email=email,
                session=session,
            ):
                raise EmailExistsError(email)

            kiosk_db.set(kiosk)
            if (
                kiosk_updated := self.repo.update(kiosk=kiosk_db, session=session)
            ) is None:
                raise NotFoundError(kiosk_id)
            kiosk_dto: Final = KioskDTO(kiosk_updated)
            logger.debug("{}", kiosk_dto)

            session.commit()
            # CAVEAT: Die erhoehte Versionsnummer ist erst COMMIT sichtbar
            kiosk_dto.version += 1
            return kiosk_dto

    def delete_by_id(self, kiosk_id: int) -> None:
        """Einen Kiosk anhand seiner ID löschen.

        :param kiosk_id: ID des zu löschenden Kiosks
        """
        logger.debug("kiosk_id={}", kiosk_id)
        with Session() as session:
            self.repo.delete_by_id(kiosk_id=kiosk_id, session=session)
            session.commit()
