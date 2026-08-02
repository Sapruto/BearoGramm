from src.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, func, Boolean, Uuid

from uuid import uuid4
from datetime import datetime

class UserORM(Base):
    __tablename__ = "users"

    uuid: Mapped[str] = mapped_column(Uuid, primary_key=True, default=uuid4)

    phone_number_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_number_salt: Mapped[str] = mapped_column(String(64), nullable=False)

    phone_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        onupdate=func.now()
    )
