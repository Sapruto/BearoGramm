import pytest

from src.modules.messages.types.media.core.validator.media_validator import (
    MediaValidator,
    MediaValidatorConfig,
)


@pytest.mark.unit
class TestMediaValidator:
    def test_validate_success(self, media_validator):
        content = b"test content"
        filename = "test.jpg"
        is_valid, error = media_validator.validate(content, filename)
        assert is_valid is True
        assert error is None

    def test_validate_empty_file(self, media_validator):
        content = b""
        filename = "test.jpg"
        is_valid, error = media_validator.validate(content, filename)
        assert is_valid is False
        assert "empty" in error

    def test_validate_file_too_large(self, media_validator):
        content = b"a" * (50 * 1024 * 1024 + 1)
        filename = "test.jpg"
        is_valid, error = media_validator.validate(content, filename)
        assert is_valid is False
        assert "too large" in error

    def test_validate_invalid_extension(self, media_validator):
        content = b"test content"
        filename = "test.exe"
        is_valid, error = media_validator.validate(content, filename)
        assert is_valid is False
        assert "Extension" in error

    def test_validate_custom_max_size(self):
        config = MediaValidatorConfig(max_file_size=1024)
        validator = MediaValidator(config)
        content = b"a" * 1024
        is_valid, error = validator.validate(content, "test.jpg")
        assert is_valid is True

        content = b"a" * 1025
        is_valid, error = validator.validate(content, "test.jpg")
        assert is_valid is False

    def test_get_file_extension(self, media_validator):
        assert media_validator.get_file_extension("test.jpg") == ".jpg"
        assert media_validator.get_file_extension("test.JPG") == ".jpg"
        assert media_validator.get_file_extension("test") == ""

    def test_is_allowed_extension(self, media_validator):
        assert media_validator.is_allowed_extension("test.jpg") is True
        assert media_validator.is_allowed_extension("test.exe") is False

    def test_is_within_size_limit(self, media_validator):
        content = b"a" * 1000
        assert media_validator.is_within_size_limit(content) is True

        content = b"a" * (50 * 1024 * 1024 + 1)
        assert media_validator.is_within_size_limit(content) is False

    def test_get_allowed_extensions(self, media_validator):
        extensions = media_validator.get_allowed_extensions()
        assert ".jpg" in extensions
        assert ".png" in extensions
        assert ".mp4" in extensions

    def test_update_config(self, media_validator):
        media_validator.update_config(max_file_size=2048)
        assert media_validator.config.max_file_size == 2048
