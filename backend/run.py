from urllib.parse import urlparse
from src.app import create_app
from src.core.settings import Settings
import uvicorn

app = create_app()

if __name__ == "__main__":
    parsed = urlparse(Settings.BASE_URL)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 8000

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=Settings.APP.DEBUG,
        log_level=Settings.APP.LOG_LEVEL.lower(),
    )
