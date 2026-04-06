# ruff: noqa: S101, D103
# Copyright (C) 2023 - present Juergen Zimmermann, Hochschule Karlsruhe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#

"""Tests für POST."""

from http import HTTPStatus
from re import search
from typing import Final

from common_test import ctx, rest_url
from httpx import post
from pytest import mark

token: str | None


@mark.rest
@mark.post_request
def test_post() -> None:
    # arrange
    neuer_kiosk: Final = {
        "name": "Kioskrest",
        "email": "testrest@kiosk.de",
        "ist_geoeffnet": True,
        "homepage": "https://kiosk-rest.de",
        "username": "testrest",
        "betreiber": {
            "vorname": "Max",
            "nachname": "Mustermann",
            "geschlecht": "M"
        },
        "produkte": [
            {"name": "Limonade", "preis": "2.50", "waehrung": "EUR"}
        ]
    }
    headers: dict[str, str] = {"Content-Type": "application/json"}

    # act
    response: Final = post(
        rest_url,
        json=neuer_kiosk,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.CREATED
    location: Final = response.headers.get("Location")
    assert location is not None
    # Prüft, ob die Location auf eine ID endet (z.B. /rest/1005)
    int_pattern: Final = "[1-9][0-9]*$"
    assert search(int_pattern, location) is not None
    assert not response.text


@mark.rest
@mark.post_request
def test_post_invalid() -> None:
    # arrange
    neuer_kiosk_invalid: Final = {
        "name": "falscher_name", # Kleinbuchstabe am Anfang verletzt Regex
        "email": "falsche_email@",
        "ist_geoeffnet": "kein_boolean",
        "homepage": "https://?!",
        "username": "testrestinvalid",
        "betreiber": {
            "vorname": "", # Validierungsfehler: darf nicht leer sein
            "nachname": "M",
            "geschlecht": "X" # Ungültiges Geschlecht
        }
    }
    headers: dict[str, str] = {"Content-Type": "application/json"}

    # act
    response: Final = post(
        rest_url,
        json=neuer_kiosk_invalid,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    body: str = response.text
    # Wir prüfen, ob die Pydantic-Fehlermeldungen die richtigen Felder nennen
    assert "name" in body
    assert "email" in body
    assert "homepage" in body
    assert "vorname" in body


@mark.rest
@mark.post_request
def test_post_email_exists() -> None:
    # arrange
    email_exists: Final = "admin@acme.com"
    neuer_kiosk: Final = {
        "name": "Kioskdoppelt",
        "email": email_exists,
        "ist_geoeffnet": True,
        "username": "emailexists",
        "betreiber": {
            "vorname": "John",
            "nachname": "Doe",
            "geschlecht": "M"
        }
    }
    headers: dict[str, str] = {"Content-Type": "application/json"}

    # act
    response: Final = post(
        rest_url,
        json=neuer_kiosk,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert email_exists in response.text


@mark.rest
@mark.post_request
def test_post_invalid_json() -> None:
    # arrange
    json_invalid: Final = '{"name" "Kiosk"}' # Fehlender Doppelpunkt
    headers: dict[str, str] = {"Content-Type": "application/json"}

    # act
    response: Final = post(
        rest_url,
        json=json_invalid,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert "should be a valid dictionary" in response.text