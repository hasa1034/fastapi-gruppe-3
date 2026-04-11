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

"""KioskGetRouter."""

from dataclasses import asdict
from typing import Annotated, Any, Final

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import JSONResponse
from loguru import logger

from kiosk.repository import Pageable
from kiosk.repository.slice import Slice
from kiosk.router.constants import ETAG, IF_NONE_MATCH, IF_NONE_MATCH_MIN_LEN
from kiosk.router.dependencies import get_service
from kiosk.router.page import Page
from kiosk.security import Role, RolesRequired, User
from kiosk.service import KioskDTO, KioskService

__all__ = ["kiosk_router"]


# APIRouter auf Basis der Klasse Router von Starlette
kiosk_router: Final = APIRouter(tags=["Lesen"])


@kiosk_router.get(
    "/{kiosk_id}",
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.KIOSK]))],
)
def get_by_id(
    kiosk_id: int,
    request: Request,
    service: Annotated[KioskService, Depends(get_service)],
) -> Response:
    """Suche mit der Kiosk-ID.

    :param kiosk_id: ID des gesuchten Kiosks als Pfadparameter
    :param request: Injiziertes Request-Objekt von FastAPI bzw. Starlette
        mit ggf. If-None-Match im Header
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit dem gefundenen Kioskdatensatz
    :rtype: Response
    :raises NotFoundError: Falls kein Kiosk gefunden wurde
    :raises ForbiddenError: Falls die Kioskdaten nicht gelesen werden dürfen
    """
    # User-Objekt ist durch Depends(RolesRequired()) in Request.state gepuffert
    user: Final[User] = request.state.current_user
    logger.debug("kiosk_id={}, user={}", kiosk_id, user)

    kiosk: Final = service.find_by_id(kiosk_id=kiosk_id, user=user)
    logger.debug("{}", kiosk)

    if_none_match: Final = request.headers.get(IF_NONE_MATCH)
    if (
        if_none_match is not None
        and len(if_none_match) >= IF_NONE_MATCH_MIN_LEN
        and if_none_match.startswith('"')
        and if_none_match.endswith('"')
    ):
        version = if_none_match[1:-1]
        logger.debug("version={}", version)
        if version is not None:
            try:
                if int(version) == kiosk.version:
                    return Response(status_code=status.HTTP_304_NOT_MODIFIED)
            except ValueError:
                logger.debug("invalid version={}", version)

    return JSONResponse(
        content=_kiosk_to_dict(kiosk),
        headers={ETAG: f'"{kiosk.version}"'},
    )


@kiosk_router.get(
    "",
    dependencies=[Depends(RolesRequired(Role.ADMIN))],
)
def get(
    request: Request,
    service: Annotated[KioskService, Depends(get_service)],
) -> JSONResponse:
    """Suche mit Query-Parameter.

    :param request: Injiziertes Request-Objekt von FastAPI bzw. Starlette
        mit Query-Parameter
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit einer Seite mit Kiosk-Daten
    :rtype: Response
    :raises NotFoundError: Falls keine Kiosks gefunden wurden
    """
    query_params: Final = request.query_params
    log_str: Final = "{}"
    logger.debug(log_str, query_params)

    page: Final = query_params.get("page")
    size: Final = query_params.get("size")
    pageable: Final = Pageable.create(number=page, size=size)

    suchparameter = dict(query_params)
    if "page" in query_params:
        del suchparameter["page"]
    if "size" in query_params:
        del suchparameter["size"]

    kiosk_slice: Final = service.find(suchparameter=suchparameter, pageable=pageable)

    result: Final = _kiosk_slice_to_page(kiosk_slice, pageable)
    logger.debug(log_str, result)
    return JSONResponse(content=result)


@kiosk_router.get(
    "/namen/{teil}",
    dependencies=[Depends(RolesRequired(Role.ADMIN))],
)
def get_namen(
    teil: str,
    service: Annotated[KioskService, Depends(get_service)],
) -> JSONResponse:
    """Suche namen zum gegebenen Teilstring.

    :param teil: Teilstring der gefundenen Nachnamen
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit Statuscode 200 und gefundenen Nachnamen im Body
    :rtype: Response
    :raises NotFoundError: Falls keine Nachnamen gefunden wurden
    """
    logger.debug("teil={}", teil)
    namen: Final = service.find_namen(teil=teil)
    return JSONResponse(content=namen)


def _kiosk_slice_to_page(
    kiosk_slice: Slice[KioskDTO],
    pageable: Pageable,
) -> dict[str, Any]:
    kiosk_dict: Final = tuple(_kiosk_to_dict(kiosk) for kiosk in kiosk_slice.content)
    page: Final = Page.create(
        content=kiosk_dict,
        pageable=pageable,
        total_elements=kiosk_slice.total_elements,
    )
    return asdict(obj=page)


def _kiosk_to_dict(kiosk: KioskDTO) -> dict[str, Any]:
    # https://docs.python.org/3/library/dataclasses.html
    kiosk_dict: Final = asdict(obj=kiosk)
    kiosk_dict.pop("version")
    return kiosk_dict
