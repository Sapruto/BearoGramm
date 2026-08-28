import pytest
from unittest.mock import AsyncMock, MagicMock

from src.modules.calls.core.clients.push_client_impl import PushClientImpl, DummyPushClientImpl, get_push_impl


@pytest.mark.unit
class TestPushClientImpl:
    def test_push_client_impl_is_abstract(self):
        with pytest.raises(TypeError):
            PushClientImpl()

    @pytest.mark.asyncio
    async def test_dummy_push_client_impl_send(self, caplog):
        client = DummyPushClientImpl()

        result = await client.send(
            phone_number="+79001234567",
            title="Test",
            body="Test body",
            data={"key": "value"}
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_dummy_push_client_impl_send_without_data(self):
        client = DummyPushClientImpl()

        result = await client.send(
            phone_number="+79001234567",
            title="Test",
            body="Test body"
        )

        assert result is True
