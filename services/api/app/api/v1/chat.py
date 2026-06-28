"""
Velour API — Chat Endpoints.

REST APIs for interacting with the AI Stylist Agent.
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.agent.stylist import StylistAgent
from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.models.chat import ChatMessage, ChatRole, ChatSession
from app.models.user import User
from app.schemas.chat import ChatMessageResponse, ChatResponse, SendMessageRequest
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/chat", tags=["Chat & Stylist"])


@router.post(
    "/",
    response_model=ApiResponse[ChatResponse],
    summary="Send a message to the AI Stylist",
)
async def send_message(
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ApiResponse[ChatResponse]:
    """Process a natural language request using the StylistAgent Tool Router."""
    agent = StylistAgent(db, current_user.id)
    reply = await agent.chat(request.content)
    
    return ApiResponse.ok(ChatResponse(reply=reply))


@router.get(
    "/history",
    response_model=ApiResponse[List[ChatMessageResponse]],
    summary="Get chat history",
)
async def get_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ApiResponse[List[ChatMessageResponse]]:
    """Fetch the active session's conversation history."""
    # Find active session
    stmt = (
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id, ChatSession.is_deleted == False)
        .order_by(ChatSession.created_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    
    if not session:
        return ApiResponse.ok([])
        
    # Fetch user and assistant messages (filter out raw Tool payloads)
    stmt_msgs = (
        select(ChatMessage)
        .where(
            ChatMessage.session_id == session.id,
            ChatMessage.role.in_([ChatRole.USER, ChatRole.ASSISTANT])
        )
        .order_by(ChatMessage.created_at.asc())
    )
    result_msgs = await db.execute(stmt_msgs)
    messages = result_msgs.scalars().all()
    
    # Filter out empty messages (like tool call requests which have empty content)
    formatted = [
        ChatMessageResponse(role=msg.role.value, content=msg.content)
        for msg in messages if msg.content
    ]
    
    return ApiResponse.ok(formatted)
