"""
Phase 2: Metrics computation functions.
Compute accuracy, urgency breakdown, sentiment trends from feedback data.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List
from .db import get_feedbacks_collection
from .schemas import AccuracyMetrics, UrgencyBreakdown, SentimentTrend

logger = logging.getLogger(__name__)


async def compute_accuracy() -> AccuracyMetrics:
    """
    Compute AI agent accuracy metrics.

    Accuracy = 1 - (overridden_count / processed_count)
    Overall and per-category accuracy.

    Returns:
        AccuracyMetrics with overall and category-specific accuracy
    """
    collection = get_feedbacks_collection()

    # Get all feedbacks that were processed by AI (agent_success is not None)
    processed = await collection.count_documents({"agent_success": {"$ne": None}})

    # Get feedbacks that have been overridden (overrides array is not empty)
    overridden = await collection.count_documents({
        "agent_success": {"$ne": None},
        "overrides": {"$exists": True, "$ne": []}
    })

    overall_accuracy = 1.0 if processed == 0 else (1.0 - (overridden / processed))

    # Compute per-category accuracy
    by_category: Dict[str, float] = {}

    # Get all unique categories
    categories_cursor = collection.distinct("analysis.category", {"agent_success": {"$ne": None}})
    categories = await categories_cursor

    for category in categories:
        if not category:
            continue

        cat_processed = await collection.count_documents({
            "agent_success": {"$ne": None},
            "analysis.category": category
        })

        cat_overridden = await collection.count_documents({
            "agent_success": {"$ne": None},
            "analysis.category": category,
            "overrides": {"$exists": True, "$ne": []}
        })

        if cat_processed > 0:
            by_category[category] = 1.0 - (cat_overridden / cat_processed)

    logger.info(
        f"Accuracy computed: {overall_accuracy:.2%} overall, "
        f"{processed} processed, {overridden} overridden"
    )

    return AccuracyMetrics(
        total_processed=processed,
        total_overridden=overridden,
        overall_accuracy=overall_accuracy,
        by_category=by_category,
    )


async def compute_urgency_breakdown() -> UrgencyBreakdown:
    """
    Compute breakdown of feedback by urgency level.

    Returns:
        UrgencyBreakdown with counts for low, medium, high urgency
    """
    collection = get_feedbacks_collection()

    low = await collection.count_documents({"analysis.urgency_level": "low"})
    medium = await collection.count_documents({"analysis.urgency_level": "medium"})
    high = await collection.count_documents({"analysis.urgency_level": "high"})
    total = low + medium + high

    logger.info(f"Urgency breakdown: low={low}, medium={medium}, high={high}, total={total}")

    return UrgencyBreakdown(low=low, medium=medium, high=high, total=total)


async def compute_sentiment_trend(days: int = 7) -> List[SentimentTrend]:
    """
    Compute daily sentiment trend for the last N days.

    Args:
        days: Number of days to look back (default 7)

    Returns:
        List of SentimentTrend objects with daily sentiment counts
    """
    collection = get_feedbacks_collection()

    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # MongoDB aggregation pipeline to group by date and sentiment
    pipeline = [
        {
            "$match": {
                "created_at": {"$gte": start_date, "$lte": end_date},
                "analysis.sentiment": {"$exists": True}
            }
        },
        {
            "$group": {
                "_id": {
                    "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                    "sentiment": "$analysis.sentiment"
                },
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"_id.date": 1}}
    ]

    results = await collection.aggregate(pipeline).to_list(length=None)

    # Transform results into SentimentTrend objects
    # Group by date
    by_date: Dict[str, Dict[str, int]] = {}
    for result in results:
        date = result["_id"]["date"]
        sentiment = result["_id"]["sentiment"]
        count = result["count"]

        if date not in by_date:
            by_date[date] = {"positive": 0, "neutral": 0, "negative": 0}

        by_date[date][sentiment] = count

    # Convert to list of SentimentTrend
    trends = [
        SentimentTrend(
            date=date,
            positive=counts["positive"],
            neutral=counts["neutral"],
            negative=counts["negative"]
        )
        for date, counts in sorted(by_date.items())
    ]

    logger.info(f"Sentiment trend computed for {days} days: {len(trends)} data points")

    return trends
