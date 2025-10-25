from datetime import datetime
from typing import Optional, List


class OverrideRecord:
    """Represents a human override of AI analysis."""
    def __init__(
        self,
        field: str,
        old_value: Optional[str],
        new_value: str,
        reason: str,
        overridden_by: str,
        overridden_at: datetime,
    ):
        self.field = field
        self.old_value = old_value
        self.new_value = new_value
        self.reason = reason
        self.overridden_by = overridden_by
        self.overridden_at = overridden_at

    def to_dict(self) -> dict:
        return {
            "field": self.field,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "reason": self.reason,
            "overridden_by": self.overridden_by,
            "overridden_at": self.overridden_at.isoformat() if isinstance(self.overridden_at, datetime) else self.overridden_at,
        }


def feedback_to_dict(feedback: dict) -> dict:
    """Convert MongoDB document to API response format."""
    feedback["id"] = str(feedback.pop("_id"))
    return feedback


def feedback_from_dict(data: dict) -> dict:
    """Convert API request to MongoDB document format."""
    doc = {
        "customer_name": data["customer_name"],
        "email": data["email"],
        "message": data["message"],
        "created_at": datetime.utcnow(),
        "analysis": data.get("analysis"),
        "analysis_error": data.get("analysis_error"),
        "agent_success": data.get("agent_success", None),  # Phase 2: Track if AI succeeded
        "overrides": data.get("overrides", []),  # Phase 2: Human corrections
    }
    return doc


def serialize_feedback(feedback: dict) -> dict:
    """Serialize feedback for JSON response."""
    result = feedback.copy()
    if isinstance(result.get("created_at"), datetime):
        result["created_at"] = result["created_at"].isoformat()
    # Serialize override timestamps
    if "overrides" in result:
        for override in result["overrides"]:
            if isinstance(override.get("overridden_at"), datetime):
                override["overridden_at"] = override["overridden_at"].isoformat()
    return result
