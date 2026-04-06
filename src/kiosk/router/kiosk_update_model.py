"""Pydantic-Model zum Aktualisieren von Kioskdaten."""

from typing import Annotated, Any

from loguru import logger
from pydantic import BaseModel, ConfigDict, EmailStr, HttpUrl, StringConstraints

from kiosk.entity import Kiosk

__all__: list[str] = ["KioskUpdateModel"]


class KioskUpdateModel(BaseModel):
    """Pydantic-Model zum Aktualisieren von Kioskdaten."""

    # Validierung analog zum Kiosk-namen, angepasst auf Kiosknamen
    name: Annotated[
        str,
        StringConstraints(
            pattern=r"^[A-ZÄÖÜ].+$",
            max_length=64,
        ),
    ]
    """Der Name des Kiosks."""

    email: EmailStr
    """Die eindeutige Emailadresse."""

    ist_geoeffnet: bool
    """Angabe, ob der Kiosk aktuell geöffnet ist."""

    homepage: HttpUrl | None = None
    """Die optionale URL der Homepage."""

    model_config = ConfigDict(
        # Beispiel fuer OpenAPI (Swagger)
        json_schema_extra={
            "example": {
                "name": "Test",
                "email": "test@acme.com",
                "ist_geoeffnet": True,
                "homepage": "https://test.rest",
            },
        }
    )

    def to_dict(self) -> dict[str, Any]:
        """Konvertierung der primitiven Attribute in ein Dictionary.

        :return: Dictionary mit den primitiven Kiosk-Attributen
        :rtype: dict[str, Any]
        """
        # Model von Pydantic in ein Dictionary konvertieren
        kiosk_dict = dict[str, Any] = self.model_dump()
        
        # Felder, die nicht Teil des Updates sind oder später gesetzt werden, auf None/Standard setzen
        kiosk_dict["id"] = None
        kiosk_dict["betreiber"] = None
        kiosk_dict["produkte"] = []
        kiosk_dict["username"] = None
        kiosk_dict["version"] = 0
        kiosk_dict["erzeugt"] = None
        kiosk_dict["aktualisiert"] = None

        # HttpUrl ist ungeeignet fuer SQLAlchemy
        
        kiosk_dict["homepage"] = str(kiosk_dict["homepage"])    
        return kiosk_dict

    def to_kiosk(self) -> Kiosk:
        """Konvertierung in ein Kiosk-Objekt für SQLAlchemy.

        :return: Kiosk-Objekt für SQLAlchemy
        :rtype: Kiosk
        """
        logger.debug("self={}", self)
        kiosk_dict: dict[str, Any] = self.to_dict()

        # Dictionary auspacken als Schlüssel-Wert-Paare (Double Star Operator)
        kiosk = Kiosk(**kiosk_dict)
        logger.debug("kiosk={}", kiosk)
        return kiosk