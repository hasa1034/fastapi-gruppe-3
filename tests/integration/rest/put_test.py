# ruff: noqa: S101, D103
# Copyright (C) 2023 - present Juergen Zimmermann, Hochschule Karlsruhe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#

"""Tests für PUT."""

from http import HTTPStatus
from typing import Final

from common_test import ctx, login, rest_url
from httpx import put
from pytest import mark

EMAIL_UPDATE: Final = "update@kiosk.de"
HOMEPAGE_UPDATE: Final = "https://www.kiosk-neu.de"


@mark.rest
@mark.put_request
def test_put() -> None:
    # arrange
    kiosk_id: Final = 1000
    if_match: Final = '"0"'
    geaenderter_kiosk: Final = {
        "name": "Kioskput",
        "email": EMAIL_UPDATE,
        "ist_geoeffnet": False,
        "homepage": HOMEPAGE_UPDATE,
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{kiosk_id}",
        json=geaenderter_kiosk,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.NO_CONTENT
    assert not response.text


@mark.rest
@mark.put_request
def test_put_invalid() -> None:
    # arrange
    kiosk_id: Final = 1000
    geaenderter_kiosk_invalid: Final = {
        "name": "falscher_name_put", # Regex-Fehler (Kleinbuchstabe)
        "email": "falsche_email_put@",
        "ist_geoeffnet": "vielleicht", # Validierungsfehler (kein bool)
        "homepage": "https://?!",
    }
    token: Final = login()
    assert token is not None
    headers: dict[str, str] = {
        "If-Match": '"0"',
        "Authorization": f"Bearer {token}",
    }

    # act
    response: Final = put(
        f"{rest_url}/{kiosk_id}",
        json=geaenderter_kiosk_invalid,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert "name" in response.text
    assert "email" in response.text
    assert "homepage" in response.text


@mark.rest
@mark.put_request
def test_put_nicht_vorhanden() -> None:
    # arrange
    kiosk_id: Final = 999999
    if_match: Final = '"0"'
    geaenderter_kiosk: Final = {
        "name": "Kioskput",
        "email": EMAIL_UPDATE,
        "ist_geoeffnet": False,
        "homepage": HOMEPAGE_UPDATE,
    }
    token: Final = login()
    assert token is not None
    headers: dict[str, str] = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{kiosk_id}",
        json=geaenderter_kiosk,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND


@mark.rest
@mark.put_request
def test_put_email_exists() -> None:
    # arrange
    kiosk_id: Final = 1000
    if_match: Final = '"1"'
    email_exists: Final = "admin@acme.com"
    geaenderter_kiosk: Final = {
        "name": "Kioskput",
        "email": email_exists,
        "ist_geoeffnet": False,
        "homepage": HOMEPAGE_UPDATE,
    }
    token: Final = login()
    assert token is not None
    headers: dict[str, str] = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{kiosk_id}",
        json=geaenderter_kiosk,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert email_exists in response.text


@mark.rest
@mark.put_request
def test_put_ohne_versionsnr() -> None:
    # arrange
    kiosk_id: Final = 1000
    geaenderter_kiosk: Final = {
        "name": "Kioskput",
        "email": EMAIL_UPDATE,
        "ist_geoeffnet": False,
        "homepage": HOMEPAGE_UPDATE,
    }
    token: Final = login()
    assert token is not None
    headers: dict[str, str] = {
        "Authorization": f"Bearer {token}",
    }

    # act
    response: Final = put(
        f"{rest_url}/{kiosk_id}",
        json=geaenderter_kiosk,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.PRECONDITION_REQUIRED


@mark.rest
@mark.put_request
def test_put_alte_versionsnr() -> None:
    # arrange
    kiosk_id: Final = 1000
    if_match: Final = '"-1"'
    geaenderter_kiosk: Final = {
        "name": "Kioskput",
        "email": EMAIL_UPDATE,
        "ist_geoeffnet": False,
        "homepage": HOMEPAGE_UPDATE,
    }
    token: Final = login()
    assert token is not None
    headers: dict[str, str] = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{kiosk_id}",
        json=geaenderter_kiosk,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.PRECONDITION_FAILED


@mark.rest
@mark.put_request
def test_put_ungueltige_versionsnr() -> None:
    # arrange
    kiosk_id: Final = 1000
    if_match: Final = '"xy"'
    geaenderter_kiosk: Final = {
        "name": "Kioskput",
        "email": EMAIL_UPDATE,
        "ist_geoeffnet": False,
        "homepage": HOMEPAGE_UPDATE,
    }
    token: Final = login()
    assert token is not None
    headers: dict[str, str] = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{kiosk_id}",
        json=geaenderter_kiosk,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.PRECONDITION_FAILED
    assert not response.text


@mark.rest
@mark.put_request
def test_put_versionsnr_ohne_quotes() -> None:
    # arrange
    kiosk_id: Final = 1000
    if_match: Final = "0"
    geaenderter_kiosk: Final = {
        "name": "Kioskput",
        "email": EMAIL_UPDATE,
        "ist_geoeffnet": False,
        "homepage": HOMEPAGE_UPDATE,
    }
    token: Final = login()
    assert token is not None
    headers: dict[str, str] = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{kiosk_id}",
        json=geaenderter_kiosk,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.PRECONDITION_FAILED