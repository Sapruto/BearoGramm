from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, String, ForeignKey, func, Index, Boolean, Text
from typing import List, Optional

from uuid import uuid4
from datetime import datetime

from src.core.database import Base


class MessageORM(Base):
    __tablename__ = "messages"

    uuid: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )

    message_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, onupdate=func.now()
    )

    has_extra_data: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)
    extra_data: Mapped[Optional["MessageDataORM"]] = relationship(
        "MessageDataORM",
        back_populates="message",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="raise",
    )

    references: Mapped[List["MessageReferenceORM"]] = relationship(
        "MessageReferenceORM",
        foreign_keys="MessageReferenceORM.source_uuid",
        back_populates="source",
        cascade="all, delete-orphan",
        lazy="raise",
    )

    chat_uuid: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("chats.uuid", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chat: Mapped["ChatORM"] = relationship(
        "ChatORM",
        back_populates="messages",
        lazy="selectin"
    )

    user_uuid: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.uuid", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    user: Mapped["UserORM"] = relationship(
        "UserORM",
        back_populates="messages",
        lazy="selectin",
        foreign_keys=[user_uuid]
    )

    __table_args__ = (
        Index("idx_message_chat_created", "chat_uuid", "created_at"),
    )
