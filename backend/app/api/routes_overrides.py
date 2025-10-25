"""
Phase 2: Override API routes.
Endpoints for applying human corrections to AI analysis.
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from ..services import apply_override, get_feedback_by_id
from ..schemas import OverrideCreate, FeedbackResponse, OverrideRecord

router = APIRouter(prefix="/api/feedback", tags=["overrides"])


@router.post("/{feedback_id}/override", response_model=FeedbackResponse, status_code=status.HTTP_200_OK)
async def create_override(feedback_id: str, override_data: OverrideCreate):
    """
    Apply human override to AI analysis field.

    This endpoint allows human reviewers to correct AI agent mistakes.
    The override is recorded with the reason and reviewer info for audit trail.

    Args:
        feedback_id: ID of the feedback to override
        override_data: Override details (field, new_value, reason, overridden_by)

    Returns:
        Updated feedback with the override applied

    Raises:
        404: Feedback not found
        500: Failed to apply override
    """
    result = await apply_override(feedback_id, override_data)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feedback with ID {feedback_id} not found"
        )

    return result


@router.get("/{feedback_id}/overrides", response_model=List[OverrideRecord])
async def get_overrides(feedback_id: str):
    """
    Get all override records for a feedback.

    Returns the complete audit trail of human corrections
    applied to this feedback's AI analysis.

    Args:
        feedback_id: ID of the feedback

    Returns:
        List of override records

    Raises:
        404: Feedback not found
    """
    feedback = await get_feedback_by_id(feedback_id)

    if feedback is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feedback with ID {feedback_id} not found"
        )

    return feedback.overrides
