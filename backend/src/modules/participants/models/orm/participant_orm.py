from sqlalchemy import ForeignKey, Uuid, Enum, JSON, Index, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from src.core.database import Base
from uuid import uuid4
from datetime import datetime
from typing import Dict

from ...models.enums import ResourceType

class ParticipantORM(Base):
    __tablename__ = "participants"

    uuid: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )

    user_uuid: Mapped[str] = mapped_column(
        Uuid(as_uuid=False),
        ForeignKey("users.uuid", ondelete="CASCADE"),
        nullable=False,
    )

    resource_uuid: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), nullable=False
    )

    resource_type: Mapped[ResourceType] = mapped_column(
        Enum(ResourceType), nullable=False
    )

    permissions: Mapped[Dict[str, bool]] = mapped_column(
        JSON,
        nullable=False,
        default=dict
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    __table_args__ = (
        Index(
            "idx_participant_unique",
            "user_uuid",
            "resource_uuid",
            "resource_type",
            unique=True
        ),
        Index(
            "idx_participant_permissions",
            "permissions",
            postgresql_using="gin"
        ),
        Index(
            "idx_participant_user_resource_type",
            "user_uuid",
            "resource_type",
            "resource_uuid"
        ),
        Index(
            "idx_participant_resource_type_uuid",
            "resource_type",
            "resource_uuid"
        ),
        Index(
            "idx_participant_user_resource",
            "user_uuid",
            "resource_uuid"
        ),
        Index(
            "idx_participant_created_at",
            "created_at"
        ),
    )
