# Copyright (C) 2025 - present Juergen Zimmermann, Hochschule Karlsruhe
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

"""Factory-Funktionen für Dependency Injection."""

from typing import Annotated

from fastapi import Depends

from kiosk.repository.kiosk_repository import KioskRepository
from kiosk.security.dependencies import get_user_service
from kiosk.security.user_service import UserService
from kiosk.service.kiosk_service import KioskService
from kiosk.service.kiosk_write_service import KioskWriteService


def get_repository() -> KioskRepository:
    """Factory-Funktion für KioskRepository.

    :return: Das Repository
    :rtype: KioskRepository
    """
    return KioskRepository()


def get_service(
    repo: Annotated[KioskRepository, Depends(get_repository)],
) -> KioskService:
    """Factory-Funktion für KioskService."""
    return KioskService(repo=repo)


def get_write_service(
    repo: Annotated[KioskRepository, Depends(get_repository)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> KioskWriteService:
    """Factory-Funktion für KioskWriteService."""
    return KioskWriteService(repo=repo, user_service=user_service)
