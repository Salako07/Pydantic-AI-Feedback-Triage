from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Query
from typing import Optional, List
import logging
import json
from ..schemas import FeedbackCreate, FeedbackResponse, FeedbackListResponse
from ..services import create_feedback, get_feedbacks, get_feedback_by_id
from ..models import serialize_feedback

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["feedback"])

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.append(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.active_connections.remove(conn)


manager = ConnectionManager()


@router.post("/feedback", response_model=FeedbackResponse, status_code=201)
async def create_feedback_endpoint(feedback: FeedbackCreate):
    """
    Create a new feedback entry.

    - Validates input
    - Runs AI analysis
    - Saves to database
    - Broadcasts to WebSocket clients
    """
    try:
        # Create feedback with AI analysis
        saved_feedback = await create_feedback(feedback)

        # Serialize for response
        response_data = serialize_feedback(saved_feedback.model_dump())

        # Broadcast to WebSocket clients
        await manager.broadcast({
            "type": "feedbacks:new",
            "data": response_data
        })

        return response_data

    except Exception as e:
        logger.error(f"Error creating feedback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create feedback: {str(e)}")


@router.get("/feedback", response_model=FeedbackListResponse)
async def list_feedbacks(
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    urgency: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    sentiment: Optional[str] = Query(None),
    unresolved_only: bool = Query(False),
):
    """
    List feedbacks with optional filters.

    - Supports pagination (limit/skip)
    - Filters: urgency, category, sentiment, unresolved_only
    """
    try:
        feedbacks, total = await get_feedbacks(
            limit=limit,
            skip=skip,
            urgency=urgency,
            category=category,
            sentiment=sentiment,
            unresolved_only=unresolved_only,
        )

        # Serialize feedbacks
        serialized = [serialize_feedback(f.model_dump()) for f in feedbacks]

        return FeedbackListResponse(feedbacks=serialized, total=total)

    except Exception as e:
        logger.error(f"Error listing feedbacks: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list feedbacks: {str(e)}")


@router.get("/feedback/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback(feedback_id: str):
    """Get a single feedback by ID."""
    try:
        feedback = await get_feedback_by_id(feedback_id)

        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")

        return serialize_feedback(feedback.model_dump())

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feedback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get feedback: {str(e)}")


@router.websocket("/ws/feedbacks")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for realtime feedback updates.

    Clients receive new feedback as it's created.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and listen for client messages
            data = await websocket.receive_text()
            # Echo back for heartbeat (optional)
            await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
