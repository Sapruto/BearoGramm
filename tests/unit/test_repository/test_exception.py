import pytest

from src.general.repository.exception import (
    NotConvertableError,
    NotConvertableField,
    NotConvertableValue
)


@pytest.mark.unit
class TestExceptions:
    def test_not_convertable_error_base(self):
        exc = NotConvertableError("Test error")
        assert str(exc) == "Test error"

    def test_not_convertable_field(self):
        field = "test_field"
        target = "int"
        exc = NotConvertableField(field, target)
        assert exc.field == field
        assert exc.target == target
        assert exc.reason is None
        assert "test_field" in str(exc)
        assert "int" in str(exc)

    def test_not_convertable_field_with_reason(self):
        field = "test_field"
        target = "int"
        reason = "Invalid format"
        exc = NotConvertableField(field, target, reason)
        assert exc.reason == reason
        assert reason in str(exc)

    def test_not_convertable_value(self):
        value = "abc"
        target = "int"
        exc = NotConvertableValue(value, target)
        assert exc.value == value
        assert exc.target == target
        assert exc.reason is None
        assert "abc" in str(exc)
        assert "str" in str(exc)

    def test_not_convertable_value_with_reason(self):
        value = "abc"
        target = "int"
        reason = "Not a number"
        exc = NotConvertableValue(value, target, reason)
        assert exc.reason == reason
        assert reason in str(exc)

    def test_not_convertable_field_inheritance(self):
        exc = NotConvertableField("field", "str")
        assert isinstance(exc, NotConvertableError)

    def test_not_convertable_value_inheritance(self):
        exc = NotConvertableValue("value", "str")
        assert isinstance(exc, NotConvertableError)
