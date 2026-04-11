"""Modul für die GraphQL-Schnittstelle."""

from kiosk.graphql_api.graphql_types import (
    BetreiberInput,
    CreatePayload,
    KioskInput,
    ProduktInput,
    Suchparameter,
)
from kiosk.graphql_api.schema import Mutation, Query, graphql_router

__all__ = [
    "BetreiberInput",
    "CreatePayload",
    "KioskInput",
    "Mutation",
    "ProduktInput",
    "Query",
    "Suchparameter",
    "graphql_router",
]
