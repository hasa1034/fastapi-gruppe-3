# ruff: noqa: S101, D103
# Copyright (C) 2022 - present Juergen Zimmermann, Hochschule Karlsruhe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#

"""Tests für Queries mit GraphQL."""

from http import HTTPStatus
from typing import Final

from common_test import ctx, graphql_url, login_graphql
from httpx import post
from pytest import mark

GRAPHQL_PATH: Final = "/graphql"


@mark.graphql
@mark.query
def test_query_id() -> None:
    # arrange
    token: Final = login_graphql()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    query: Final = {
        "query": """
            {
                kiosk(kioskId: "1000") {
                    version
                    name
                    email
                    istGeoeffnet
                    homepage
                    username
                    betreiber {
                        vorname
                        nachname
                        geschlecht
                    }
                    produkte {
                        name
                        preis
                        waehrung
                    }
                }
            }
        """,
    }

    # act
    response: Final = post(graphql_url, json=query, headers=headers, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    data: Final = response_body["data"]
    assert data is not None
    kiosk: Final = data["kiosk"]
    assert isinstance(kiosk, dict)
    assert kiosk["name"] is not None
    assert response_body.get("errors") is None


@mark.graphql
@mark.query
def test_query_id_notfound() -> None:
    # arrange
    token: Final = login_graphql()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    query: Final = {
        "query": """
            {
                kiosk(kioskId: "999999") {
                    name
                }
            }
        """,
    }

    # act
    response: Final = post(graphql_url, json=query, headers=headers, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    assert response_body["data"]["kiosk"] is None
    assert response_body.get("errors") is None


@mark.graphql
@mark.query
def test_query_email() -> None:
    # arrange
    token: Final = login_graphql()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    query: Final = {
        "query": """
            {
                kioske(suchparameter: {email: "admin@acme.com"}) {
                    id
                    version
                    name
                    email
                    istGeoeffnet
                    betreiber {
                        nachname
                    }
                }
            }
        """,
    }

    # act
    response: Final = post(graphql_url, json=query, headers=headers, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    kioske: Final = response_body["data"]["kioske"]
    assert isinstance(kioske, list)
    assert len(kioske) > 0
    assert response_body.get("errors") is None


@mark.graphql
@mark.query
def test_query_name() -> None:
    # arrange
    token: Final = login_graphql()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    query: Final = {
        "query": """
            {
                kioske(suchparameter: {name: "Kiosk"}) {
                    id
                    name
                    produkte {
                        name
                    }
                }
            }
        """,
    }

    # act
    response: Final = post(graphql_url, json=query, headers=headers, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    kioske: Final = response_body["data"]["kioske"]
    assert isinstance(kioske, list)
    assert len(kioske) > 0
    assert response_body.get("errors") is None


@mark.graphql
@mark.query
def test_query_name_notfound() -> None:
    # arrange
    token: Final = login_graphql()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    query: Final = {
        "query": """
            {
                kioske(suchparameter: {name: "Nichtvorhanden"}) {
                    id
                }
            }
        """,
    }

    # act
    response: Final = post(graphql_url, json=query, headers=headers, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    kioske: Final = response_body["data"]["kioske"]
    assert isinstance(kioske, list)
    assert len(kioske) == 0
