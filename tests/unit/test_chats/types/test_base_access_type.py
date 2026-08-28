import pytest
from abc import ABC
from pydantic import BaseModel

from src.modules.chats.chat_types.base.base_access_type import BaseAccessType, definite_access_type
from src.modules.chats.chat_types.base.base_access_threshold import BaseAccessThreshold


class MockThreshold(BaseAccessThreshold):
    pass


class MockAccessType(BaseAccessType[MockThreshold]):
    def get_threshold(self):
        return MockThreshold()

    def get_raw_data(self):
        return {"user_uuid": self.user_uuid}

    def get_type(self):
        return "mock"


@pytest.mark.unit
class TestBaseAccessType:
    def test_base_access_type_is_abstract(self):
        assert issubclass(BaseAccessType, ABC)
        assert issubclass(BaseAccessType, BaseModel)

    def test_base_access_type_creation(self):
        access = MockAccessType(user_uuid="test_uuid")
        assert access.user_uuid == "test_uuid"

    def test_base_access_type_requires_abstract_methods(self):
        with pytest.raises(TypeError):
            class InvalidAccessType(BaseAccessType):
                pass

            InvalidAccessType(user_uuid="test")

    def test_base_access_type_abstract_methods_implemented(self):
        access = MockAccessType(user_uuid="test_uuid")
        assert hasattr(access, 'get_threshold')
        assert hasattr(access, 'get_raw_data')
        assert hasattr(access, 'get_type')

    def test_get_threshold_returns_correct_type(self):
        access = MockAccessType(user_uuid="test_uuid")
        threshold = access.get_threshold()
        assert isinstance(threshold, MockThreshold)

    def test_get_raw_data_returns_dict(self):
        access = MockAccessType(user_uuid="test_uuid")
        raw_data = access.get_raw_data()
        assert isinstance(raw_data, dict)
        assert raw_data["user_uuid"] == "test_uuid"

    def test_get_type_returns_string(self):
        access = MockAccessType(user_uuid="test_uuid")
        assert isinstance(access.get_type(), str)
        assert access.get_type() == "mock"

    def test_definite_access_type_defined(self):
        assert definite_access_type is not None

    def test_base_access_type_inheritance(self):
        class CustomAccessType(BaseAccessType[MockThreshold]):
            def get_threshold(self):
                return MockThreshold()

            def get_raw_data(self):
                return {"user_uuid": self.user_uuid, "custom": "data"}

            def get_type(self):
                return "custom"

        access = CustomAccessType(user_uuid="test")
        assert access.get_type() == "custom"
        assert access.get_raw_data()["custom"] == "data"
