"""Modul für persistente Kioskdaten."""

from kiosk.entity.base import Base
from kiosk.entity.betreiber import Betreiber
from kiosk.entity.geschlecht import Geschlecht
from kiosk.entity.kiosk import Kiosk
from kiosk.entity.produkt import Produkt

# https://docs.python.org/3/tutorial/modules.html#importing-from-a-package
__all__ = [
    "Base",
    "Betreiber",
    "Geschlecht",
    "Kiosk",
    "Produkt",
]
