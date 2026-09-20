import uuid
from pathlib import Path
from typing import Optional
from pathlib import PurePosixPath
import mimetypes


class MediaUtils:
    def __init__(self):
        self.mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".svg": "image/svg+xml",
            ".bmp": "image/bmp",
            ".ico": "image/x-icon",
            ".heic": "image/heic",
            ".avif": "image/avif",

            ".mp4": "video/mp4",
            ".avi": "video/x-msvideo",
            ".mov": "video/quicktime",
            ".mkv": "video/x-matroska",
            ".webm": "video/webm",
            ".flv": "video/x-flv",
            ".m4v": "video/x-m4v",

            ".mp3": "audio/mpeg",
            ".ogg": "audio/ogg",
            ".oga": "audio/ogg",
            ".opus": "audio/opus",
            ".wav": "audio/wav",
            ".flac": "audio/flac",
            ".aac": "audio/aac",
            ".m4a": "audio/mp4",
            ".wma": "audio/x-ms-wma",

            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".xls": "application/vnd.ms-excel",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".ppt": "application/vnd.ms-powerpoint",
            ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            ".txt": "text/plain",
            ".csv": "text/csv",
            ".json": "application/json",
            ".xml": "application/xml",
            ".md": "text/markdown",
            ".rtf": "application/rtf",
            ".odt": "application/vnd.oasis.opendocument.text",

            ".zip": "application/zip",
            ".rar": "application/vnd.rar",
            ".7z": "application/x-7z-compressed",
            ".tar": "application/x-tar",
            ".gz": "application/gzip",

            ".tgs": "application/x-tgsticker",
        }

    def _safe_ext(self, filename: str) -> str:
        ext = PurePosixPath(filename).suffix.lower()
        if ext and len(ext) <= 6 and ext.isascii() and ext[1:].isalnum():
            return ext
        guessed, _ = mimetypes.guess_extension(
            mimetypes.guess_type(filename)[0] or ""
        )
        return guessed or ""

    def generate_path(
        self,
        original_filename: str,
        owner_type: Optional[str] = None,
        owner_uuid: Optional[str] = None,
        enclosure: Optional[str] = None,
    ) -> str:
        ext = self._safe_ext(original_filename)
        file_uuid = uuid.uuid4().hex
        name = f"{file_uuid}{ext}"

        parts = ["media"]
        if enclosure:
            parts.append(enclosure)
        if owner_type and owner_uuid:
            parts += [owner_type, owner_uuid]
        parts.append(name)

        return "/".join(parts)

    def get_content_type(self, filename: str) -> str:
        ext = Path(filename).suffix.lower()
        return self.mime_types.get(ext, "application/octet-stream")

    def get_extension(self, filename: str) -> str:
        return Path(filename).suffix.lower()
