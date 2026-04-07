# ruff: noqa: S101, D103, ARG005
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

"""Unit-Tests für find_by_id() von KioskService."""

from copy import deepcopy
from datetime import date
from typing import TYPE_CHECKING

from pytest import fixture, mark, raises

from kiosk.entity import Betreiber, Kiosk, Geschlecht
from kiosk.service import EmailExistsError, UsernameExistsError

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@fixture
def session_mock(mocker: MockerFixture):
    session = mocker.Mock()
    # Patching von "with Session() as session:" in kiosk_write_service.py
    mocker.patch(
        "kiosk.service.kiosk_write_service.Session",
        return_value=mocker.MagicMock(
            __enter__=lambda self: session,
            __exit__=lambda self, exc_type, exc, tb: None,
        ),
    )
    return session


@mark.unit
@mark.unit_create
def test_create(
    kiosk_write_service, session_mock, keycloak_admin_mock, mocker
) -> None:
    # Arrange
    email = "mock@email.test"
    betreiber = Betreiber(
        id=999,
        vorname="mock",
        nachname="Mocking",
        geschlecht=Geschlecht.MAENNLICH,
        kiosk_id=None,
        kiosk=None,
    )
    kiosk = Kiosk(
        id=None,
        email=email,
        name="Mocktest",
        ist_geoeffnet=True,
        homepage="https://www.test.de",
        username="mocktest",
        betreiber=betreiber,
        produkte=[],
    )

    betreiber.kiosk = kiosk
    kiosk_db_mock = deepcopy(kiosk)
    generierte_id = 1
    kiosk_db_mock.id = generierte_id
    kiosk_db_mock.betreiber.id = generierte_id

    # Patch fuer KeycloakAdmin.get_user_id() und KeycloakAdmin.get_users()
    keycloak_admin_mock.get_user_id.return_value = None
    keycloak_admin_mock.get_users.return_value = []

    # session.scalar(select(func.count()).where(Kiosk.email == email)
    session_mock.scalar.return_value = 0
    session_mock.add.return_value = None

    def flush_side_effect(objects=None):
        for obj in objects or []:
            obj.id = generierte_id  # Emulation: generierter PK in session.flush()

    session_mock.flush.side_effect = flush_side_effect

    # Patch fuer die Funktion send_mail
    mocker.patch("kiosk.service.kiosk_write_service.send_mail", return_value=None)

    # Act
    kiosk_dto = kiosk_write_service.create(kiosk=kiosk)

    # Assert
    assert kiosk_dto.id == generierte_id


@mark.unit
@mark.unit_create
def test_create_username_none(kiosk_write_service) -> None:
    # Arrange
    betreiber = Betreiber(
        id=999,
        vorname="mock",
        nachname="Mocking",
        geschlecht=Geschlecht.MAENNLICH,
        kiosk_id=None,
        kiosk=None,
    )
    kiosk = Kiosk(
        id=None,
        email="mock@email.test",
        name="Mocktest",
        ist_geoeffnet=True,
        homepage="https://www.test.de",
        username=None,
        betreiber=betreiber,
        produkte=[],
    )
    betreiber.kiosk = kiosk

    # Act
    with raises(ValueError) as err:
        kiosk_write_service.create(kiosk=kiosk)

    # Assert
    assert err.type is ValueError


@mark.unit
@mark.unit_create
def test_create_username_exists(kiosk_write_service, keycloak_admin_mock) -> None:
    # Arrange
    email = "mock@email.test"
    betreiber = Betreiber(
        id=999,
        vorname="mock",
        nachname="Mocking",
        geschlecht=Geschlecht.MAENNLICH,
        kiosk_id=None,
        kiosk=None,
    )
    kiosk = Kiosk(
        id=None,
        email=email,
        name="Mocktest",
        ist_geoeffnet=True,
        homepage="https://www.test.de",
        username="mocktest",
        betreiber=betreiber,
        produkte=[],
    )
    betreiber.kiosk = kiosk

    # Patch fuer KeycloakAdmin.get_user_id()
    user_id = "12345678-1234-1234-1234-123456789012"
    keycloak_admin_mock.get_user_id.return_value = user_id
    keycloak_admin_mock.get_users.return_value = []

    # Act
    with raises(UsernameExistsError) as err:
        kiosk_write_service.create(kiosk=kiosk)

    # Assert
    assert err.type is UsernameExistsError


@mark.unit
@mark.unit_create
def test_create_email_exists(kiosk_write_service, keycloak_admin_mock) -> None:
    # Arrange
    email = "mock@email.test"
    betreiber = Betreiber(
        id=999,
        vorname="mock",
        nachname="Mocking",
        geschlecht=Geschlecht.MAENNLICH,
        kiosk_id=None,
        kiosk=None,
    )
    kiosk = Kiosk(
        id=None,
        email=email,
        name="Mocktest",
        ist_geoeffnet=True,
        homepage="https://www.test.de",
        username="mocktest",
        betreiber=betreiber,
        produkte=[],
    )
    betreiber.kiosk = kiosk

    # Patch fuer KeycloakAdmin.get_users()
    keycloak_admin_mock.get_user_id.return_value = None  # sonst UsernameExistsError
    keycloak_admin_mock.get_users.return_value = [
        {"id": "12345678-1234-1234-1234-123456789012", "email": email}
    ]

    # Act
    with raises(EmailExistsError) as err:
        kiosk_write_service.create(kiosk=kiosk)

    # Assert
    assert err.type is EmailExistsError
