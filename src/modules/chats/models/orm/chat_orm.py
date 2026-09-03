from sqlalchemy import DateTime, func, Uuid, Index, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base
from uuid import uuid4
from datetime import datetime
from typing import List

from ...chat_types.chat_types import ChatType


class ChatORM(Base):
    __tablename__ = "chats"

    uuid: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    chat_type: Mapped[ChatType] = mapped_column(Enum(ChatType))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    messages: Mapped[List["MessageORM"]] = relationship(
        "MessageORM",
        back_populates="chat",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="MessageORM.created_at.desc()",
    )

    __table_args__ = (Index("idx_chats_type", "chat_type"),)
