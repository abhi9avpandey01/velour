"""
Velour API — Background Removal Adapter.

Uses the 'rembg' library to remove backgrounds from images.
"""

import io

from PIL import Image
import rembg

from app.ai.adapters.base import BaseAdapter


class BackgroundRemovalAdapter(BaseAdapter):
    """Adapter for removing backgrounds from clothing images."""

    def remove_background(self, image_bytes: bytes) -> bytes:
        """Process an image and return it with a transparent background.

        Args:
            image_bytes: The raw bytes of the original image.

        Returns:
            The raw bytes of the processed PNG image.
        """
        input_image = Image.open(io.BytesIO(image_bytes))
        
        # rembg automatically downloads its u2net models on first run
        output_image = rembg.remove(input_image)
        
        output_buffer = io.BytesIO()
        output_image.save(output_buffer, format="PNG")
        
        return output_buffer.getvalue()
