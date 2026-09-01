import pytest
from abc import ABC
from pydantic import BaseModel

from src.modules.chats.chat_types.base.base_access_threshold import BaseAccessThreshold


class MockThreshold(BaseAccessThreshold):
    custom_field: str = "test"


class AnotherThreshold(BaseAccessThreshold):
    value: int = 0


@pytest.mark.unit
class TestBaseAccessThreshold:
    def test_base_access_threshold_is_abstract(self):
        assert issubclass(BaseAccessThreshold, ABC)
        assert issubclass(BaseAccessThreshold, BaseModel)

    def test_base_access_threshold_instantiation(self):
        threshold = BaseAccessThreshold()
        assert isinstance(threshold, BaseAccessThreshold)
        assert isinstance(threshold, BaseModel)

    def test_mock_threshold_inheritance(self):
        threshold = MockThreshold()
        assert isinstance(threshold, BaseAccessThreshold)
        assert threshold.custom_field == "test"

    def test_another_threshold_inheritance(self):
        threshold = AnotherThreshold()
        assert isinstance(threshold, BaseAccessThreshold)
        assert threshold.value == 0

    def test_base_access_threshold_with_fields(self):
        threshold = BaseAccessThreshold()
        assert hasattr(threshold, "model_dump")
        assert hasattr(threshold, "model_dump_json")

    def test_threshold_serialization(self):
        threshold = MockThreshold(custom_field="hello")
        data = threshold.model_dump()
        assert data["custom_field"] == "hello"

    def test_threshold_deserialization(self):
        threshold = MockThreshold.model_validate({"custom_field": "world"})
        assert threshold.custom_field == "world"
