from src.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, func, Uuid

from typing import List
from uuid import uuid4
from datetime import datetime


class UserORM(Base):
    __tablename__ = "users"

    uuid: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )

    phone_number_encrypted: Mapped[str] = mapped_column(String(512), nullable=True)
    phone_number_hash: Mapped[str] = mapped_column(
        String(64), nullable=True, index=True
    )
    phone_number_mask: Mapped[str] = mapped_column(String(20), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )

    messages: Mapped[List["MessageORM"]] = relationship(
        "MessageORM",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
        foreign_keys="MessageORM.user_uuid"
    )
