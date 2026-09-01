import pytest
from datetime import datetime
from src.modules.chats.models.orm.chat_orm import ChatORM


@pytest.mark.unit
class TestChatORM:
    def test_chat_orm_table_name(self):
        assert ChatORM.__tablename__ == "chats"
