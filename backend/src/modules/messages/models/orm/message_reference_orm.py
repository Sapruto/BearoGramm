from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid, DateTime, String, ForeignKey, func, Index, Enum, text, Integer, Boolean
from typing import Optional

from uuid import uuid4
from datetime import datetime

from ..enums.reference_type import ReferenceType

from src.core.database import Base


class MessageReferenceORM(Base):
    __tablename__ = "message_reference"

    uuid: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )

    reference_type: Mapped[ReferenceType] = mapped_column(
        Enum(
            ReferenceType,
            name="reference_type",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )

    source_uuid: Mapped[str] = mapped_column(
        String(36), ForeignKey("messages.uuid", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    target_uuid: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("messages.uuid", ondelete="SET NULL"),
        nullable=True, index=True,
    )

    span_start: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    span_end: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    span_all: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    source: Mapped["MessageORM"] = relationship(
        "MessageORM", foreign_keys=[source_uuid],
        back_populates="references", lazy="raise",
    )
    target: Mapped[Optional["MessageORM"]] = relationship(
        "MessageORM", foreign_keys=[target_uuid], lazy="raise",
    )

    __table_args__ = (
        Index(
            "uq_msg_ref_source_type",
            "source_uuid", "reference_type",
            unique=True,
            postgresql_where=text("reference_type IN ('answer', 'quote')"),
        ),
        Index("ix_msg_ref_target_type", "target_uuid", "reference_type"),
    )
