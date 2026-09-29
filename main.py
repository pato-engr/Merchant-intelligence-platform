from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.models import user as user_models
from app.services.bootstrap_users import (
    initialize_identity_store,
)

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.services.model_service import model_service
from app.models import geo as geo_models
from app.models import user as user_models


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    model_service.load()
    initialize_identity_store()
    
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered merchant lifecycle, risk and operational intelligence API.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(ValueError)
async def value_error_handler(_: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/", tags=["System"])
def root() -> dict[str, str]:
    return {
        "application": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
    }
