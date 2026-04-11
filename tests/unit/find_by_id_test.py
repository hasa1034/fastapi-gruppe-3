# ruff: noqa: S101, S106, D103, ARG005
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

from dataclasses import asdict
from typing import TYPE_CHECKING

from pytest import fixture, mark, raises

from kiosk.entity import Betreiber, Geschlecht, Kiosk
from kiosk.security import Role, User
from kiosk.service import ForbiddenError, KioskDTO, KioskService, NotFoundError

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@fixture
def session_mock(mocker: MockerFixture):
    session = mocker.Mock()
    # Patching von "with Session() as session:" in kiosk_service.py
    mocker.patch(
        "kiosk.service.kiosk_service.Session",
        return_value=mocker.MagicMock(
            __enter__=lambda self: session,
            __exit__=lambda self, exc_type, exc, tb: None,
        ),
    )
    return session


@mark.unit
@mark.unit_find_by_id
def test_find_by_id(kiosk_service, session_mock) -> None:
    # Arrange
    kiosk_id = 1
    username = "mocktest"
    email = "mock@email.test"
    name = "Mocktest"

    user_mock = User(
        username=username,
        email=email,
        name=name,
        roles=[Role.ADMIN],
        password="mockpass",
    )
    betreiber_mock = Betreiber(
        id=11,
        vorname="mock",
        nachname="Mocking",
        geschlecht=Geschlecht.MAENNLICH,
        kiosk_id=kiosk_id,
        kiosk=None,
    )
    kiosk_mock = Kiosk(
        id=kiosk_id,
        email=email,
        name=name,
        ist_geoeffnet=True,
        homepage="https://www.test.de",
        username=username,
        betreiber=betreiber_mock,
        produkte=[],
    )
    betreiber_mock.kiosk = kiosk_mock
    kiosk_dto_mock = KioskDTO(kiosk_mock)
    # session.scalar(select(Kiosk)...)
    session_mock.scalar.return_value = kiosk_mock

    # Act
    kiosk_dto = kiosk_service.find_by_id(kiosk_id=kiosk_id, user=user_mock)

    # Assert
    assert asdict(kiosk_dto) == asdict(kiosk_dto_mock)


@mark.unit
@mark.unit_find_by_id
def test_find_by_id_not_found(kiosk_service: KioskService, session_mock) -> None:
    # Arrange
    kiosk_id = 999
    user_mock = User(
        username="mocktest",
        email="mock@email.test",
        name="Mocktest",
        roles=[Role.ADMIN],
        password="mockpass",
    )
    # session.scalar(select(Kiosk)...)
    session_mock.scalar.return_value = None

    # Act
    with raises(NotFoundError) as err:
        kiosk_service.find_by_id(kiosk_id=kiosk_id, user=user_mock)

    # Assert
    assert err.type == NotFoundError
    assert str(err.value) == "Not Found"  # super().__init__("Not Found")
    assert err.value.kiosk_id == kiosk_id


@mark.unit
@mark.unit_find_by_id
def test_find_by_id_not_found_not_admin(
    kiosk_service: KioskService, session_mock
) -> None:
    # Arrange
    kiosk_id = 999
    user_mock = User(
        username="mocktest",
        email="mock@email.test",
        name="Mocktest",
        roles=[],
        password="mockpass",
    )
    # session.scalar(select(Kiosk)...)
    session_mock.scalar.return_value = None

    # Act
    with raises(ForbiddenError) as err:
        kiosk_service.find_by_id(kiosk_id=kiosk_id, user=user_mock)

    # Assert
    assert err.type == ForbiddenError


@mark.unit
@mark.unit_find_by_id
def test_find_by_id_not_admin(kiosk_service, session_mock) -> None:
    # Arrange
    kiosk_id = 1
    username = "mocktest"
    email = "mock@email.test"
    name = "Mocktest"

    user_mock = User(
        username=username,
        email=email,
        name=name,
        roles=[Role.KIOSK],
        password="mockpass",
    )
    betreiber_mock = Betreiber(
        id=11,
        vorname="mock",
        nachname="Mocking",
        geschlecht=Geschlecht.MAENNLICH,
        kiosk_id=kiosk_id,
        kiosk=None,
    )
    kiosk_mock = Kiosk(
        id=kiosk_id,
        email=email,
        name=name,
        ist_geoeffnet=True,
        homepage="https://www.test.de",
        username=username,
        betreiber=betreiber_mock,
        produkte=[],
    )
    betreiber_mock.kiosk = kiosk_mock
    kiosk_dto_mock = KioskDTO(kiosk_mock)
    # session.scalar(select(Kiosk)...)
    session_mock.scalar.return_value = kiosk_mock

    # Act
    kiosk_dto = kiosk_service.find_by_id(kiosk_id=kiosk_id, user=user_mock)

    # Assert
    assert asdict(kiosk_dto) == asdict(kiosk_dto_mock)


@mark.unit
@mark.unit_find_by_id
def test_find_by_id_other(kiosk_service, session_mock) -> None:
    # Arrange
    kiosk_id = 1
    email = "mock@email.test"
    name = "Mocktest"

    user_mock = User(
        username="other",
        email=email,
        name=name,
        roles=[Role.KIOSK],
        password="mockpass",
    )
    betreiber_mock = Betreiber(
        id=11,
        vorname="mock",
        nachname="Mocking",
        geschlecht=Geschlecht.MAENNLICH,
        kiosk_id=kiosk_id,
        kiosk=None,
    )
    kiosk_mock = Kiosk(
        id=kiosk_id,
        email=email,
        name=name,
        ist_geoeffnet=True,
        homepage="https://www.test.de",
        username="mocktest",
        betreiber=betreiber_mock,
        produkte=[],
    )
    betreiber_mock.kiosk = kiosk_mock
    # session.scalar(select(Kiosk)...)
    session_mock.scalar.return_value = kiosk_mock

    # Act
    with raises(ForbiddenError) as err:
        kiosk_service.find_by_id(kiosk_id=kiosk_id, user=user_mock)

    # Assert
    assert err.type == ForbiddenError
