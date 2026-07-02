"""
Velour API — Stylist Agent Orchestrator.

Manages the conversational loop between the User, OpenAI API, and the Tool Router.
Enforces strict guardrails via the system prompt.
"""

import json
import uuid
from typing import List

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.agent.router import ToolRouter
from app.core.config import settings
from app.models.chat import ChatMessage, ChatRole, ChatSession


SYSTEM_PROMPT = """You are the Velour AI Stylist, a personalized wardrobe assistant. 
Your goal is to help users select outfits, manage their wardrobe, and understand their style.

CRITICAL RULES:
1. YOU MUST NEVER GENERATE AN OUTFIT YOURSELF. You do not have direct access to image data or internal wardrobe storage without tools. 
2. ALWAYS use the `generate_outfit` tool when the user asks for suggestions, outfits, or clothing combinations.
3. ALWAYS use the `search_wardrobe` tool when the user asks what they own, where an item is, or for general wardrobe inquiries.
4. When presenting an outfit:
   - Cite the specific items returned by the tool.
   - Explain WHY those items work together (e.g., color coordination, occasion suitability).
   - If the output includes a reason/rationale from the tool, incorporate it into your explanation.
5. NEVER invent items, patterns, or colors that are not present in the tool results. If you don't know, admit it politely.
6. Tone: Be concise, encouraging, stylish, and fashion-forward. Keep responses easy to read.

If a tool fails or returns no results, be transparent, apologize, and ask the user to provide more details or try a different query.
"""

class StylistAgent:
    """Orchestrates the LLM and the local Velour Tools."""

    def __init__(self, session: AsyncSession, user_id: uuid.UUID):
        self.session = session
        self.user_id = user_id
        
        # Gemini uses an OpenAI-compatible API layer
        self.client = AsyncOpenAI(
            api_key=settings.gemini_api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        self.router = ToolRouter(session, user_id)

    async def get_or_create_session(self) -> ChatSession:
        """Fetch the user's active session, or create a new one."""
        # For simplicity, just grab the most recent session
        stmt = (
            select(ChatSession)
            .where(ChatSession.user_id == self.user_id, ChatSession.is_deleted == False)
            .order_by(ChatSession.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        chat_session = result.scalar_one_or_none()
        
        if not chat_session:
            chat_session = ChatSession(id=uuid.uuid4(), user_id=self.user_id)
            self.session.add(chat_session)
            await self.session.commit()
            
        return chat_session

    async def get_history(self, session_id: uuid.UUID) -> List[dict]:
        """Fetch previous messages formatted for OpenAI-compatible API."""
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
        )
        result = await self.session.execute(stmt)
        messages = result.scalars().all()
        
        history = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in messages:
            formatted = {"role": msg.role.value, "content": msg.content}
            if msg.tool_calls:
                formatted["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                formatted["tool_call_id"] = msg.tool_call_id
            history.append(formatted)
            
        return history

    async def chat(self, user_message: str) -> str:
        """The main conversational loop."""
        chat_session = await self.get_or_create_session()
        
        # 1. Save User Message
        msg = ChatMessage(
            id=uuid.uuid4(),
            session_id=chat_session.id,
            role=ChatRole.USER,
            content=user_message
        )
        self.session.add(msg)
        await self.session.commit()

        # 2. Build History
        messages = await self.get_history(chat_session.id)
        
        # 3. Call Gemini with Tools
        response = await self.client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=messages,
            tools=self.router.get_openai_tools(),
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message

        # 4. Handle Tool Calls
        if response_message.tool_calls:
            # Save the assistant's tool call request
            tool_call_msg = ChatMessage(
                id=uuid.uuid4(),
                session_id=chat_session.id,
                role=ChatRole.ASSISTANT,
                content="", # Content is empty when making a tool call
                tool_calls=[t.model_dump() for t in response_message.tool_calls]
            )
            self.session.add(tool_call_msg)
            
            # We append the exact same dictionary to our local messages array so the next API call works
            messages.append(response_message.model_dump(exclude_none=True))

            for tool_call in response_message.tool_calls:
                # Execute tool
                args = json.loads(tool_call.function.arguments)
                tool_result = await self.router.execute_tool(tool_call.function.name, args)
                
                # Save the tool's result
                result_str = json.dumps(tool_result)
                tool_result_msg = ChatMessage(
                    id=uuid.uuid4(),
                    session_id=chat_session.id,
                    role=ChatRole.TOOL,
                    content=result_str,
                    tool_call_id=tool_call.id
                )
                self.session.add(tool_result_msg)
                
                # Append to active history
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result_str,
                })
                
            # Commit all tool tracking to DB
            await self.session.commit()

            # 5. Get final response from Gemini now that it has the tool results
            final_response = await self.client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=messages,
            )
            final_content = final_response.choices[0].message.content
        else:
            final_content = response_message.content

        # 6. Save final Assistant Message
        final_msg = ChatMessage(
            id=uuid.uuid4(),
            session_id=chat_session.id,
            role=ChatRole.ASSISTANT,
            content=final_content
        )
        self.session.add(final_msg)
        await self.session.commit()

        return final_content
