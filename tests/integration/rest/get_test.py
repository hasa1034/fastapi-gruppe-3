# ruff: noqa: S101, D103
# Copyright (C) 2023 - present Juergen Zimmermann, Hochschule Karlsruhe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#

"""Tests für GET mit Query-Parameter."""

from http import HTTPStatus
from typing import Final

from common_test import ctx, login, rest_url
from httpx import get
from pytest import mark

@mark.rest
@mark.get_request
@mark.parametrize("email", ["admin@acme.com", "info@kiosk.de"])
def test_get_by_email(email: str) -> None:
    # arrange
    params = {"email": email}
    token: Final = login()
    assert token is not None
    headers: dict[str, str] = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(rest_url, params=params, headers=headers, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    content: Final = response_body["content"]
    assert isinstance(content, list)
    assert len(content) == 1
    kiosk = content[0]
    assert kiosk is not None
    assert kiosk.get("email") == email
    assert kiosk.get("id") is not None

@mark.rest
@mark.get_request
@mark.parametrize("email", ["nicht@vorhanden.com", "falscher@kiosk.de"])
def test_get_by_email_not_found(email: str) -> None:
    # arrange
    params: dict[str, str] = {"email": email}
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(rest_url, params=params, headers=headers, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND

@mark.rest
@mark.get_request
@mark.parametrize("teil", ["Kiosk", "Markt"])
def test_get_by_name(teil: str) -> None:
    # arrange
    params: dict[str, str] = {"name": teil}
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(rest_url, params=params, headers=headers, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    content: Final = response_body["content"]
    for k in content:
        kiosk_name = k.get("name")
        assert kiosk_name is not None and isinstance(kiosk_name, str)
        assert teil.lower() in kiosk_name.lower()
        assert k.get("id") is not None

@mark.rest
@mark.get_request
@mark.parametrize("name", ["UnbekannterKiosk", "GibtsNicht"])
def test_get_by_name_not_found(name: str) -> None:
    # arrange
    params: dict[str, str] = {"name": name}
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(rest_url, params=params, headers=headers, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND

@mark.rest
@mark.get_request
@mark.parametrize("teil", ["a", "n"])
def test_get_kiosknamen(teil: str) -> None:
    # arrange
    token: Final = login()
    assert token is not None
    headers: dict[str, str] = {"Authorization": f"Bearer {token}"}

    # act
    # KORREKTUR: Pfad an 'namen' statt 'nachnamen' angepasst
    response: Final = get(
        f"{rest_url}/namen/{teil}",
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    kiosknamen: Final = response.json()
    assert isinstance(kiosknamen, list)
    assert len(kiosknamen) > 0
    for name in kiosknamen:
        assert teil.lower() in name.lower()

@mark.rest
@mark.get_request
@mark.parametrize("teil", ["xyz", "Abc"])
def test_get_kiosknamen_not_found(teil: str) -> None:
    # arrange
    token: Final = login()
    assert token is not None
    headers: dict[str, str] = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{rest_url}/namen/{teil}",
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND