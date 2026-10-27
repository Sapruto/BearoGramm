from datetime import datetime, timezone
from sqlalchemy import event, Connection
from sqlalchemy.orm import Mapper

from src.modules.chats.models.orm.chat_orm import ChatORM
from src.modules.messages.models.orm.message_orm import MessageORM


@event.listens_for(MessageORM, "after_insert")
def _touch_chat_on_message_insert(
    _mapper: Mapper[MessageORM],
    connection: Connection,
    target: MessageORM,
) -> None:
    chat_table = ChatORM.__table__
    connection.execute(
        chat_table.update()
        .where(chat_table.c.uuid == target.chat_uuid)
        .values(last_message_at=datetime.now(timezone.utc))
    )
