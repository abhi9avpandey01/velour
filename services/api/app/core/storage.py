"""
Velour API — Storage Client.

Wrapper around the Supabase Storage client for uploading and validating images.
"""

import io
import mimetypes
import uuid
from typing import IO

from PIL import Image, UnidentifiedImageError
from supabase import create_client, Client

from app.core.config import settings
from app.core.exceptions import ValidationError

# Initialize the Supabase client globally
supabase: Client = create_client(settings.supabase_url, settings.supabase_key)

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}


class StorageService:
    """Service to handle direct uploads to Supabase storage.

    Includes validation for file sizes, dimensions, and mime types.
    """

    @staticmethod
    async def validate_image(file_obj: IO[bytes], filename: str) -> dict[str, int | str]:
        """Validate an image file before upload.

        Validates mime type, file size, and extracts dimensions using Pillow.

        Args:
            file_obj: The file buffer.
            filename: The original filename.

        Returns:
            A dictionary containing metadata (width, height, mime_type).

        Raises:
            ValidationError: If the file is invalid or too large.
        """
        file_obj.seek(0, 2)
        size = file_obj.tell()
        file_obj.seek(0)

        if size > MAX_FILE_SIZE_BYTES:
            raise ValidationError("File exceeds maximum allowed size of 10MB.")

        # Determine MIME type
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type not in ALLOWED_MIME_TYPES:
            raise ValidationError(f"Unsupported file type. Allowed: {ALLOWED_MIME_TYPES}")

        # Validate with Pillow
        try:
            image_data = file_obj.read()
            img = Image.open(io.BytesIO(image_data))
            img.verify()  # Verify it's a valid image without decoding entirely
            file_obj.seek(0)  # Reset pointer for actual upload

            # Need to reopen to get dimensions accurately sometimes, but for simple formats this works
            img = Image.open(io.BytesIO(image_data))
            width, height = img.size
            return {
                "width": width,
                "height": height,
                "mime_type": mime_type,
            }
        except UnidentifiedImageError:
            raise ValidationError("The uploaded file is not a valid image or is corrupted.")

    @staticmethod
    def upload_original_image(
        user_id: uuid.UUID,
        item_id: uuid.UUID,
        file_obj: IO[bytes],
        mime_type: str,
    ) -> str:
        """Upload an image to Supabase Storage.

        Constructs the strict path: users/{userId}/wardrobe/{itemId}/original.{ext}

        Args:
            user_id: The owner of the image.
            item_id: The wardrobe item ID.
            file_obj: The file stream.
            mime_type: The validated mime type.

        Returns:
            The public URL of the uploaded image.
        """
        ext = "jpg"
        if mime_type == "image/png":
            ext = "png"
        elif mime_type == "image/webp":
            ext = "webp"

        path = f"users/{user_id}/wardrobe/{item_id}/original.{ext}"

        file_obj.seek(0)
        file_bytes = file_obj.read()

        # Upload to Supabase
        supabase.storage.from_(settings.supabase_bucket).upload(
            path=path,
            file=file_bytes,
            file_options={"content-type": mime_type, "x-upsert": "true"}
        )

        # Get public URL
        public_url = supabase.storage.from_(settings.supabase_bucket).get_public_url(path)
        return public_url

    @staticmethod
    def upload_profile_picture(
        user_id: uuid.UUID,
        file_obj: IO[bytes],
        mime_type: str,
    ) -> str:
        """Upload a profile picture to Supabase Storage.

        Constructs the path: users/{userId}/profile_picture.{ext}

        Args:
            user_id: The owner of the image.
            file_obj: The file stream.
            mime_type: The validated mime type.

        Returns:
            The public URL of the uploaded image with cache-busting timestamp.
        """
        import time
        ext = "jpg"
        if mime_type == "image/png":
            ext = "png"
        elif mime_type == "image/webp":
            ext = "webp"

        path = f"users/{user_id}/profile_picture.{ext}"

        file_obj.seek(0)
        file_bytes = file_obj.read()

        # Upload to Supabase
        supabase.storage.from_(settings.supabase_bucket).upload(
            path=path,
            file=file_bytes,
            file_options={"content-type": mime_type, "x-upsert": "true"}
        )

        # Get public URL and append cache bust
        public_url = supabase.storage.from_(settings.supabase_bucket).get_public_url(path)
        return f"{public_url}?t={int(time.time())}"
