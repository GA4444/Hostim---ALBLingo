"""
AlbLingo - Albanian Language Learning Platform
Main FastAPI application with production-ready configuration.
"""
import os
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .config import settings
from .routers import (
    exercises, progress, seed, auth, ai, audio, 
    course_progression, database_viewer, leaderboard, 
    admin, ocr, gamification, chatbot, chatbot_advanced
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Creates database tables on startup.
    """
    # Startup: Initialize database tables
    init_db()
    print(f"[AlbLingo] Database initialized. Environment: {settings.ENVIRONMENT}")
    print(f"[AlbLingo] CORS origins: {settings.ALLOWED_ORIGINS}")
    yield
    # Shutdown: cleanup if needed
    print("[AlbLingo] Shutting down...")


def create_app() -> FastAPI:
    """
    Application factory for creating the FastAPI app.
    Uses environment-based configuration for production deployment.
    """
    app = FastAPI(
        title="AlbLingo - Albanian Language Learning Platform",
        version="1.0.0",
        description="API for the AlbLingo Albanian language learning platform",
        lifespan=lifespan,
    )

    # CORS Configuration - Uses environment variable ALLOWED_ORIGINS
    # In production, set ALLOWED_ORIGINS to your Vercel frontend URL
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # Register API Routers
    app.include_router(exercises.router, prefix="/api", tags=["exercises"])
    app.include_router(progress.router, prefix="/api", tags=["progress"])
    app.include_router(seed.router, prefix="/api", tags=["seed"])
    app.include_router(auth.router, prefix="/api", tags=["auth"])
    app.include_router(ai.router, prefix="/api", tags=["ai"])
    app.include_router(audio.router, prefix="/api", tags=["audio"])
    app.include_router(course_progression.router, prefix="/api", tags=["course-progression"])
    app.include_router(ocr.router, prefix="/api", tags=["ocr"])
    app.include_router(gamification.router, prefix="/api", tags=["gamification"])
    app.include_router(chatbot.router, prefix="/api", tags=["chatbot"])
    app.include_router(chatbot_advanced.router, prefix="/api", tags=["chatbot-advanced"])
    app.include_router(database_viewer.router, tags=["database-viewer"])
    app.include_router(leaderboard.router, prefix="/api", tags=["leaderboard"])
    app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

    return app


app = create_app()


# Root endpoint
@app.get("/")
def read_root():
    """Root endpoint - API welcome message."""
    return {
        "message": "Welcome to AlbLingo API",
        "status": "running",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }


# Health check endpoint
@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    Returns current status and timestamp.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "environment": settings.ENVIRONMENT,
        "database": "postgresql" if settings.is_postgres else "sqlite",
    }


