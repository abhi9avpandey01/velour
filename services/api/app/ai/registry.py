"""
Velour API — Model Registry.

Responsible for caching and memory management of heavy AI models (PyTorch/Transformers).
Supports lazy loading and automatic device allocation (GPU/CPU).
"""

import logging
from typing import Any, Dict

import torch

logger = logging.getLogger(__name__)


class ModelRegistry:
    """Singleton registry for AI models to prevent memory leaks and redundant loading."""

    _instance = None
    _models: Dict[str, Any] = {}
    _device: str = "cuda" if torch.cuda.is_available() else "cpu"

    def __new__(cls) -> "ModelRegistry":
        if cls._instance is None:
            cls._instance = super(ModelRegistry, cls).__new__(cls)
            logger.info(f"ModelRegistry initialized. Using device: {cls._device}")
        return cls._instance

    @property
    def device(self) -> str:
        """Get the active compute device (cuda or cpu)."""
        return self._device

    def get_model(self, model_key: str, loader_func: Any) -> Any:
        """Retrieve a model from memory, loading it if necessary.

        Args:
            model_key: Unique identifier for the model.
            loader_func: A callable that returns the loaded model and processor.

        Returns:
            The loaded model (usually a tuple of model and processor).
        """
        if model_key not in self._models:
            logger.info(f"Lazy loading model: {model_key} onto {self.device}")
            try:
                self._models[model_key] = loader_func(self.device)
                logger.info(f"Successfully loaded {model_key}")
            except Exception as e:
                logger.error(f"Failed to load model {model_key}: {e}")
                raise

        return self._models[model_key]

    def unload_model(self, model_key: str) -> None:
        """Unload a model from memory to free up VRAM/RAM."""
        if model_key in self._models:
            del self._models[model_key]
            
            # Force garbage collection and empty CUDA cache
            import gc
            gc.collect()
            if self.device == "cuda":
                torch.cuda.empty_cache()
                
            logger.info(f"Unloaded model: {model_key}")

    def clear_all(self) -> None:
        """Clear all loaded models."""
        keys = list(self._models.keys())
        for key in keys:
            self.unload_model(key)


# Global singleton instance
registry = ModelRegistry()
