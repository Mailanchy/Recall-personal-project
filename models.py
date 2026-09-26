from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import func
import uuid
import datetime


class Base(DeclarativeBase):
    pass

class Material(Base):
    __tablename__ = "materials"

    id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, primary_key=True)
    name: Mapped[str]
    last_processed: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    content_hash: Mapped[str] = mapped_column(String(64)) # hashlib.sha256
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True) ,server_default=func.now())

class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    material_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("materials.id"))
    headings: Mapped[str] = mapped_column(Text)
    position: Mapped[int]


