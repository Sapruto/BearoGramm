from src.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, func, Uuid, ForeignKey

from uuid import uuid4
from datetime import datetime

class UserSessionORM(Base):
    __tablename__ = "user_tokens"

    uuid: Mapped[str] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_uuid: Mapped[str] = mapped_column(Uuid, ForeignKey("users.uuid"), index=True)
    token_hash: Mapped[str] = mapped_column(String(255), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    device_name: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
