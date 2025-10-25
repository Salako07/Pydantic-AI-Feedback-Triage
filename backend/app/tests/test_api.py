import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from ..main import app
from ..schemas import FeedbackAnalysis, FeedbackDB
from datetime import datetime


@pytest.mark.asyncio
async def test_create_feedback_success():
    """Test successful feedback creation."""
    mock_feedback = FeedbackDB(
        id="507f1f77bcf86cd799439011",
        customer_name="John Doe",
        email="john@example.com",
        message="I love your product!",
        created_at=datetime.utcnow(),
        analysis=FeedbackAnalysis(
            sentiment="positive",
            urgency_level="low",
            category="product",
            summary="Customer expresses satisfaction with product",
            recommended_action="Send thank you note and ask for testimonial"
        )
    )

    with patch('app.api.routes_feedback.create_feedback', new_callable=AsyncMock) as mock_create:
        with patch('app.api.routes_feedback.manager.broadcast', new_callable=AsyncMock):
            mock_create.return_value = mock_feedback

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/feedback",
                    json={
                        "customer_name": "John Doe",
                        "email": "john@example.com",
                        "message": "I love your product!"
                    }
                )

            assert response.status_code == 201
            data = response.json()
            assert data["customer_name"] == "John Doe"
            assert data["email"] == "john@example.com"
            assert data["analysis"]["sentiment"] == "positive"


@pytest.mark.asyncio
async def test_create_feedback_validation_error():
    """Test feedback creation with invalid input."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/feedback",
            json={
                "customer_name": "",  # Invalid: empty
                "email": "invalid-email",  # Invalid format
                "message": "Test"
            }
        )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_list_feedbacks():
    """Test listing feedbacks with filters."""
    mock_feedbacks = [
        FeedbackDB(
            id="507f1f77bcf86cd799439011",
            customer_name="Jane Smith",
            email="jane@example.com",
            message="Billing issue",
            created_at=datetime.utcnow(),
            analysis=FeedbackAnalysis(
                sentiment="negative",
                urgency_level="high",
                category="billing",
                summary="Customer has billing problem",
                recommended_action="Contact immediately"
            )
        )
    ]

    with patch('app.api.routes_feedback.get_feedbacks', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = (mock_feedbacks, 1)

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/feedback?limit=10&urgency=high")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["feedbacks"]) == 1
        assert data["feedbacks"][0]["analysis"]["urgency_level"] == "high"


@pytest.mark.asyncio
async def test_get_feedback_by_id():
    """Test getting single feedback by ID."""
    mock_feedback = FeedbackDB(
        id="507f1f77bcf86cd799439011",
        customer_name="Bob Johnson",
        email="bob@example.com",
        message="Feature request",
        created_at=datetime.utcnow(),
        analysis=FeedbackAnalysis(
            sentiment="neutral",
            urgency_level="low",
            category="product",
            summary="Customer suggests new feature",
            recommended_action="Add to product backlog"
        )
    )

    with patch('app.api.routes_feedback.get_feedback_by_id', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_feedback

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/feedback/507f1f77bcf86cd799439011")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "507f1f77bcf86cd799439011"
        assert data["customer_name"] == "Bob Johnson"


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
