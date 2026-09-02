import pytest
from datetime import datetime
from uuid import uuid4

from src.modules.chats.chat_types.personal.personal_models.personal_access_threshold import (
    PersonalAccessThreshold,
)
from src.modules.chats.chat_types.base.base_access_threshold import BaseAccessThreshold


@pytest.mark.unit
class TestPersonalAccessThreshold:
    def test_personal_access_threshold_inheritance(self):
        threshold = PersonalAccessThreshold()
        assert isinstance(threshold, BaseAccessThreshold)

    def test_personal_access_threshold_creation(self):
        threshold = PersonalAccessThreshold(is_blocked=False, unread_count=0)
        assert threshold.is_blocked is False
        assert threshold.unread_count == 0
        assert threshold.blocked_at is None
        assert threshold.blocked_by is None
        assert threshold.last_message_at is None

    def test_personal_access_threshold_with_all_fields(self):
        now = datetime.now()
        blocked_by = str(uuid4())

        threshold = PersonalAccessThreshold(
            is_blocked=True,
            blocked_at=now,
            blocked_by=blocked_by,
            last_message_at=now,
            unread_count=5,
        )

        assert threshold.is_blocked is True
        assert threshold.blocked_at == now
        assert threshold.blocked_by == blocked_by
        assert threshold.last_message_at == now
        assert threshold.unread_count == 5

    def test_personal_access_threshold_defaults(self):
        threshold = PersonalAccessThreshold()
        assert threshold.is_blocked is False
        assert threshold.unread_count == 0
        assert threshold.blocked_at is None
        assert threshold.blocked_by is None
        assert threshold.last_message_at is None

    def test_block_method(self):
        threshold = PersonalAccessThreshold()
        blocker = str(uuid4())
        before = datetime.now()
        threshold.block(blocker)
        after = datetime.now()

        assert threshold.is_blocked is True
        assert threshold.blocked_by == blocker
        assert threshold.blocked_at is not None
        assert before <= threshold.blocked_at <= after

    def test_unblock_method(self):
        threshold = PersonalAccessThreshold()
        threshold.is_blocked = True
        threshold.blocked_at = datetime.now()
        threshold.blocked_by = str(uuid4())

        threshold.unblock()

        assert threshold.is_blocked is False
        assert threshold.blocked_at is None
        assert threshold.blocked_by is None

    def test_block_unblock_cycle(self):
        threshold = PersonalAccessThreshold()
        blocker = str(uuid4())

        threshold.block(blocker)
        assert threshold.is_blocked is True

        threshold.unblock()
        assert threshold.is_blocked is False

        threshold.block(blocker)
        assert threshold.is_blocked is True

    def test_block_method_updates_blocked_at(self):
        import time

        threshold = PersonalAccessThreshold()
        blocker = str(uuid4())

        threshold.block(blocker)
        first_blocked_at = threshold.blocked_at

        time.sleep(0.001)

        threshold.unblock()
        threshold.block(blocker)

        assert threshold.blocked_at > first_blocked_at
