"""
Velour API — AI Gateway.

Handles routing, retries, error isolation, and execution of AI adapters.
"""

import logging
import time
from typing import Any

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)


class InferenceError(Exception):
    """Raised when an AI adapter fails to complete inference."""
    pass


class AIGateway:
    """The central gateway for all AI model inference requests.

    Wraps adapter calls in robust retry policies and prevents model crashes
    from taking down the main Celery worker thread.
    """

    @staticmethod
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(InferenceError),
        reraise=True,
    )
    def execute_adapter(adapter_cls: type, method_name: str, *args: Any, **kwargs: Any) -> Any:
        """Execute a method on an AI adapter with retry logic.

        Args:
            adapter_cls: The adapter class to instantiate.
            method_name: The name of the method to call.
            *args: Positional arguments for the method.
            **kwargs: Keyword arguments for the method.

        Returns:
            The result of the adapter method.

        Raises:
            InferenceError: If all retries fail.
        """
        adapter_name = adapter_cls.__name__
        logger.info(f"Gateway routing to {adapter_name}.{method_name}")
        
        start_time = time.time()
        try:
            adapter = adapter_cls()
            method = getattr(adapter, method_name)
            result = method(*args, **kwargs)
            
            elapsed = time.time() - start_time
            logger.info(f"Gateway success: {adapter_name}.{method_name} in {elapsed:.2f}s")
            
            return result
        except Exception as e:
            logger.error(f"Gateway error in {adapter_name}.{method_name}: {e}")
            # Raise InferenceError to trigger tenacity retries
            raise InferenceError(f"Adapter failed: {e}") from e
