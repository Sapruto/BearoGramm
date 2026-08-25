import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

class MediaUtils:
    def __init__(self):
        self.mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.svg': 'image/svg+xml',
            '.bmp': 'image/bmp',
            '.ico': 'image/x-icon',
            '.mp4': 'video/mp4',
            '.avi': 'video/x-msvideo',
            '.mov': 'video/quicktime',
            '.mkv': 'video/x-matroska',
            '.webm': 'video/webm'
        }

    def generate_path(self, original_filename: str, chat_uuid: Optional[str] = None) -> str:
        ext = Path(original_filename).suffix.lower()
        if not ext:
            ext = '.bin'

        clean_name = ''.join(c for c in Path(original_filename).stem if c.isalnum() or c in '._-')
        if not clean_name:
            clean_name = 'file'

        file_uuid = uuid.uuid4().hex[:8]
        now = datetime.now()
        date_path = now.strftime("%Y/%m/%d")

        final_name = f"{file_uuid}_{clean_name}{ext}"

        if chat_uuid:
            return f"{chat_uuid}/{date_path}/{final_name}"

        return f"media/{date_path}/{final_name}"

    def get_content_type(self, filename: str) -> str:
        ext = Path(filename).suffix.lower()
        return self.mime_types.get(ext, 'application/octet-stream')

    def get_extension(self, filename: str) -> str:
        return Path(filename).suffix.lower()
