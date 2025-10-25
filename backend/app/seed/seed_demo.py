"""
Phase 2: Demo data seeding script.
Seeds the database with sample feedback for testing and demonstration.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.db import connect_to_mongo, close_mongo_connection, get_feedbacks_collection
from app.schemas import FeedbackCreate, OverrideCreate
from app.services import create_feedback, apply_override
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Demo feedback messages
DEMO_FEEDBACKS = [
    {
        "customer_name": "Sarah Johnson",
        "email": "sarah.j@example.com",
        "message": "I absolutely love your product! It has made my workflow so much more efficient. The interface is intuitive and the features are exactly what I needed. Keep up the great work!"
    },
    {
        "customer_name": "Michael Chen",
        "email": "m.chen@company.com",
        "message": "I've been trying to access my premium account for the past 2 hours but keep getting an error. This is completely unacceptable as I paid for this service. I need this resolved immediately or I want a full refund!"
    },
    {
        "customer_name": "Emily Rodriguez",
        "email": "emily.r@startup.io",
        "message": "The recent update broke several features I use daily. The export function no longer works and the app crashes when I try to sync. Please fix this ASAP as it's affecting my work."
    },
    {
        "customer_name": "David Kim",
        "email": "david.kim@email.com",
        "message": "It would be great if you could add a dark mode option. I often work late at night and the bright interface strains my eyes. Just a suggestion for a future update!"
    },
    {
        "customer_name": "Jessica Martinez",
        "email": "jess.martinez@domain.com",
        "message": "Your support team was incredibly helpful! They resolved my billing issue within minutes. Very impressed with the customer service."
    },
    {
        "customer_name": "Robert Taylor",
        "email": "r.taylor@business.com",
        "message": "Critical issue: Our entire team cannot log in to the platform. We have a client presentation in 30 minutes and need access urgently. This is causing significant business disruption."
    },
    {
        "customer_name": "Amanda White",
        "email": "amanda.white@example.org",
        "message": "The mobile app could use some improvements. It's functional but feels a bit clunky compared to the web version. Maybe simplify the navigation?"
    },
    {
        "customer_name": "Christopher Lee",
        "email": "chris.lee@tech.com",
        "message": "Question about the API rate limits. I'm building an integration and want to make sure I understand the throttling correctly. Can someone from the tech team reach out?"
    },
    {
        "customer_name": "Laura Garcia",
        "email": "laura.g@company.net",
        "message": "Been using your service for 6 months now. Overall it's solid, but occasionally the system is slow during peak hours. Not a dealbreaker but worth mentioning."
    },
    {
        "customer_name": "James Anderson",
        "email": "j.anderson@email.com",
        "message": "You charged my card twice this month! I've been trying to reach billing for 3 days with no response. This is unacceptable and I'm considering switching to a competitor if not resolved today."
    },
]


async def seed_demo_data():
    """Seed the database with demo feedback."""
    logger.info("Starting demo data seeding...")

    # Connect to database
    await connect_to_mongo()

    # Create all demo feedbacks
    created_feedbacks = []
    for i, feedback_data in enumerate(DEMO_FEEDBACKS, 1):
        try:
            feedback = FeedbackCreate(**feedback_data)
            result = await create_feedback(feedback)
            created_feedbacks.append(result)
            logger.info(f"[{i}/{len(DEMO_FEEDBACKS)}] Created feedback: {result.id} - {result.customer_name}")
        except Exception as e:
            logger.error(f"Failed to create feedback {i}: {e}")

    logger.info(f"Created {len(created_feedbacks)} demo feedbacks")

    # Apply a demo override to demonstrate the feature
    if created_feedbacks:
        # Override the sentiment of the first feedback
        first_feedback = created_feedbacks[0]
        try:
            override = OverrideCreate(
                field="sentiment",
                new_value="positive",
                reason="Demo override: Correcting AI sentiment analysis for demonstration purposes",
                overridden_by="demo@admin.com"
            )
            await apply_override(first_feedback.id, override)
            logger.info(f"Applied demo override to feedback {first_feedback.id}")
        except Exception as e:
            logger.error(f"Failed to apply demo override: {e}")

    # Close connection
    await close_mongo_connection()

    logger.info("Demo data seeding completed!")
    logger.info(f"You can now test the API with {len(created_feedbacks)} sample feedbacks")


async def clear_demo_data():
    """Clear all feedback data from the database (use with caution)."""
    logger.warning("Clearing all feedback data...")

    await connect_to_mongo()
    collection = get_feedbacks_collection()

    result = await collection.delete_many({})
    logger.info(f"Deleted {result.deleted_count} feedback documents")

    await close_mongo_connection()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed or clear demo data")
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear all feedback data instead of seeding"
    )
    args = parser.parse_args()

    if args.clear:
        asyncio.run(clear_demo_data())
    else:
        asyncio.run(seed_demo_data())
