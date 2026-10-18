from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, DateTime, String, ForeignKey, Index, Enum
from typing import Optional

from uuid import uuid4
from datetime import datetime

from src.core.database import Base

from .default_avatar_randomizer import AvatarRandomizer
from ..enums import Gender


randomizer = AvatarRandomizer()


class ProfileCustomORM(Base):
    __tablename__ = "profile_custom"

    uuid: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    name: Mapped[str] = mapped_column(String(67), nullable=False, default="Unnamed")
    avatar_url: Mapped[str] = mapped_column(String(555), nullable=False, default=lambda: str(randomizer.get_random_avatar()))

    banner_color: Mapped[str] = mapped_column(String(7), nullable=False, default="#000000")
    gender: Mapped[Gender] = mapped_column(
        Enum(
            Gender,
            name="gender",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        default=Gender.BEAR,
    )
    bio: Mapped[str] = mapped_column(Text, nullable=False, default="I am ameba")

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    user_uuid: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.uuid", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    user: Mapped[Optional["UserORM"]] = relationship(
        "UserORM",
        back_populates="profile_customs",
        lazy="selectin",
        foreign_keys=[user_uuid]
    )

    __table_args__ = (
        Index("idx_profile_custom_user_uuid", "user_uuid"),
        Index("idx_profile_custom_updated_at", "updated_at"),
    )
