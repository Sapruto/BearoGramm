import pytest
from conftest import MockEntity, MockORM, MockFields


@pytest.mark.unit
class TestBaseRepository:
    @pytest.mark.asyncio
    async def test_save(self, sql_repository, manager):
        entity = MockEntity(id="1", name="test")
        manager.create.return_value = MockORM(id="1", name="test")
        result = await sql_repository.save(entity)
        assert result.id == "1"
        assert result.name == "test"
        manager.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_exception(self, sql_repository, manager):
        manager.create.side_effect = Exception("DB error")
        entity = MockEntity(id="1", name="test")
        with pytest.raises(Exception):
            await sql_repository.save(entity)

    @pytest.mark.asyncio
    async def test_get_by_field(self, sql_repository, manager):
        manager.get_by_field.return_value = MockORM(id="1", name="test")
        result = await sql_repository.get_by_field("1", MockFields.ID)
        assert result.id == "1"
        manager.get_by_field.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_field_not_found(self, sql_repository, manager):
        manager.get_by_field.return_value = None
        result = await sql_repository.get_by_field("999", MockFields.ID)
        assert result is None

    @pytest.mark.asyncio
    async def test_delete(self, sql_repository, manager):
        manager.delete.return_value = 1
        from src.general.repository.sql.sql_query import SqlQuery
        query = SqlQuery[MockFields]()
        query.add_filter(MockFields.ID, "1")
        result = await sql_repository.delete(query)
        assert result == 1
        manager.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_get(self, sql_repository, manager):
        manager.get_all.return_value = [MockORM(id="1", name="test")]
        from src.general.repository.sql.sql_query import SqlQuery
        query = SqlQuery[MockFields]()
        query.add_filter(MockFields.ID, "1")
        result = await sql_repository.get(query)
        assert result.id == "1"
        manager.get_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all(self, sql_repository, manager):
        manager.get_all.return_value = [
            MockORM(id="1", name="test1"),
            MockORM(id="2", name="test2")
        ]
        from src.general.repository.sql.sql_query import SqlQuery
        query = SqlQuery[MockFields]()
        result = await sql_repository.get_all(query)
        assert len(result) == 2
        manager.get_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_count(self, sql_repository, manager):
        manager.count.return_value = 5
        from src.general.repository.sql.sql_query import SqlQuery
        query = SqlQuery[MockFields]()
        result = await sql_repository.count(query)
        assert result == 5
        manager.count.assert_called_once()
