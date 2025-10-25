import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from ..ai_agent import analyze_message
from ..schemas import FeedbackAnalysis


@pytest.mark.asyncio
async def test_analyze_message_success():
    """Test successful message analysis."""
    mock_analysis = FeedbackAnalysis(
        sentiment="negative",
        urgency_level="high",
        category="billing",
        summary="Customer cannot access paid service",
        recommended_action="Investigate account billing status immediately"
    )

    mock_result = MagicMock()
    mock_result.data = mock_analysis

    with patch('app.ai_agent.agent.run', new_callable=AsyncMock) as mock_run:
        mock_run.return_value = mock_result

        analysis, error = await analyze_message(
            "I paid for premium but can't access it!",
            request_id="test-123"
        )

        assert analysis is not None
        assert error is None
        assert analysis.sentiment == "negative"
        assert analysis.urgency_level == "high"
        assert analysis.category == "billing"


@pytest.mark.asyncio
async def test_analyze_message_validation_error():
    """Test handling of validation errors with retry."""
    from pydantic_ai.exceptions import UserError

    with patch('app.ai_agent.agent.run', new_callable=AsyncMock) as mock_run:
        # Simulate validation failures
        mock_run.side_effect = UserError("Invalid JSON format")

        analysis, error = await analyze_message(
            "Test message",
            request_id="test-456"
        )

        assert analysis is None
        assert error is not None
        assert "validation failed" in error.lower()
        assert mock_run.call_count == 3  # Initial + 2 retries


@pytest.mark.asyncio
async def test_analyze_message_unexpected_error():
    """Test handling of unexpected errors."""
    with patch('app.ai_agent.agent.run', new_callable=AsyncMock) as mock_run:
        mock_run.side_effect = Exception("API connection failed")

        analysis, error = await analyze_message(
            "Test message",
            request_id="test-789"
        )

        assert analysis is None
        assert error is not None
        assert "unexpected error" in error.lower()
