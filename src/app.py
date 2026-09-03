from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from src.core.settings import Settings
from src.core.paths import STATIC_ROOT
from src.core.database import init_db, close_db
from src.core.logger import get_logger


logger = get_logger(__name__)


def include_all_routers(app: FastAPI) -> FastAPI:
    from src.modules.user import auth_router
    from src.modules.chats.chat_types.personal import personal_chats_router
    from src.modules.messages import message_router
    from src.modules.calls import calls_router

    app.include_router(auth_router)
    app.include_router(personal_chats_router)
    app.include_router(message_router)
    app.include_router(calls_router)

    return app


@asynccontextmanager
async def lifespan(app: FastAPI):
    if Settings.DATABASE.INIT_DB:
        logger.info("Initializing database...")
        await init_db()

    logger.info(f"Application started in {Settings.ENV} mode")
    logger.info(f"Debug mode: {Settings.APP.DEBUG}")

    yield

    logger.info("Shutting down application...")
    await close_db()


def create_app() -> FastAPI:
    app = FastAPI(
        title=Settings.APP.APP_NAME,
        version=Settings.APP.APP_VERSION,
        debug=Settings.APP.DEBUG,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=Settings.CORS.ALLOWED_ORIGINS,
        allow_credentials=Settings.CORS.ALLOW_CREDENTIALS,
        allow_methods=Settings.CORS.ALLOWED_METHODS,
        allow_headers=Settings.CORS.ALLOWED_HEADERS,
    )

    if STATIC_ROOT.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_ROOT)), name="static")

    app = include_all_routers(app)

    @app.get("/")
    async def index():
        return "67"

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.error(f"HTTP Exception: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail, "code": exc.status_code},
        )

    @app.middleware("http")
    async def log_errors(request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.critical(f"Unhandled exception: {e}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "detail": str(e) if Settings.APP.DEBUG else None
                }
            )

    return app
