"""Pydantic-Model für die  Kioskdaten."""

from typing import Annotated, Final

from loguru import logger
from pydantic import StringConstraints

from kiosk.entity import Kiosk
from kiosk.router.betreiber_model import BetreiberModel
from kiosk.router.produkt_model import ProduktModel
from kiosk.router.kiosk_update_model import KioskUpdateModel

__all__: list[str] = ["KioskModel"]

class KioskModel(KioskUpdateModel):
    """Vollständiges Pydantic-Model für die API."""

    betreiber: BetreiberModel
    """Der zugehörige Betreiber (1:1)."""

    produkte: list[ProduktModel]
    """Die Liste der Produkte (1:N)."""

    username: Annotated[str, StringConstraints(max_length=20)]
    """Der Benutzername für den Login."""

    def to_kiosk(self) -> Kiosk:
        """Konvertierung in ein Kiosk-Objekt für SQLAlchemy (Entity)."""
        logger.debug("self={}", self)
        
        # 1. Einfache Daten aus dem UpdateModel holen
        kiosk_dict = self.to_dict()
        
        # 2. Username hinzufügen (der oft nicht Teil des UpdateModels ist)
        kiosk_dict["username"] = self.username
        
        # 3. Kiosk-Entity initialisieren
        # Da id, version, erzeugt etc. von DB kommen, setzen wir sie auf None
        kiosk_dict["id"] = None
        kiosk_dict["version"] = 0
        
        kiosk: Final = Kiosk(**kiosk_dict)

        # 4. Betreiber konvertieren und verknüpfen
        kiosk.betreiber = self.betreiber.to_betreiber()
        
        # 5. Produkte konvertieren und verknüpfen
        kiosk.produkte = [
            p.to_produkt() for p in self.produkte
        ]

        logger.debug("Erzeugte Kiosk-Entity: {}", kiosk)
        return kiosk