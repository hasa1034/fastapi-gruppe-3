"""Pydantic-Model für die Produktdaten."""

from decimal import Decimal
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, StringConstraints

from kiosk.entity import Produkt

__all__: list[str] = ["ProduktModel"]


class ProduktModel(BaseModel):
    """Pydantic-Model für die Produktdaten."""

    name: str
    """Der Name des Produkts."""
    
    preis: Decimal
    """Der Preis."""
    
    waehrung: Annotated[str, StringConstraints(pattern=r"^[A-Z]{3}$")]
    """Die Währung (3 Großbuchstaben, z.B. EUR)."""

    model_config = ConfigDict(
        # Beispiel für OpenAPI / Swagger
        json_schema_extra={
            "example": {
                "name": "Limonade",
                "preis": "2.50",
                "waehrung": "EUR",
            },
        }
    )

    def to_produkt(self) -> Produkt:
        """Konvertierung in ein Produkt-Objekt für SQLAlchemy.

        :return: Produkt-Objekt für SQLAlchemy
        :rtype: Produkt
        """
        # Model von Pydantic in ein Dictionary konvertieren
        produkt_dict: dict[stry, Any] = self.model_dump()
        
        # Felder, die in der Datenbank automatisch gesetzt werden oder 
        # erst später verknüpft werden, auf None setzen
        produkt_dict["id"] = None
        produkt_dict["kiosk_id"] = None
        produkt_dict["kiosk"] = None

        # Double Star Operator packt das Dict als Argumente für den Konstruktor aus
        return Produkt(**produkt_dict)