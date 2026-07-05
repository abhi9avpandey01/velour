"""
Velour API — Background Removal Adapter.

Uses the external Remove.bg API to remove backgrounds from images.
"""

import logging
import requests

from app.ai.adapters.base import BaseAdapter
from app.core.config import settings

logger = logging.getLogger(__name__)


class BackgroundRemovalAdapter(BaseAdapter):
    """Adapter for removing backgrounds from clothing images via Remove.bg."""

    def remove_background(self, image_bytes: bytes) -> bytes:
        """Process an image and return it with a transparent background.

        Args:
            image_bytes: The raw bytes of the original image.

        Returns:
            The raw bytes of the processed PNG image.
        """
        api_key = settings.remove_bg_api_key
        if not api_key or api_key == "removebg-placeholder" or api_key == "your-removebg-api-key":
            logger.warning("Remove.bg API key not found. Returning original image.")
            return image_bytes

        try:
            response = requests.post(
                'https://api.remove.bg/v1.0/removebg',
                files={'image_file': image_bytes},
                data={'size': 'auto'},
                headers={'X-Api-Key': api_key},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.content
            else:
                logger.error(f"Remove.bg failed: {response.status_code} {response.text}")
                # Fallback to returning the original image if the API fails
                return image_bytes
        except Exception as e:
            logger.error(f"Error calling Remove.bg API: {e}")
            return image_bytes
