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

"""PatientWriteRouter."""
from typing import Annotated, Final

from fastapi import APIRouter, Depends, Request, Response, status
from loguru import logger

from kiosk.problem_details import create_problem_details
from kiosk.router.constants import IF_MATCH, IF_MATCH_MIN_LEN
from kiosk.router.dependencies import get_write_service
from kiosk.router.kiosk_model import KioskModel
from kiosk.router.kiosk_update_model import KioskUpdateModel
from kiosk.security import Role, RolesRequired
from kiosk.service import KioskWriteService

__all__: list[str] = ["kiosk_write_router"]


kiosk_write_router: Final = APIRouter(tags=["Schreiben"])


@kiosk_write_router.post("")
def post(
    kiosk_model: KioskModel,
    request: Request,
    service: Annotated[KioskWriteService, Depends(get_write_service)],
) -> Response:
    """POST-Request, um einen neuen Kiosk anzulegen.

    :param kiosk_model: Kioskdaten als Pydantic-Model
    :param request: Injiziertes Request-Objekt von FastAPI bzw. Starlette
        mit der Request-URL
    :param service: Injizierter Service für Geschäftslogik
    :rtype: Response
    :raises ValidationError: Falls es bei Pydantic Validierungsfehler gibt
    :raises EmailExistsError: Falls die Emailadresse bereits existiert
    :raises UsernameExistsError: Falls der Benutzername bereits existiert
    """
    logger.debug("kiosk_model={}", kiosk_model)
    kiosk_dto: Final = service.create(kiosk=kiosk_model.to_kiosk())
    logger.debug("kiosk_dto={}", kiosk_dto)

    return Response(
        status_code=status.HTTP_201_CREATED,
        headers={"Location": f"{request.url}/{kiosk_dto.id}"},
    )


@kiosk_write_router.put(
    "/{kiosk_id}",
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.KIOSK]))],
)
def put(
    kiosk_id: int,
    kiosk_update_model: KioskUpdateModel,
    request: Request,
    service: Annotated[KioskWriteService, Depends(get_write_service)],
) -> Response:
    """PUT-Request, um einen Kiosk zu aktualisieren.

    :param kiosk_id: ID des zu aktualisierenden Kiosks als Pfadparameter
    :param request: Injiziertes Request-Objekt von FastAPI bzw. Starlette
        mit If-Match im Header
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit Statuscode 204
    :rtype: Response
    :raises ValidationError: Falls es bei Marshmallow Validierungsfehler gibt
    :raises EmailExistsError: Falls die neue Emailadresse bereits
    :raises NotFoundError: Falls zur id kein Kiosk existiert
    :raises VersionOutdatedError: Falls die Versionsnummer nicht aktuell ist
    """
    if_match_value: Final = request.headers.get(IF_MATCH)
    logger.debug(
        "kiosk_id={}, if_match={}, kiosk_update_model={}",
        kiosk_id,
        if_match_value,
        kiosk_update_model,
    )

    if if_match_value is None:
        return create_problem_details(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
        )

    if (
        len(if_match_value) < IF_MATCH_MIN_LEN
        or not if_match_value.startswith('"')
        or not if_match_value.endswith('"')
    ):
        return create_problem_details(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
        )

    version: Final = if_match_value[1:-1]
    try:
        version_int: Final = int(version)
    except ValueError:
        return Response(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
        )

    kiosk: Final = kiosk_update_model.to_kiosk()
    kiosk_modified: Final = service.update(
        kiosk=kiosk,
        kiosk_id=kiosk_id,
        version=version_int,
    )
    logger.debug("kiosk_modified={}", kiosk_modified)

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        headers={"ETag": f'"{kiosk_modified.version}"'},
    )


@kiosk_write_router.delete(
    "/{kiosk_id}",
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.KIOSK]))],
)
def delete_by_id(
    kiosk_id: int,
    service: Annotated[KioskWriteService, Depends(get_write_service)],
) -> Response:
    """DELETE-Request, um einen Kiosk anhand seiner ID zu löschen.

    :param kiosk_id: ID des zu löschenden Kiosks
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit Statuscode 204
    :rtype: Response
    """
    logger.debug("kiosk_id={}", kiosk_id)
    service.delete_by_id(kiosk_id=kiosk_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
