from random import choice
from pathlib import Path
from src.core.paths import STATIC_ROOT


MEDIA_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff']


class AvatarRandomizer:
    def __init__(self):
        self.current_dir = STATIC_ROOT / "default_avatars"
        
        self.avatars = [
            f for f in self.current_dir.iterdir() 
            if f.is_file() and f.suffix.lower() in MEDIA_EXTENSIONS
        ]

    def get_random_avatar(self) -> str:
        if not self.avatars:
            return None
            
        random_file = choice(self.avatars)
        
        return f"media/default_avatars/{random_file.name}"
