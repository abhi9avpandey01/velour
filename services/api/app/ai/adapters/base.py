"""
Velour API — Base AI Adapter.

Defines the abstract interface that all AI models must implement.
This ensures models are fully interchangeable.
"""

from abc import ABC


class BaseAdapter(ABC):
    """Abstract base class for all AI Gateway adapters.

    All adapter imports and heavy model initializations should happen
    inside the specific adapter methods or via the ModelRegistry to 
    prevent slowing down the main API server.
    """
    pass
