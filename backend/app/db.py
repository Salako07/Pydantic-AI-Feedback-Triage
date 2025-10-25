import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import logging

logger = logging.getLogger(__name__)

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://mongodb:27017")
DATABASE_NAME = "feedback_triage"

client: AsyncIOMotorClient = None
database = None


async def connect_to_mongo():
    """Connect to MongoDB."""
    global client, database
    try:
        client = AsyncIOMotorClient(MONGODB_URI)
        # Test the connection
        await client.admin.command("ping")
        database = client[DATABASE_NAME]
        logger.info(f"Connected to MongoDB at {MONGODB_URI}")
    except ConnectionFailure as e:
        logger.error(f"Could not connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close MongoDB connection."""
    global client
    if client:
        client.close()
        logger.info("Closed MongoDB connection")


def get_database():
    """Get database instance."""
    return database


def get_feedbacks_collection():
    """Get feedbacks collection."""
    return database.feedbacks
