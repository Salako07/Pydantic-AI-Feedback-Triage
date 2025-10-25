from datetime import datetime
from typing import Literal, Optional, List
from pydantic import BaseModel, EmailStr, Field


class FeedbackCreate(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    message: str = Field(..., min_length=1, max_length=8000)


class FeedbackAnalysis(BaseModel):
    sentiment: Literal["positive", "neutral", "negative"]
    urgency_level: Literal["low", "medium", "high"]
    category: str = Field(..., min_length=1, max_length=100)
    summary: str = Field(..., min_length=1, max_length=500)
    recommended_action: str = Field(..., min_length=1, max_length=500)


# Phase 2: Override schemas
class OverrideCreate(BaseModel):
    """Request to override AI analysis field."""
    field: Literal["sentiment", "urgency_level", "category", "summary", "recommended_action"]
    new_value: str = Field(..., min_length=1, max_length=500)
    reason: str = Field(..., min_length=1, max_length=1000)
    overridden_by: str = Field(..., min_length=1, max_length=200)  # email or name


class OverrideRecord(BaseModel):
    """Record of a human override."""
    field: str
    old_value: Optional[str]
    new_value: str
    reason: str
    overridden_by: str
    overridden_at: datetime


class FeedbackDB(BaseModel):
    id: str
    customer_name: str
    email: str
    message: str
    created_at: datetime
    analysis: Optional[FeedbackAnalysis] = None
    analysis_error: Optional[str] = None
    agent_success: Optional[bool] = None  # Phase 2: True if AI succeeded, False if failed
    overrides: List[OverrideRecord] = []  # Phase 2: List of human corrections


class FeedbackResponse(FeedbackDB):
    pass


class FeedbackListResponse(BaseModel):
    feedbacks: list[FeedbackResponse]
    total: int


# Phase 2: Metrics schemas
class AccuracyMetrics(BaseModel):
    """Metrics for AI agent accuracy."""
    total_processed: int
    total_overridden: int
    overall_accuracy: float  # 1 - (overridden / processed)
    by_category: dict[str, float]  # category -> accuracy


class UrgencyBreakdown(BaseModel):
    """Breakdown of feedback by urgency level."""
    low: int
    medium: int
    high: int
    total: int


class SentimentTrend(BaseModel):
    """Sentiment trend data."""
    date: str  # ISO date
    positive: int
    neutral: int
    negative: int


class PromptConfig(BaseModel):
    """Configuration for AI prompt tuning."""
    bias_words: List[str] = []
    urgency_rules: dict = {}
    max_retries: int = 2
    version: str = "1.0"
