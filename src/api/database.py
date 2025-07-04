from datetime import datetime
from typing import Dict, Generator, List, Optional

from sqlalchemy import ForeignKey, String, Text, create_engine, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    sessionmaker,
)

from src.api.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    __allow_unmapped__ = True


class Document(Base):
    """Document model based on the ERD."""

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    filename: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(Text, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(server_default=func.now())
    source_path: Mapped[str] = mapped_column(Text, nullable=False)
    anonymized_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    tags: Mapped[List["Tag"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )
    anonymization_events: Mapped[List["AnonymizationEvent"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )

    # Store entities as JSON in memory (not in database)
    _entities: Optional[List[Dict[str, str]]] = None


class Tag(Base):
    """Tag model based on the ERD."""

    __tablename__ = "tags"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(32), ForeignKey("documents.id"))
    name: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationship
    document: Mapped["Document"] = relationship(back_populates="tags")


class AnonymizationEvent(Base):
    """AnonymizationEvent model based on the ERD."""

    __tablename__ = "anonymization_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(32), ForeignKey("documents.id"))
    anonymized_at: Mapped[datetime] = mapped_column(server_default=func.now())
    time_taken: Mapped[int] = mapped_column(nullable=False)  # Seconds
    status: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationship
    document: Mapped["Document"] = relationship(back_populates="anonymization_events")

    # Store PII entities as JSON in memory (not in database)
    _pii_entities: Optional[List[Dict[str, str]]] = None

    @property
    def pii_entities(self) -> Optional[List[Dict[str, str]]]:
        return self._pii_entities

    @pii_entities.setter
    def pii_entities(self, value: List[Dict[str, str]]) -> None:
        self._pii_entities = value


# Create the database tables
Base.metadata.create_all(bind=engine)


# Dependency
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
