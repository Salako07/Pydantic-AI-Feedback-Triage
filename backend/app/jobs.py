"""
Phase 2: Background jobs using APScheduler.
Weekly review job to compute metrics and send Slack summary.
"""
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from .metrics import compute_accuracy, compute_urgency_breakdown, compute_sentiment_trend
from .integrations import send_weekly_summary_to_slack

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler: AsyncIOScheduler = None


def get_scheduler() -> AsyncIOScheduler:
    """Get or create the global scheduler instance."""
    global scheduler
    if scheduler is None:
        scheduler = AsyncIOScheduler()
    return scheduler


async def weekly_review_job():
    """
    Weekly review job: compute metrics, save report, send to Slack.
    Runs every Monday at 9 AM UTC by default (configurable via env var).
    """
    logger.info("Starting weekly review job...")

    try:
        # Compute metrics
        accuracy = await compute_accuracy()
        urgency = await compute_urgency_breakdown()
        sentiment_trend = await compute_sentiment_trend(days=7)

        # Prepare report data
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "accuracy": {
                "total_processed": accuracy.total_processed,
                "total_overridden": accuracy.total_overridden,
                "overall_accuracy": accuracy.overall_accuracy,
                "by_category": accuracy.by_category,
            },
            "urgency_breakdown": {
                "low": urgency.low,
                "medium": urgency.medium,
                "high": urgency.high,
                "total": urgency.total,
            },
            "sentiment_trend": [
                {
                    "date": trend.date,
                    "positive": trend.positive,
                    "neutral": trend.neutral,
                    "negative": trend.negative,
                }
                for trend in sentiment_trend
            ],
        }

        # Save report to file
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        report_path = reports_dir / f"weekly_report_{timestamp}.json"

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Weekly report saved to {report_path}")

        # Send to Slack
        send_weekly_summary_to_slack(accuracy, urgency, str(report_path))

        logger.info("Weekly review job completed successfully")

    except Exception as e:
        logger.error(f"Error in weekly review job: {e}", exc_info=True)


def start_scheduler():
    """
    Start the APScheduler with weekly review job.
    Schedule is configurable via SCHEDULE_CRON_WEEKLY env var.
    Default: Every Monday at 9 AM UTC (cron: "0 9 * * 1")
    """
    scheduler = get_scheduler()

    # Get cron schedule from env var or use default
    cron_expr = os.getenv("SCHEDULE_CRON_WEEKLY", "0 9 * * 1")

    # Parse cron expression (minute hour day month day_of_week)
    parts = cron_expr.split()
    if len(parts) != 5:
        logger.error(f"Invalid cron expression: {cron_expr}. Using default.")
        parts = ["0", "9", "*", "*", "1"]

    trigger = CronTrigger(
        minute=parts[0],
        hour=parts[1],
        day=parts[2],
        month=parts[3],
        day_of_week=parts[4],
        timezone="UTC"
    )

    # Add job to scheduler
    scheduler.add_job(
        weekly_review_job,
        trigger=trigger,
        id="weekly_review",
        name="Weekly AI Agent Performance Review",
        replace_existing=True,
    )

    # Start scheduler
    scheduler.start()

    logger.info(
        f"Scheduler started. Weekly review job scheduled with cron: {cron_expr} "
        f"(next run: {scheduler.get_job('weekly_review').next_run_time})"
    )


def stop_scheduler():
    """Stop the APScheduler gracefully."""
    scheduler = get_scheduler()
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
