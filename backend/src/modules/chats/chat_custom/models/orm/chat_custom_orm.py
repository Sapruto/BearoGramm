from sqlalchemy import String, ForeignKey, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime, timezone
from uuid import uuid4

from src.core.database import Base


class ChatCustomORM(Base):
    __tablename__ = "chat_reading"

    uuid: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )

    name: Mapped[str] = mapped_column(String(67), nullable=False, default="")
    avatar_uuid: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("media.uuid", ondelete="SET NULL"),
        nullable=True,
    )
    banner_color: Mapped[str] = mapped_column(String(7), nullable=False, default="#000000")

    chat_uuid: Mapped[str] = mapped_column(
        String(36), ForeignKey("chats.uuid", ondelete="CASCADE"), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc),
    )

    chat: Mapped["ChatORM"] = relationship("ChatORM", back_populates="read_states")

    __table_args__ = (
        UniqueConstraint("chat_uuid", "user_uuid", name="uq_chat_read_state_user"),
        Index("idx_chat_read_states_chat", "chat_uuid"),
        Index("idx_chat_read_states_user", "user_uuid"),
    )
