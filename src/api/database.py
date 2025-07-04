from datetime import datetime
from typing import Dict, Generator, List, Optional

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Session, relationship, sessionmaker

from src.api.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class Document(Base):
    """Document model based on the ERD."""

    __tablename__ = "documents"

    id = Column(String(32), primary_key=True)
    filename = Column(Text, nullable=False)
    content_type = Column(Text, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.now)
    source_path = Column(Text, nullable=False)
    anonymized_path = Column(Text, nullable=True)

    # Relationships
    tags = relationship("Tag", back_populates="document", cascade="all, delete-orphan")
    anonymization_events = relationship(
        "AnonymizationEvent", back_populates="document", cascade="all, delete-orphan"
    )

    # Store entities as JSON in memory (not in database)
    _entities: Optional[List[Dict[str, str]]] = None


class Tag(Base):
    """Tag model based on the ERD."""

    __tablename__ = "tags"

    id = Column(String(32), primary_key=True)
    document_id = Column(String(32), ForeignKey("documents.id"))
    name = Column(Text, nullable=False)

    # Relationship
    document = relationship("Document", back_populates="tags")


class AnonymizationEvent(Base):
    """AnonymizationEvent model based on the ERD."""

    __tablename__ = "anonymization_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String(32), ForeignKey("documents.id"))
    anonymized_at = Column(DateTime, default=datetime.now)
    time_taken = Column(Integer, nullable=False)  # Seconds
    status = Column(Text, nullable=False)

    # Relationship
    document = relationship("Document", back_populates="anonymization_events")

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
