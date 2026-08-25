from pathlib import Path
from typing import Optional, Set, Tuple
from pydantic import BaseModel, Field

class MediaValidatorConfig(BaseModel):
    max_file_size: int = Field(
        default=50 * 1024 * 1024,
        gt=0
    )

    allowed_extensions: Set[str] = Field(
        default={
            '.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp', '.ico',
            '.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.m4v'
        }
    )

    allowed_mime_types: Optional[Set[str]] = Field(default=None)

class MediaValidator:
    def __init__(self, config: Optional[MediaValidatorConfig] = None):
        self.config = config or MediaValidatorConfig()

    def validate(self, content: bytes, filename: str) -> Tuple[bool, Optional[str]]:
        if len(content) == 0:
            return False, "File is empty"

        if len(content) > self.config.max_file_size:
            size_mb = self.config.max_file_size // (1024 * 1024)
            return False, f"File too large. Maximum size: {size_mb}MB"

        ext = Path(filename).suffix.lower()
        if ext not in self.config.allowed_extensions:
            allowed = ', '.join(sorted(self.config.allowed_extensions))
            return False, f"Extension '{ext}' not allowed. Allowed: {allowed}"

        return True, None

    def get_file_extension(self, filename: str) -> str:
        return Path(filename).suffix.lower()

    def is_allowed_extension(self, filename: str) -> bool:
        return self.get_file_extension(filename) in self.config.allowed_extensions

    def is_within_size_limit(self, content: bytes) -> bool:
        return len(content) <= self.config.max_file_size

    def get_allowed_extensions(self) -> Set[str]:
        return self.config.allowed_extensions

    def update_config(self, **kwargs) -> None:
        new_config = self.config.model_copy(update=kwargs)
        self.config = new_config

def get_default_media_validator() -> MediaValidator:
    return MediaValidator()
