from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import DateTime, String, Integer, Enum, Boolean
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from src.core.database import Base

from .enums import MediaType


class MediaORM(Base):
    __tablename__ = "media"

    uuid: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    full_url: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    url: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    hash: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    content_type: Mapped[str] = mapped_column(String, nullable=False)
    media_type: Mapped[MediaType] = mapped_column(
        Enum(
            MediaType,
            name="gender",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        default=MediaType.ATTACHMENT,
    )
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    ptrs: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    is_server_file: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=lambda: datetime.now(timezone.utc),
    )
