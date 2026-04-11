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

"""Unit-Tests für find() von KioskService."""

from typing import TYPE_CHECKING

from pytest import fixture, mark, raises

from kiosk.entity import Betreiber, Geschlecht, Kiosk
from kiosk.repository import Pageable
from kiosk.service import NotFoundError

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
@mark.unit_find
def test_find_by_name(kiosk_service, session_mock) -> None:
    # Arrange
    name = "Mocktest"
    kiosk_id = 1
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
        email="mock@email.test",
        name=name,
        ist_geoeffnet=True,
        homepage="https://www.test.de",
        username="mocktest",
        betreiber=betreiber_mock,
        produkte=[],
    )
    betreiber_mock.kiosk = kiosk_mock
    suchparameter = {"name": name}
    pageable = Pageable(size=5, number=0)
    # session.scalars(select(Kiosk)...).all()
    session_mock.scalars.return_value.all.return_value = [kiosk_mock]

    # Act
    kiosks_slice = kiosk_service.find(suchparameter=suchparameter, pageable=pageable)

    # Assert
    assert len(kiosks_slice.content) == 1
    assert kiosks_slice.content[0].name == name


@mark.unit
@mark.unit_find
def test_find_by_name_not_found(kiosk_service, session_mock) -> None:
    # Arrange
    name = "Notfound"
    suchparameter = {"name": name}
    pageable = Pageable(size=5, number=0)
    # session.scalars(select(Kiosk)...).all()
    session_mock.scalars.return_value.all.return_value = []

    # Act
    with raises(NotFoundError) as err:
        kiosk_service.find(suchparameter=suchparameter, pageable=pageable)

    # Assert
    assert err.type == NotFoundError
    assert str(err.value) == "Not Found"  # super().__init__("Not Found")
    assert err.value.suchparameter is not None
    assert err.value.suchparameter.get("name") == name  # pyright: ignore[reportOptionalMemberAccess]


@mark.unit
@mark.unit_find
def test_find_by_email(kiosk_service, session_mock) -> None:
    # Arrange
    email = "mock@email.test"
    kiosk_id = 1
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
        name="Mocktest",
        ist_geoeffnet=True,
        homepage="https://www.test.de",
        username="mocktest",
        betreiber=betreiber_mock,
        produkte=[],
    )
    betreiber_mock.kiosk = kiosk_mock
    suchparameter = {"email": email}
    pageable = Pageable(size=5, number=0)
    # session.scalar(select(Kiosk)...)
    session_mock.scalar.return_value = kiosk_mock

    # Act
    kiosks_slice = kiosk_service.find(suchparameter=suchparameter, pageable=pageable)

    # Assert
    assert len(kiosks_slice.content) == 1
    assert kiosks_slice.content[0].email == email

    betreiber_mock.kiosk = kiosk_mock
    suchparameter = {"email": email}
    pageable = Pageable(size=5, number=0)
    # session.scalar(select(Kiosk)...)
    session_mock.scalar.return_value = kiosk_mock

    # Act
    kioske_slice = kiosk_service.find(suchparameter=suchparameter, pageable=pageable)

    # Assert
    assert len(kioske_slice.content) == 1
    assert kioske_slice.content[0].email == email


@mark.unit
@mark.unit_find
def test_find_by_email_not_found(kiosk_service, session_mock) -> None:
    # Arrange
    email = "not@found.mock"
    suchparameter = {"email": email}
    pageable = Pageable(size=5, number=0)
    # session.scalar(select(Kiosk)...)
    session_mock.scalar.return_value = None

    # Act
    with raises(NotFoundError) as err:
        kiosk_service.find(suchparameter=suchparameter, pageable=pageable)

    # Assert
    assert str(err.value) == "Not Found"  # super().__init__("Not Found")
    assert err.value.suchparameter is not None
    assert err.value.suchparameter.get("email") == email  # pyright: ignore[reportOptionalMemberAccess]
