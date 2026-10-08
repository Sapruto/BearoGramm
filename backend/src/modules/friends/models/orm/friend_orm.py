from src.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, func, ForeignKey, Enum

from uuid import uuid4
from datetime import datetime

from ..enums import FriendStatus


class FriendORM(Base):
    __tablename__ = "friends"

    uuid: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )

    user_uuid1: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.uuid", ondelete="CASCADE"), nullable=False
    )
    user_status1: Mapped[FriendStatus] = mapped_column(
        Enum(
            FriendStatus,
            name="friend_status",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        default=FriendStatus.PROCESS,
    )

    user_uuid2: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.uuid", ondelete="CASCADE"), nullable=False
    )
    user_status2: Mapped[FriendStatus] = mapped_column(
        Enum(
            FriendStatus,
            name="friend_status",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        default=FriendStatus.PROCESS,
    )

    initiator_uuid: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.uuid", ondelete="CASCADE"), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
