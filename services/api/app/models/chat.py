"""
Velour API — Chat Models.

Stores the conversation history and contextual state for the Stylist Agent.
"""

import uuid
from typing import Any

from sqlalchemy import (
    Enum as SQLEnum,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum

from app.db.base import BaseModel


class ChatRole(str, Enum):
    """The role of the message sender."""
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    SYSTEM = "system"


class ChatSession(BaseModel):
    """A single continuous chat session with the Stylist Agent."""
    __tablename__ = "chat_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Optional active context the agent is currently working on
    current_occasion: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    user = relationship("User")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(BaseModel):
    """A single message within a chat session."""
    __tablename__ = "chat_messages"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    role: Mapped[ChatRole] = mapped_column(SQLEnum(ChatRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Store tool calls or arguments for observability and state rebuilding
    tool_calls: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=True)
    tool_call_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    session = relationship("ChatSession", back_populates="messages")
