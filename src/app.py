from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv
import logging

from src.core.database import init_db, close_db

load_dotenv()

def include_all_routers(app: FastAPI) -> FastAPI:
    from src.modules.user import auth_router
    from src.modules.chats.chat_types.personal import personal_chats_router

    app.include_router(auth_router)
    app.include_router(personal_chats_router)

    return app

@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.getenv("INIT_DB", False) == "True":
        await init_db()

    yield
    await close_db()

def create_app() -> FastAPI:
    BASE_DIR = Path(__file__).parent.parent
    STATIC_DIR = BASE_DIR / 'frontend' / 'static'
    app = FastAPI(lifespan=lifespan)

    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    app = include_all_routers(app)

    @app.get("/")
    async def index():
        return "67"

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={'error': exc.detail, 'code': exc.status_code}
        )

    @app.middleware("http")
    async def log_errors(request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            logging.critical(f"Unhandled: {e}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={'error': 'Internal Server Error'}
            )

    return app
