from pathlib import Path
from functools import lru_cache

PROJECT_ROOT = Path(__file__).parent.parent.parent
LOGS_ROOT = PROJECT_ROOT / "logs"
TEMPLATES_ROOT = PROJECT_ROOT / "frontend" / "templates"
ENV_PATH = PROJECT_ROOT / ".env"

DATABASE_ROOT = PROJECT_ROOT / "data" # for develop and test on sqlite3

def in_logs(subpath: str = "") -> Path:
    return LOGS_ROOT / subpath

def in_temp(subpath: str = "") -> Path:
    return TEMPLATES_ROOT / subpath

@lru_cache(maxsize=128)
def get_project_file(*parts) -> Path:
    return PROJECT_ROOT.joinpath(*parts)

LOGS_ROOT.mkdir(parents=True, exist_ok=True)
TEMPLATES_ROOT.mkdir(parents=True, exist_ok=True)
DATABASE_ROOT.mkdir(parents=True, exist_ok=True)
