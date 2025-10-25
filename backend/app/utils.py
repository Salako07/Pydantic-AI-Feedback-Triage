import logging
from typing import Any
import json


def setup_logging():
    """Configure structured logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def mask_email(email: str) -> str:
    """Mask email for logging privacy."""
    if "@" in email:
        local, domain = email.split("@")
        masked_local = local[:2] + "***" if len(local) > 2 else "***"
        return f"{masked_local}@{domain}"
    return "***"


def serialize_for_json(obj: Any) -> str:
    """Serialize object to JSON string."""
    return json.dumps(obj, default=str)
