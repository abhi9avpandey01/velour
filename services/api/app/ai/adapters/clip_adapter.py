"""
Velour API — CLIP Adapter.

Generates 512-dimensional embedding vectors using Hugging Face Inference API.
"""

import logging
import math
import requests

from app.ai.adapters.base import BaseAdapter
from app.core.config import settings

logger = logging.getLogger(__name__)


class CLIPAdapter(BaseAdapter):
    """Adapter for generating similarity embeddings using Hugging Face API."""

    def __init__(self) -> None:
        self.api_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/openai/clip-vit-base-patch32"
        self.headers = {"Authorization": f"Bearer {settings.hf_api_token}"}

    def _normalize(self, embedding: list[float]) -> list[float]:
        norm = math.sqrt(sum(x * x for x in embedding))
        if norm > 0:
            return [x / norm for x in embedding]
        return embedding

    def generate_embedding(self, image_bytes: bytes) -> list[float]:
        """Generate a 512-dimensional embedding vector for an image via HF API."""
        if not settings.hf_api_token or settings.hf_api_token == "hf-placeholder" or settings.hf_api_token == "your-hf-api-token":
            logger.warning("HF API token not found. Returning empty embedding.")
            return [0.0] * 512
            
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                data=image_bytes,
                timeout=15
            )
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0 and isinstance(result[0], list):
                    embedding = result[0]
                elif isinstance(result, list):
                    embedding = result
                else:
                    embedding = [0.0] * 512
                
                return self._normalize(embedding)
            else:
                logger.error(f"HF API failed: {response.status_code} {response.text}")
                return [0.0] * 512
        except Exception as e:
            logger.error(f"Error calling HF API: {e}")
            return [0.0] * 512

    def generate_text_embedding(self, text: str) -> list[float]:
        """Generate a 512-dimensional embedding vector for text via HF API."""
        if not settings.hf_api_token or settings.hf_api_token == "hf-placeholder" or settings.hf_api_token == "your-hf-api-token":
            logger.warning("HF API token not found. Returning empty embedding.")
            return [0.0] * 512

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={"inputs": [text]},
                timeout=15
            )
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0 and isinstance(result[0], list):
                    embedding = result[0]
                elif isinstance(result, list):
                    embedding = result
                else:
                    embedding = [0.0] * 512
                
                return self._normalize(embedding)
            else:
                logger.error(f"HF API failed: {response.status_code} {response.text}")
                return [0.0] * 512
        except Exception as e:
            logger.error(f"Error calling HF API: {e}")
            return [0.0] * 512

