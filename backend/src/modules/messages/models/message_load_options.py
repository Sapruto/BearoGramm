from dataclasses import dataclass
from sqlalchemy.orm import selectinload

from .orm.message_orm import MessageORM


@dataclass
class MessageLoadOptions:
    extra: bool = False
    references: bool = False
    user: bool = False
    chat: bool = False

    def loader_options(self) -> list:
        opts = []
        if self.extra:
            opts.append(selectinload(MessageORM.extra_data))
        if self.references:
            opts.append(selectinload(MessageORM.references))
        if self.user:
            opts.append(selectinload(MessageORM.user))
        if self.chat:
            opts.append(selectinload(MessageORM.chat))
        return opts

    @classmethod
    def none(cls) -> "MessageLoadOptions":
        return cls()

    @classmethod
    def full(cls) -> "MessageLoadOptions":
        return cls(extra=True, references=True, user=True)
