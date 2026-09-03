import pytest
from pathlib import Path

from src.modules.messages.types.media.core.utils.media_utils import MediaUtils


@pytest.mark.unit
class TestMediaUtils:
    def test_generate_path_with_chat_uuid(self, media_utils):
        filename = "test.jpg"
        chat_uuid = "chat123"
        path = media_utils.generate_path(filename, chat_uuid)

        assert chat_uuid in path
        assert "test.jpg" in path or "test" in path
        assert path.endswith(".jpg")

    def test_generate_path_without_chat_uuid(self, media_utils):
        filename = "test.jpg"
        path = media_utils.generate_path(filename)

        assert "media/" in path
        assert "test.jpg" in path or "test" in path
        assert path.endswith(".jpg")

    def test_generate_path_without_extension(self, media_utils):
        filename = "testfile"
        path = media_utils.generate_path(filename)

        assert path.endswith(".bin")

    def test_generate_path_with_special_chars(self, media_utils):
        filename = "test!@#$%^&*.jpg"
        path = media_utils.generate_path(filename)

        assert path.endswith(".jpg")
        assert "test" in path

    def test_get_content_type_image(self, media_utils):
        assert media_utils.get_content_type("test.jpg") == "image/jpeg"
        assert media_utils.get_content_type("test.png") == "image/png"
        assert media_utils.get_content_type("test.gif") == "image/gif"
        assert media_utils.get_content_type("test.webp") == "image/webp"

    def test_get_content_type_video(self, media_utils):
        assert media_utils.get_content_type("test.mp4") == "video/mp4"
        assert media_utils.get_content_type("test.avi") == "video/x-msvideo"
        assert media_utils.get_content_type("test.mov") == "video/quicktime"
        assert media_utils.get_content_type("test.webm") == "video/webm"

    def test_get_content_type_unknown(self, media_utils):
        assert media_utils.get_content_type("test.xyz") == "application/octet-stream"

    def test_get_extension(self, media_utils):
        assert media_utils.get_extension("test.jpg") == ".jpg"
        assert media_utils.get_extension("test.JPG") == ".jpg"
        assert media_utils.get_extension("test") == ""
