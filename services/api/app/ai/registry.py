"""
Velour API — AI Model Registry.

Singleton registry to cache and manage heavy AI models in memory.
Implements a strict LRU (Least Recently Used) eviction policy to prevent VRAM memory leaks.
"""

import gc
import logging
from typing import Any, Callable, Dict

import torch

logger = logging.getLogger(__name__)


class ModelRegistry:
    """Singleton registry to cache and manage heavy AI models in memory."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.models: Dict[str, tuple[Any, Any]] = {}
            self.usage_order: list[str] = []
            self.max_models_in_memory = 2  # Prevent OOM by keeping only max 2 heavy models loaded
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self._initialized = True

    def get_model(self, key: str, loader_func: Callable[[str], tuple[Any, Any]]) -> tuple[Any, Any]:
        """Fetch a model from memory, loading it if necessary."""
        if key in self.models:
            # Update LRU order
            self.usage_order.remove(key)
            self.usage_order.append(key)
            return self.models[key]
            
        logger.info(f"ModelRegistry: Cache miss for '{key}'. Loading to {self.device}...")
        
        # Evict oldest model if we hit the limit
        if len(self.models) >= self.max_models_in_memory:
            lru_key = self.usage_order.pop(0)
            self.unload_model(lru_key)
            
        try:
            model_tuple = loader_func(self.device)
            self.models[key] = model_tuple
            self.usage_order.append(key)
            logger.info(f"Successfully loaded {key}")
            return model_tuple
        except Exception as e:
            logger.error(f"Failed to load model {key}: {e}", exc_info=True)
            raise

    def unload_model(self, key: str) -> None:
        """Explicitly remove a model from memory and flush VRAM."""
        if key in self.models:
            logger.info(f"ModelRegistry: Evicting '{key}' from memory to free VRAM.")
            del self.models[key]
            if key in self.usage_order:
                self.usage_order.remove(key)
            
            # Force garbage collection and CUDA cache clear
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

# Global singleton instance
registry = ModelRegistry()
