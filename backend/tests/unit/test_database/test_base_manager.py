import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession

from src.general.db.base_manager import (
    BaseManager,
    OnConflictAction,
    ObjectAlreadyExistsError,
    InvalidTransactionStateError,
)

Base = declarative_base()


class TestModel(Base):
    __tablename__ = "test_model"
    id = Column(String, primary_key=True)
    name = Column(String)
    age = Column(Integer)


class TestManager(BaseManager[TestModel]):
    def __init__(self, immutable_fields: list = None):
        super().__init__(TestModel, immutable_fields)

    @property
    def identifier_field(self):
        return TestModel.id


@pytest.fixture
def mock_session():
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def manager():
    return TestManager()


@pytest.mark.unit
class TestBaseManager:
    def test_init(self):
        manager = TestManager()
        assert manager.model == TestModel
        assert TestModel.id in manager.immutable_fields

    def test_init_with_immutable_fields(self):
        manager = TestManager(immutable_fields=["email"])
        assert "email" in manager.immutable_fields
        assert TestModel.id in manager.immutable_fields

    @pytest.mark.asyncio
    async def test_get_by_field(self, manager, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = TestModel(id="1", name="test")
        mock_session.execute.return_value = mock_result

        result = await manager.get_by_field("1", TestModel.id, session=mock_session)

        assert result is not None
        assert result.id == "1"
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_field_not_found(self, manager, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await manager.get_by_field("999", TestModel.id, session=mock_session)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_all(self, manager, mock_session):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            TestModel(id="1", name="test1"),
            TestModel(id="2", name="test2"),
        ]
        mock_session.execute.return_value = mock_result

        result = await manager.get_all(session=mock_session)

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_count(self, manager, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 5
        mock_session.execute.return_value = mock_result

        result = await manager.count(session=mock_session)

        assert result == 5

    @pytest.mark.asyncio
    async def test_create_success(self, manager, mock_session):
        orm = TestModel(id="1", name="test")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await manager.create(orm, session=mock_session, commit=True)

        assert result == orm
        mock_session.add.assert_called_once_with(orm)
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_without_commit_and_session(self, manager):
        orm = TestModel(id="1", name="test")

        with pytest.raises(InvalidTransactionStateError):
            await manager.create(orm, commit=False, session=None)

    @pytest.mark.asyncio
    async def test_create_on_conflict_nothing(self, manager, mock_session):
        orm = TestModel(id="1", name="test")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = TestModel(id="1")
        mock_session.execute.return_value = mock_result

        with pytest.raises(ObjectAlreadyExistsError):
            await manager.create(
                orm, on_conflict=OnConflictAction.NOTHING, session=mock_session
            )

    @pytest.mark.asyncio
    async def test_create_without_orm(self, manager):
        with pytest.raises(ValueError):
            await manager.create(None)

    @pytest.mark.asyncio
    async def test_update_by_identifier(self, manager, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = TestModel(id="1", name="updated")
        mock_session.execute.return_value = mock_result

        result = await manager.update(
            identifier="1",
            field_identifier=TestModel.id,
            session=mock_session,
            commit=True,
            name="updated",
        )

        assert result is not None
        assert result.name == "updated"
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_by_where(self, manager, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = TestModel(id="1", name="updated")
        mock_session.execute.return_value = mock_result

        result = await manager.update(
            where={TestModel.id: "1"}, session=mock_session, commit=True, name="updated"
        )

        assert result is not None
        assert result.name == "updated"

    @pytest.mark.asyncio
    async def test_delete(self, manager, mock_session):
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result

        result = await manager.delete(where={TestModel.id: "1"}, session=mock_session)

        assert result == 1
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_exists_true(self, manager, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = "1"
        mock_session.execute.return_value = mock_result

        result = await manager.exists("1", TestModel.id, session=mock_session)

        assert result is True

    @pytest.mark.asyncio
    async def test_exists_false(self, manager, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await manager.exists("999", TestModel.id, session=mock_session)

        assert result is False

    @pytest.mark.asyncio
    async def test_update_no_params(self, manager):
        with pytest.raises(ValueError):
            await manager.update()

    @pytest.mark.asyncio
    async def test_update_both_where_and_identifier(self, manager):
        with pytest.raises(ValueError):
            await manager.update(
                identifier="1", field_identifier=TestModel.id, where={TestModel.id: "1"}
            )

    @pytest.mark.asyncio
    async def test_update_no_data(self, manager):
        with pytest.raises(ValueError):
            await manager.update(identifier="1", field_identifier=TestModel.id)

    @pytest.mark.asyncio
    async def test_delete_no_where(self, manager):
        with pytest.raises(ValueError):
            await manager.delete(where=None)
