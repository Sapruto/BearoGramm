from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Enum,  Integer, JSON

from ..enums.extra_data_type import ExtraDataType

from src.core.database import Base


class MessageDataORM(Base):
    __tablename__ = "message_data"

    message_uuid: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("messages.uuid", ondelete="CASCADE"),
        primary_key=True,
    )

    extra_data_type: Mapped[ExtraDataType] = mapped_column(
        Enum(
            ExtraDataType,
            name="extra_data_type",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        index=True,
    )

    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    message: Mapped["MessageORM"] = relationship(
        "MessageORM",
        back_populates="extra_data",
        lazy="raise",
    )
