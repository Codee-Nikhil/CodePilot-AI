"""FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, chat, dashboard, github, health, readme, repositories, reviews, settings, users
from app.api.error_handlers import register_exception_handlers
from app.core.config import get_settings
from app.services.indexing_service import recover_interrupted_jobs

app_settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    recover_interrupted_jobs()
    yield


app = FastAPI(title=app_settings.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[app_settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_exception_handlers(app)

for router in (health, auth, users, github, repositories, chat, reviews, readme, dashboard, settings):
    app.include_router(router.router, prefix="/api")
