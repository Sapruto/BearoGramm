from sqlalchemy import String, ForeignKey, DateTime, func, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import Optional
from datetime import datetime
from uuid import uuid4

from src.core.database import Base


class ChatReadingORM(Base):
    __tablename__ = "chat_reading"

    uuid: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    chat_uuid: Mapped[str] = mapped_column(
        String(36), ForeignKey("chats.uuid", ondelete="CASCADE"), nullable=False
    )
    user_uuid: Mapped[str] = mapped_column(String(36), nullable=False)

    last_read_message_uuid: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("messages.uuid", ondelete="SET NULL"),
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=func.now(), onupdate=func.now(),
    )

    chat: Mapped["ChatORM"] = relationship("ChatORM", back_populates="read_states")

    __table_args__ = (
        UniqueConstraint("chat_uuid", "user_uuid", name="uq_chat_read_state_user"),
        Index("idx_chat_read_states_chat", "chat_uuid"),
        Index("idx_chat_read_states_user", "user_uuid"),
    )
