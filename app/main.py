import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_db
from app.core.logging import setup_logging, get_logger
from app.api.auth import router as auth_router
from app.api.chat import router as chat_router

setup_logging(log_level=settings.LOG_LEVEL)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    await init_db()
    logger.info("Database initialized successfully")
    yield
    logger.info(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(chat_router, prefix="/api")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response: {request.method} {request.url.path} - Status: {response.status_code}")
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "Internal Server Error", "data": None}
    )


@app.get("/", tags=["根路径"])
async def root():
    logger.debug("Root endpoint called")
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "message": "Welcome to Shezhen AI Backend"
    }


@app.get("/health", tags=["健康检查"])
async def health_check():
    return {"status": "healthy"}
