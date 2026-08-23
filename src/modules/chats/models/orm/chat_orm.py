from sqlalchemy import JSON, DateTime, func, Uuid, String, Index
from sqlalchemy.orm import Mapped, mapped_column
from src.core.database import Base
from uuid import uuid4
from datetime import datetime
from typing import List

from ...chat_types.base.base_access_type import definite_access_type

class ChatORM(Base):
    __tablename__ = "chats"

    uuid: Mapped[str] = mapped_column(Uuid, primary_key=True, default=uuid4)
    accesses: Mapped[List[definite_access_type]] = mapped_column(JSON)
    access_type: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now()
    )

    __table_args__ = (
        Index('idx_chats_access_type', 'access_type'),
        Index('idx_chats_accesses_gin', 'accesses', postgresql_using='gin'),
        Index('idx_chats_type_accesses', 'access_type', postgresql_ops={'accesses': 'jsonb_path_ops'}),
    )
