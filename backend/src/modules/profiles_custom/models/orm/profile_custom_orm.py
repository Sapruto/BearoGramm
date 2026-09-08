from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON, Uuid, DateTime, String, ForeignKey, Index
from typing import List, Optional

from uuid import uuid4
from datetime import datetime

from src.core.database import Base
from src.general.processors.base.base_data import base_data_type


class ProfileCustomORM(Base):
    __tablename__ = "profile_custom"

    uuid: Mapped[str] = mapped_column(
        Uuid(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    data: Mapped[List[base_data_type]] = mapped_column(JSON)

    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
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
