from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON, Uuid, DateTime, String, ForeignKey, text, func, Index
from typing import List, Optional

from uuid import uuid4
from datetime import datetime

from src.core.database import Base
from ...types.base.base_message_data import base_message_data_type


class MessageORM(Base):
    __tablename__ = "messages"

    uuid: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )

    message_data: Mapped[List[base_message_data_type]] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    chat_uuid: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("chats.uuid", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_uuid: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.uuid", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    chat: Mapped["ChatORM"] = relationship(
        "ChatORM",
        back_populates="messages",
        lazy="selectin"
    )

    user: Mapped["UserORM"] = relationship(
        "UserORM",
        back_populates="messages",
        lazy="selectin",
        foreign_keys=[user_uuid]
    )

    __table_args__ = (
        Index("idx_message_created_at", "created_at"),
        Index(
            "idx_message_data_gin",
            "message_data",
            postgresql_using="gin",
            postgresql_ops={"message_data": "jsonb_path_ops"},
        ),
        Index(
            "idx_message_data_type_btree",
            text("(message_data->>'data_type')"),
            postgresql_using="btree",
        ),
        Index("idx_message_chat_user", "chat_uuid", "user_uuid"),
        Index("idx_message_chat_created", "chat_uuid", "created_at"),
    )
