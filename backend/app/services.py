import logging
from datetime import datetime
from typing import Optional, Dict, Any
from bson import ObjectId
from .db import get_feedbacks_collection
from .models import feedback_to_dict, feedback_from_dict, serialize_feedback
from .schemas import FeedbackCreate, FeedbackDB, FeedbackAnalysis, OverrideCreate
from .ai_agent import analyze_message
from .integrations import send_slack_notification
import uuid

logger = logging.getLogger(__name__)


async def create_feedback(
    feedback_data: FeedbackCreate,
) -> FeedbackDB:
    """
    Create a new feedback entry with AI analysis.

    Args:
        feedback_data: Validated feedback input

    Returns:
        FeedbackDB: Saved feedback with analysis
    """
    request_id = str(uuid.uuid4())[:8]

    logger.info(f"[{request_id}] Creating feedback for {feedback_data.email}")

    # Run AI analysis
    analysis, error = await analyze_message(feedback_data.message, request_id)

    # Phase 2: Set agent_success based on whether analysis succeeded
    agent_success = analysis is not None

    # Prepare document
    doc_data = {
        "customer_name": feedback_data.customer_name,
        "email": feedback_data.email,
        "message": feedback_data.message,
        "analysis": analysis.model_dump() if analysis else None,
        "analysis_error": error,
        "agent_success": agent_success,  # Phase 2
    }

    doc = feedback_from_dict(doc_data)

    # Save to database
    collection = get_feedbacks_collection()
    result = await collection.insert_one(doc)

    # Retrieve and return
    saved_doc = await collection.find_one({"_id": result.inserted_id})
    feedback_dict = feedback_to_dict(saved_doc)

    feedback_obj = FeedbackDB(**feedback_dict)

    logger.info(f"[{request_id}] Feedback saved with ID: {feedback_dict['id']}")

    # Phase 2: Send Slack notification for high urgency
    if agent_success and analysis.urgency_level == "high":
        logger.info(f"[{request_id}] Sending Slack notification for high urgency feedback")
        send_slack_notification(feedback_obj)

    return feedback_obj


async def get_feedbacks(
    limit: int = 50,
    skip: int = 0,
    urgency: Optional[str] = None,
    category: Optional[str] = None,
    sentiment: Optional[str] = None,
    unresolved_only: bool = False,
) -> tuple[list[FeedbackDB], int]:
    """
    Get feedbacks with optional filters.

    Returns:
        tuple: (list of feedbacks, total count)
    """
    collection = get_feedbacks_collection()

    # Build filter query
    query: Dict[str, Any] = {}

    if urgency:
        query["analysis.urgency_level"] = urgency

    if category:
        query["analysis.category"] = {"$regex": category, "$options": "i"}

    if sentiment:
        query["analysis.sentiment"] = sentiment

    if unresolved_only:
        # In a real system, you'd have a "resolved" field
        # For now, we'll just filter out null analysis as a proxy
        query["analysis"] = {"$ne": None}

    # Get total count
    total = await collection.count_documents(query)

    # Get feedbacks
    cursor = collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
    feedbacks = await cursor.to_list(length=limit)

    # Convert to response format
    feedback_list = [FeedbackDB(**feedback_to_dict(f)) for f in feedbacks]

    return feedback_list, total


async def get_feedback_by_id(feedback_id: str) -> Optional[FeedbackDB]:
    """Get a single feedback by ID."""
    collection = get_feedbacks_collection()

    try:
        feedback = await collection.find_one({"_id": ObjectId(feedback_id)})
        if feedback:
            return FeedbackDB(**feedback_to_dict(feedback))
    except Exception as e:
        logger.error(f"Error fetching feedback {feedback_id}: {e}")

    return None


async def apply_override(
    feedback_id: str,
    override_data: OverrideCreate
) -> Optional[FeedbackDB]:
    """
    Phase 2: Apply human override to AI analysis field.

    Args:
        feedback_id: ID of the feedback to override
        override_data: Override details (field, new_value, reason, overridden_by)

    Returns:
        Updated FeedbackDB or None if feedback not found
    """
    collection = get_feedbacks_collection()

    try:
        # Get current feedback
        feedback = await collection.find_one({"_id": ObjectId(feedback_id)})
        if not feedback:
            logger.warning(f"Feedback {feedback_id} not found for override")
            return None

        # Get old value from analysis
        old_value = None
        if feedback.get("analysis"):
            old_value = feedback["analysis"].get(override_data.field)

        # Create override record
        override_record = {
            "field": override_data.field,
            "old_value": str(old_value) if old_value is not None else None,
            "new_value": override_data.new_value,
            "reason": override_data.reason,
            "overridden_by": override_data.overridden_by,
            "overridden_at": datetime.utcnow(),
        }

        # Update feedback: modify analysis field and append override record
        update_operations = {
            "$push": {"overrides": override_record}
        }

        # Also update the analysis field itself with the new value
        if feedback.get("analysis"):
            update_operations["$set"] = {
                f"analysis.{override_data.field}": override_data.new_value
            }

        result = await collection.update_one(
            {"_id": ObjectId(feedback_id)},
            update_operations
        )

        if result.modified_count == 0:
            logger.warning(f"Failed to apply override to feedback {feedback_id}")
            return None

        # Retrieve and return updated feedback
        updated_feedback = await collection.find_one({"_id": ObjectId(feedback_id)})
        feedback_dict = feedback_to_dict(updated_feedback)

        logger.info(
            f"Override applied to feedback {feedback_id}: "
            f"{override_data.field} changed from '{old_value}' to '{override_data.new_value}' "
            f"by {override_data.overridden_by}"
        )

        return FeedbackDB(**feedback_dict)

    except Exception as e:
        logger.error(f"Error applying override to feedback {feedback_id}: {e}", exc_info=True)
        return None
