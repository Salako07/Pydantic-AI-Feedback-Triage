"""
Phase 2: Metrics API routes.
Endpoints for accessing AI agent performance metrics.
"""
from fastapi import APIRouter, Query
from typing import List
from ..metrics import compute_accuracy, compute_urgency_breakdown, compute_sentiment_trend
from ..schemas import AccuracyMetrics, UrgencyBreakdown, SentimentTrend

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/accuracy", response_model=AccuracyMetrics)
async def get_accuracy_metrics():
    """
    Get AI agent accuracy metrics.

    Returns overall accuracy and per-category accuracy.
    Accuracy = 1 - (overridden / processed)
    """
    return await compute_accuracy()


@router.get("/urgency-breakdown", response_model=UrgencyBreakdown)
async def get_urgency_breakdown():
    """
    Get breakdown of feedback by urgency level.

    Returns counts for low, medium, and high urgency feedback.
    """
    return await compute_urgency_breakdown()


@router.get("/sentiment-trend", response_model=List[SentimentTrend])
async def get_sentiment_trend(
    days: int = Query(default=7, ge=1, le=90, description="Number of days to look back")
):
    """
    Get daily sentiment trend for the last N days.

    Args:
        days: Number of days to look back (1-90, default 7)

    Returns list of daily sentiment counts (positive, neutral, negative).
    """
    return await compute_sentiment_trend(days=days)
