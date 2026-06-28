"""
Velour API — Base Agent Tool.

Abstract base class for all Stylist Agent tools.
Defines the interface for OpenAI function calling.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseTool(ABC):
    """Abstract base class for all tools provided to the LLM."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the tool (must match function name in schema)."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """The description of what the tool does."""
        pass

    @property
    @abstractmethod
    def parameters_schema(self) -> Dict[str, Any]:
        """The OpenAI JSON schema for the tool parameters."""
        pass
        
    def to_openai_tool(self) -> Dict[str, Any]:
        """Convert to the OpenAI chat completions tool format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters_schema,
            }
        }

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with the provided arguments from the LLM."""
        pass
