"""
Velour API — CLIP Adapter.

Generates 512-dimensional embedding vectors from clothing images using
OpenAI's CLIP model (clip-vit-base-patch32).
"""

import io
from typing import Any

from PIL import Image
import torch

from app.ai.adapters.base import BaseAdapter
from app.ai.registry import registry


def _load_clip(device: str) -> tuple[Any, Any]:
    """Load the CLIP model and processor into memory."""
    from transformers import CLIPModel, CLIPProcessor
    
    model_id = "openai/clip-vit-base-patch32"
    model = CLIPModel.from_pretrained(model_id).to(device)
    processor = CLIPProcessor.from_pretrained(model_id)
    return model, processor


class CLIPAdapter(BaseAdapter):
    """Adapter for generating similarity embeddings using CLIP."""

    def __init__(self) -> None:
        self.model_key = "clip-vit-base-patch32"
        self.model, self.processor = registry.get_model(self.model_key, _load_clip)
        self.device = registry.device

    def generate_embedding(self, image_bytes: bytes) -> list[float]:
        """Generate a 512-dimensional embedding vector for an image.

        Args:
            image_bytes: The raw image bytes.

        Returns:
            A list of 512 floats representing the embedding.
        """
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
            
        # Normalize the embedding for cosine similarity search later
        image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)
        
        # Convert to a flat Python list of floats
        embedding = image_features.squeeze(0).cpu().tolist()
        return embedding

    def generate_text_embedding(self, text: str) -> list[float]:
        """Generate a 512-dimensional embedding vector for text.

        Args:
            text: The query string.

        Returns:
            A list of 512 floats representing the text embedding.
        """
        inputs = self.processor(text=[text], return_tensors="pt", padding=True).to(self.device)
        
        with torch.no_grad():
            text_features = self.model.get_text_features(**inputs)
            
        text_features = text_features / text_features.norm(p=2, dim=-1, keepdim=True)
        embedding = text_features.squeeze(0).cpu().tolist()
        return embedding
