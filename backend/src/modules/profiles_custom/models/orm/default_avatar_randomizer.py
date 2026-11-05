from random import choice
from pathlib import Path
from typing import Optional

from src.core.logger import get_logger
from src.core.paths import STATIC_ROOT
from src.modules.media.core.services.media_service import MediaService, get_media_service

logger = get_logger(__name__)

MEDIA_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}


class AvatarRandomizer:
    def __init__(
        self,
        media_service: Optional[MediaService] = None,
        avatars_dir: Optional[Path] = None,
    ):
        self._media_service = media_service or get_media_service()
        self.avatars_dir = avatars_dir or (STATIC_ROOT / "default_avatars")
        self._files = [
            f for f in self.avatars_dir.iterdir()
            if f.is_file() and f.suffix.lower() in MEDIA_EXTENSIONS
        ]
        self._avatar_uuids: list[str] = []

    async def preload(self) -> None:
        uuids: list[str] = []
        for file in self._files:
            relative_path = Path("default_avatars") / file.name
            media_uuid = await self._media_service.get_or_create_server_file(
                storage_path=relative_path,
                file_name=file.name,
            )
            if media_uuid:
                uuids.append(media_uuid)
            else:
                logger.warning(f"Failed to register default avatar: {file}")

        self._avatar_uuids = uuids
        logger.info(f"AvatarRandomizer preloaded {len(uuids)}/{len(self._files)} avatars")

    def pick_random_file(self) -> Optional[str]:
        if not self._files:
            return None
        return choice(self._files).name

    def get_random_avatar(self) -> Optional[str]:
        if not self._avatar_uuids:
            return None
        return choice(self._avatar_uuids)


_avatar_randomizer: Optional[AvatarRandomizer] = None


def get_avatar_randomizer() -> AvatarRandomizer:
    global _avatar_randomizer
    if _avatar_randomizer is None:
        _avatar_randomizer = AvatarRandomizer()
    return _avatar_randomizer


def set_avatar_randomizer(randomizer: AvatarRandomizer) -> None:
    global _avatar_randomizer
    _avatar_randomizer = randomizer


async def setup_avatar_randomizer() -> None:
    randomizer = AvatarRandomizer()
    await randomizer.preload()
    set_avatar_randomizer(randomizer)
