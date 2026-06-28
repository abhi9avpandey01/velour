"""
Velour API — Tool Router.

Maps OpenAI tool call names to the actual python BaseTool instances.
"""

import uuid
from typing import Any, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.tools.base import BaseTool
from app.agent.tools.recommendation_tool import GenerateOutfitTool
from app.agent.tools.wardrobe_tool import SearchWardrobeTool


class ToolRouter:
    """Manages available tools and dispatches LLM calls to them."""

    def __init__(self, session: AsyncSession, user_id: uuid.UUID):
        self.session = session
        self.user_id = user_id
        
        # Instantiate available tools
        self._tools: Dict[str, BaseTool] = {
            "generate_outfit": GenerateOutfitTool(session, user_id),
            "search_wardrobe": SearchWardrobeTool(session, user_id),
        }

    def get_openai_tools(self) -> List[Dict[str, Any]]:
        """Return the JSON schema array required by the OpenAI API."""
        return [tool.to_openai_tool() for tool in self._tools.values()]

    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Find the requested tool and execute it."""
        tool = self._tools.get(name)
        if not tool:
            return {"error": f"Tool '{name}' is not registered."}
            
        try:
            return await tool.execute(**arguments)
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
