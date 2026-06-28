"""
Velour API — Chat Schemas.

Pydantic schemas for the Chat API.
"""

from typing import Any, List
from pydantic import BaseModel, ConfigDict


class SendMessageRequest(BaseModel):
    """The JSON payload to send a message to the Stylist Agent."""
    content: str


class ChatMessageResponse(BaseModel):
    """A formatted message from the history."""
    role: str
    content: str
    
    # Hide tool calls from the simple frontend response unless needed
    model_config = ConfigDict(from_attributes=True)


class ChatResponse(BaseModel):
    """The agent's reply."""
    reply: str
