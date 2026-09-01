import pytest
from pydantic import BaseModel

from src.general.repository.interfaces.query_interface import QueryInterface
from src.general.types_var import Fields


class MockFields:
    ID = "id"


class MockQuery(QueryInterface[MockFields]):
    pass


@pytest.mark.unit
class TestQueryInterface:
    def test_query_interface_is_pydantic_model(self):
        assert issubclass(QueryInterface, BaseModel)

    def test_query_interface_is_generic(self):
        query = MockQuery()
        assert isinstance(query, QueryInterface)

    def test_query_interface_instantiation(self):
        query = MockQuery()
        assert hasattr(query, "model_dump")
        assert hasattr(query, "model_dump_json")
