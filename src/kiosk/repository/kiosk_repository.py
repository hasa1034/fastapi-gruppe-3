

"""Repository fuer persistente Kioskdaten."""

# "list" ist eine mutable "Sequence"
# https://docs.python.org/3/library/stdtypes.html#lists
# https://docs.python.org/3/library/stdtypes.html#typesseq
from collections.abc import Mapping, Sequence
from typing import Final

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from kiosk.entity import Kiosk
from kiosk.repository.pageable import Pageable
from kiosk.repository.slice import Slice

__all__ = ["KioskRepository"]


class KioskRepository:
    """Repository-Klasse mit CRUD-Methoden für die Entity-Klasse Kiosk."""

    def find_by_id(self, kiosk_id: int | None, session: Session) -> Kiosk | None:
        """Suche einen Kiosk anhand der ID inkl. Betreiber und Produkte."""
        logger.debug("kiosk_id={}", kiosk_id)
        if kiosk_id is None:
            return None

        # Wir laden Betreiber (1:1) und Produkte (1:N) direkt mit (Eager Loading)
        statement: Final = (
            select(Kiosk)
            .options(
                joinedload(Kiosk.betreiber),
                joinedload(Kiosk.produkte)
            )
            .where(Kiosk.id == kiosk_id)
        )
        return session.scalar(statement)

    def find(self, suchparameter: Mapping[str, str], pageable: Pageable, session: Session) -> Slice[Kiosk]:
        """Suche Kioske mit Filtern (z.B. Name oder Email)."""
        logger.debug("suchparameter={}", suchparameter)
        
        if not suchparameter:
            return self._find_all(pageable, session)

        # Beispiel: Suche nach Name
        for key, value in suchparameter.items():
            if key == "name":
                return self._find_by_name(value, pageable, session)
            if key == "email":
                kiosk = self._find_by_email(value, session)
                return Slice(content=(kiosk,), total_elements=1) if kiosk else Slice(content=(), total_elements=0)
        
        return Slice(content=(), total_elements=0)

    def _find_all(self, pageable: Pageable, session: Session) -> Slice[Kiosk]:
        offset = pageable.number * pageable.size
        statement: Final = (
            select(Kiosk)
            .options(joinedload(Kiosk.betreiber))
            .limit(pageable.size)
            .offset(offset)
        )
        kioske = session.scalars(statement).all()
        anzahl = session.scalar(select(func.count()).select_from(Kiosk)) or 0
        return Slice(content=tuple(kioske), total_elements=anzahl)
    
    
    def _find_by_email(self, email: str, session: Session) -> Kiosk | None:
        statement: Final = (
            select(Kiosk)
            .options(joinedload(Kiosk.betreiber))
            .where(Kiosk.email == email)
        )
        return session.scalar(statement)

    
    def _find_by_name(self, teil: str, pageable: Pageable, session: Session) -> Slice[Kiosk]:
        offset = pageable.number * pageable.size
        statement: Final = (
            select(Kiosk)
            .options(joinedload(Kiosk.betreiber))
            .filter(Kiosk.name.ilike(f"%{teil}%"))
            .limit(pageable.size)
            .offset(offset)
        )
        kioske = session.scalars(statement).all()
        anzahl = session.scalar(
            select(func.count()).select_from(Kiosk).filter(Kiosk.name.ilike(f"%{teil}%"))
        ) or 0
        return Slice(content=tuple(kioske), total_elements=anzahl)
    
    

    def create(self, kiosk: Kiosk, session: Session) -> Kiosk:
        """Speichert einen neuen Kiosk und vergibt eine ID."""
        logger.debug("Speichere Kiosk: {}", kiosk.name)
        session.add(kiosk)
        session.flush() # ID generieren lassen
        return kiosk

    def delete_by_id(self, kiosk_id: int, session: Session) -> None:
        """Löscht einen Kiosk (und durch 'cascade' auch den Betreiber/Produkte)."""
        if (kiosk := self.find_by_id(kiosk_id, session)) is not None:
            session.delete(kiosk)
            logger.debug("Kiosk {} gelöscht", kiosk_id)