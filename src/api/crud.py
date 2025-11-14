from typing import Any, Optional, Protocol, TypeVar, Union, overload

from sqlalchemy import UnaryExpression
from sqlalchemy.orm import InstrumentedAttribute, Mapped, Session

from src.api.database import (
    AnonymizationEvent,
    Base,
    Document,
    Tag,
)


async def commit_session(db: Session) -> None:
    """Commit the session and handle any errors."""
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise e


class BaseWithId(Protocol):
    id: Mapped[int]


class BaseWithUuid(Protocol):
    id: Mapped[str]


Entity = TypeVar("Entity", bound=Base)
EntityWithId = TypeVar("EntityWithId", bound=BaseWithId)
EntityWithUuid = TypeVar("EntityWithUuid", bound=BaseWithUuid)


def get_entity(
    db: Session, entity: type[EntityWithId], id: int
) -> Optional[EntityWithId]:
    return db.query(entity).filter(entity.id == id).first()


def get_entity_uuid(
    db: Session, entity: type[EntityWithUuid], uuid: str
) -> Optional[EntityWithUuid]:
    return db.query(entity).filter(entity.id == uuid).first()


def get_entity_by_field(
    db: Session,
    entity: type[Entity],
    field: InstrumentedAttribute[Any],
    value: Union[str, int, bool],
) -> Optional[Entity]:
    return db.query(entity).filter(field == value).first()


def get_entity_by_field_in(
    db: Session,
    entity: type[Entity],
    field: InstrumentedAttribute[Any],
    value: list[str | int | bool],
) -> list[Entity]:
    return db.query(entity).filter(field.in_(value)).all()


def get_entities(db: Session, entity: type[Entity]) -> list[Entity]:
    return db.query(entity).all()


def get_entities_by_field(
    db: Session,
    entity: type[Entity],
    field: InstrumentedAttribute[Any],
    value: Union[str, int, bool],
) -> list[Entity]:
    return db.query(entity).filter(field == value).all()


def get_entites_by_field_paged(
    db: Session,
    entity: type[Entity],
    field: InstrumentedAttribute[Any],
    value: str | int | bool,
    limit: int,
    offset: int,
    sort: UnaryExpression[Any],
) -> list[Entity]:
    return (
        db.query(entity)
        .filter(field == value)
        .order_by(sort)
        .limit(limit)
        .offset(offset)
        .all()
    )


@overload
async def delete_entity(db: Session, entity: type[EntityWithUuid], id: str) -> None: ...


@overload
async def delete_entity(db: Session, entity: type[EntityWithId], id: int) -> None: ...


async def delete_entity(
    db: Session, entity: type[EntityWithUuid | EntityWithId], id: str | int
) -> None:
    db.query(entity).filter(entity.id == id).delete()
    await commit_session(db)


async def delete_entities(db: Session, entity: type[Entity]) -> None:
    db.query(entity).delete()
    await commit_session(db)


# Document-specific CRUD functions
def create_document(
    db: Session,
    id: str,
    filename: str,
    content_type: str,
    source_path: str,
    anonymized_path: Optional[str] = None,
    pii_entities: Optional[str] = None,
) -> Document:
    """Create a new document."""
    db_document = Document(
        id=id,
        filename=filename,
        content_type=content_type,
        source_path=source_path,
        anonymized_path=anonymized_path,
        pii_entities=pii_entities,
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


def create_tag(db: Session, id: str, name: str, document_id: str) -> Tag:
    """Create a new tag."""
    tag = Tag(id=id, name=name, document_id=document_id)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


def create_anonymization_event(
    db: Session, document_id: str, time_taken: int, status: str
) -> AnonymizationEvent:
    """Create a new anonymization event."""
    event = AnonymizationEvent(
        document_id=document_id, time_taken=time_taken, status=status
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def update_document_anonymized_path(
    db: Session, document_id: str, anonymized_path: str
) -> Optional[Document]:
    """Update the anonymized path of a document."""
    document = db.query(Document).filter(Document.id == document_id).first()
    if document:
        document.anonymized_path = anonymized_path
        db.commit()
        db.refresh(document)
    return document


def get_document(db: Session, document_id: str) -> Optional[Document]:
    """Get a document by ID."""
    return db.query(Document).filter(Document.id == document_id).first()
