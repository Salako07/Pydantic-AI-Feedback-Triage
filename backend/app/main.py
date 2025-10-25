import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .db import connect_to_mongo, close_mongo_connection
from .api.routes_feedback import router as feedback_router
from .api.routes_metrics import router as metrics_router  # Phase 2
from .api.routes_overrides import router as overrides_router  # Phase 2
from .jobs import start_scheduler, stop_scheduler  # Phase 2
from .utils import setup_logging
import logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting up application...")
    await connect_to_mongo()

    # Phase 2: Start background job scheduler
    try:
        start_scheduler()
        logger.info("Background scheduler started successfully")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")

    yield

    # Shutdown
    logger.info("Shutting down application...")

    # Phase 2: Stop scheduler
    try:
        stop_scheduler()
        logger.info("Background scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")

    await close_mongo_connection()


app = FastAPI(
    title="AI-Powered Customer Feedback Triage",
    description="Intelligent customer feedback analysis and triage system with Phase 2 enhancements",
    version="2.0.0",  # Phase 2
    lifespan=lifespan,
)

# CORS middleware - allow all origins for WebSocket compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=False,  # Must be False when using wildcard origins
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(feedback_router)
app.include_router(metrics_router)  # Phase 2
app.include_router(overrides_router)  # Phase 2


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "AI-Powered Customer Feedback Triage",
        "version": "2.0.0",  # Phase 2
        "phase": "Phase 2 - Production Ready"
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "llm_model": os.getenv("LLM_MODEL", "openai:gpt-4o"),
        "features": {
            "ai_analysis": True,
            "human_overrides": True,  # Phase 2
            "metrics": True,  # Phase 2
            "slack_alerts": bool(os.getenv("SLACK_WEBHOOK_URL")),  # Phase 2
            "weekly_jobs": True,  # Phase 2
        }
    }
