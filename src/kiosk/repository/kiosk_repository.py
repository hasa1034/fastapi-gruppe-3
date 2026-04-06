
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
            .options(joinedload(Kiosk.betreiber))
            .where(Kiosk.id == kiosk_id)
        )
        kiosk: Final = session.scalar(statement)
        logger.debug("{}", kiosk)
        return kiosk
    
    

    def find(self, suchparameter: Mapping[str, str], pageable: Pageable, session: Session) -> Slice[Kiosk]:
        """Suche Kioske mit Filtern (z.B. Name oder Email)."""
        log_str: Final = "{}"
        logger.debug(log_str, suchparameter)
        
        if not suchparameter:
            return self._find_all(pageable=pageable, session=session)

        
        for key, value in suchparameter.items():
            if key == "email":
                kiosk: Kiosk | None = self._find_by_email(email=value, session=session)
                logger.debug(log_str, kiosk)
                return (
                    Slice(content=(kiosk,), total_elements=1)
                    if kiosk is not None
                    else Slice(content=(), total_elements=0))
            if key == "name":
                kiosken: Slice[Kiosk] = self._find_by_name(teil=value, pageable=pageable, session=session)
                logger.debug(log_str, kiosken)
                return kiosken
        return Slice(content=(), total_elements=0)

    def _find_all(self, pageable: Pageable, session: Session) -> Slice[Kiosk]:
        logger.debug("aufgerufen")
        offset: int = pageable.number * pageable.size
        statement: Final = ((
            select(Kiosk)
            .options(joinedload(Kiosk.betreiber))
            .limit(pageable.size)
            .offset(offset)
        )   
            if pageable.size != 0
            else (select(Kiosk).options(joinedload(Kiosk.betreiber)))                   
        )
        kiosken: Final = (session.scalars(statement)).all()
        anzahl: Final = self._count_all_rows(session)
        kiosk_slice: Final = Slice(content=tuple(kiosken), total_elements=anzahl)
        logger.debug("kiosk_slice={}", kiosk_slice)
        return kiosk_slice
    
    def _count_all_rows(self, session: Session) -> int:
        statement: Final = select(func.count()).select_from(Kiosk)
        count: Final = session.execute(statement).scalar()
        return count if count is not None else 0


    def _find_by_email(self, email: str, session: Session) -> Kiosk | None:
        
        logger.debug("email={}", email)
        statement: Final = (
            select(Kiosk)
            .options(joinedload(Kiosk.betreiber))
            .where(Kiosk.email == email)
        )
        kiosk: Final = session.scalar(statement)
        logger.debug("{}", kiosk)
        return kiosk

    
    def _find_by_name(
        self,
        teil: str,
        pageable: Pageable,
        session: Session,
    ) -> Slice[Kiosk]:
        logger.debug("teil={}", teil)
        offset: int = pageable.number * pageable.size
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#querying
        statement: Final = (
            (
                select(Kiosk)
                .options(joinedload(Kiosk.betreiber))
                .filter(Kiosk.name.ilike(f"%{teil}%"))
                .limit(pageable.size)
                .offset(offset)
            )
            if pageable.size != 0
            else (
                select(Kiosk)
                .options(joinedload(Kiosk.betreiber))
                .filter(Kiosk.name.ilike(f"%{teil}%"))
            )
        )
        kioske: Final = session.scalars(statement).all()
        anzahl: Final = self._count_rows_nachname(teil, session)
        kiosk_slice: Final = Slice(content=tuple(kioske), total_elements=anzahl)
        logger.debug("{}", kiosk_slice)
        return kiosk_slice

    def _count_rows_name(self, teil: str, session: Session) -> int:
        statement: Final = (
            select(func.count())
            .select_from(Kiosk)
            .filter(Kiosk.name.ilike(f"%{teil}%"))
        )
        count: Final = session.execute(statement).scalar()
        return count if count is not None else 0

    def exists_email(self, email: str, session: Session) -> bool:
        """Abfrage, ob es die Emailadresse bereits gibt.

        :param email: Emailadresse
        :param session: Session für SQLAlchemy
        :return: True, falls es die Emailadresse bereits gibt, False sonst
        :rtype: bool
        """
        logger.debug("email={}", email)

        statement: Final = select(func.count()).where(Kiosk.email == email)
        anzahl: Final = session.scalar(statement)
        logger.debug("anzahl={}", anzahl)
        return anzahl is not None and anzahl > 0

    def exists_email_other_id(
        self,
        email: str,
        kiosk_id: int,
        session: Session,
    ) -> bool:
        """Abfrage, ob es die Emailadresse bei einer anderen Kiosk-ID bereits gibt.

        :param email: Emailadresse
        :param kiosk_id: eigene Kiosk-ID
        :param session: Session für SQLAlchemy
        :return: True, falls es die Emailadresse bereits gibt, False sonst
        :rtype: bool
        """
        logger.debug("email={}", email)

        statement: Final = select(Kiosk.id).where(Kiosk.email == email)
        id_db: Final = session.scalar(statement)
        logger.debug("id_db={}", id_db)
        return id_db is not None and id_db != kiosk_id

    def create(self, kiosk: Kiosk, session: Session) -> Kiosk:
        """Speichere einen neuen Kiosk ab.

        :param kiosk: Die Daten des neuen Kiosks ohne ID
        :param session: Session für SQLAlchemy
        :return: Der neu angelegte Kiosk mit generierter ID
        :rtype: Kiosk
        """
        logger.debug(
            "kiosk={}, kiosk.betreiber={}, kiosk.produkte={}",
            kiosk,
            kiosk.betreiber,
            kiosk.produkte,
        )
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#adding-new-or-existing-items
        session.add(instance=kiosk)
        # flush(), damit die ID aus der Sequence vor COMMIT fuer Logging verfuegbar ist
        # https://docs.sqlalchemy.org/en/20/tutorial/orm_data_manipulation.html#flushing
        session.flush(objects=[kiosk])
        logger.debug("kiosk_id={}", kiosk.id)
        return kiosk

    def update(self, kiosk: Kiosk, session: Session) -> Kiosk | None:
        """Aktualisiere einen Kiosk.

        :param kiosk: Die neuen Kioskdaten
        :param session: Session für SQLAlchemy
        :return: Der aktualisierte Kiosk oder None, falls kein Kiosk mit der ID
        existiert
        :rtype: Kiosk | None
        """
        logger.debug("{}", kiosk)

        if (
            kiosk_db := self.find_by_id(kiosk_id=kiosk.id, session=session)
        ) is None:
            # Kioskdaten wurden i.a. zuvor in der Session aktualisiert
            return None

        # session.add(kiosk_db) nicht notwendig, da bereits in der Session zugegriffen
        # CAVEAT: Die erhoehte Versionsnummer ist erst *nach* COMMIT sichtbar

        logger.debug("{}", kiosk_db)
        return kiosk_db

    def delete_by_id(self, kiosk_id: int, session: Session) -> None:
        """Lösche die Daten zu einem Kiosk.

        :param kiosk_id: Die ID des zu löschenden Kiosks
        :param session: Session für SQLAlchemy
        """
        logger.debug("kiosk_id={}", kiosk_id)

        # delete(Kiosk).where(Kiosk.kiosk_id == kiosk_id) OHNE cascade
        # "walrus operator" https://peps.python.org/pep-0572
        if (kiosk := self.find_by_id(kiosk_id=kiosk_id, session=session)) is None:
            return
        session.delete(kiosk)
        logger.debug("ok")

    def find_namen(self, teil: str, session: Session) -> Sequence[str]:
        """Suche Namen zu einem Teilstring.

        :param teil: Teilstring zu den gesuchten Namen
        :param session: Session für SQLAlchemy
        :return: Liste der gefundenen Namen oder eine leere Liste
        :rtype: Sequence[str]
        """
        logger.debug("teil={}", teil)

        statement: Final = (
            select(Kiosk.name)
            .filter(Kiosk.name.ilike(f"%{teil}%"))
            .distinct()
        )
        namen: Final = (session.scalars(statement)).all()

        logger.debug("namen={}", namen)
        return namen

    def exists_username(self, username: str | None, session: Session) -> bool:
        """Abfrage, ob es den Benutzernamen bereits gibt.

        :param username: Benutzername
        :param session: Session für SQLAlchemy
        :return: True, falls es den Benutzernamen bereits gibt
        :rtype: bool
        """
        logger.debug("username={}", username)
        if username is None:
            return False

        statement: Final = select(Kiosk.username).filter_by(username=username)
        username_db: Final = session.scalar(statement)
        logger.debug("username_db={}", username_db)
        return username_db is not None

