"""
Velour API — Unified AI Service using Google Gemini.

Handles vision extraction and outfit recommendation.
"""

import base64
import io
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

import httpx
from PIL import Image

from app.core.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """Reusable service for interacting with Google Gemini."""

    def __init__(self) -> None:
        if not settings.gemini_api_key or settings.gemini_api_key == "gemini-placeholder":
            logger.warning("Gemini API key is missing or set to placeholder.")
        
        # We use gemini-2.5-flash which supports both vision and text tasks well and has free tier quota.
        self.model_name = "gemini-2.5-flash"
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"
        
        # Determine paths to prompt files relative to this file
        base_dir = Path(__file__).parent.parent
        self.analyze_prompt_path = base_dir / "prompts" / "analyze_clothing.txt"
        self.recommend_prompt_path = base_dir / "prompts" / "recommend_outfit.txt"

    def _load_prompt(self, path: Path) -> str:
        """Load prompt text from a file."""
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {path}")
        return path.read_text(encoding="utf-8")

    def _parse_and_validate_json(self, text: str, required_keys: List[str]) -> Dict[str, Any]:
        """Strip markdown formatting if present and parse JSON."""
        # Sometimes Gemini wraps JSON in ```json ... ```
        clean_text = text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        
        parsed = json.loads(clean_text.strip())
        
        # Basic validation
        for key in required_keys:
            if key not in parsed:
                raise ValueError(f"Missing required key in Gemini response: {key}")
                
        return parsed

    def analyzeClothing(self, image_bytes: bytes) -> Dict[str, Any]:
        """Analyze an image of clothing and extract attributes.
        
        Returns validated JSON with {category, color, pattern, style, description, confidence}.
        Retries once on malformed JSON.
        """
        prompt = self._load_prompt(self.analyze_prompt_path)
        
        try:
            image = Image.open(io.BytesIO(image_bytes))
            # Convert to RGB to avoid issues with alpha channels in some models
            if image.mode != "RGB":
                image = image.convert("RGB")
        except Exception as e:
            logger.error(f"Failed to load image for analysis: {e}")
            raise ValueError("Invalid image bytes provided.") from e

        # Base64 encode the JPEG image
        try:
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG")
            img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        except Exception as e:
            logger.error(f"Failed to convert image to JPEG: {e}")
            raise ValueError("Could not process image.") from e

        required_keys = ["category", "subcategory", "color", "pattern", "style", "description", "confidence"]
        
        for attempt in range(2):
            try:
                payload = {
                    "contents": [
                        {
                            "parts": [
                                {"text": prompt},
                                {
                                    "inlineData": {
                                        "mimeType": "image/jpeg",
                                        "data": img_b64
                                    }
                                }
                            ]
                        }
                    ],
                    "generationConfig": {
                        "responseMimeType": "application/json",
                        "temperature": 0.0
                    }
                }
                
                response = httpx.post(
                    self.api_url,
                    params={"key": settings.gemini_api_key},
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                response_json = response.json()
                
                if "candidates" not in response_json or not response_json["candidates"]:
                    raise ValueError(f"Empty response candidates from Gemini: {response_json}")
                    
                candidate = response_json["candidates"][0]
                if "content" not in candidate or "parts" not in candidate["content"] or not candidate["content"]["parts"]:
                    raise ValueError(f"No content parts in candidate: {candidate}")
                    
                response_text = candidate["content"]["parts"][0].get("text", "")
                if not response_text:
                    raise ValueError("Empty text response from Gemini.")
                    
                validated_data = self._parse_and_validate_json(response_text, required_keys)
                
                # Store only normalized data
                normalized = {
                    "category": str(validated_data["category"]).strip().title(),
                    "subcategory": str(validated_data["subcategory"]).strip().title(),
                    "color": str(validated_data["color"]).strip().lower(),
                    "pattern": str(validated_data["pattern"]).strip().lower(),
                    "style": str(validated_data["style"]).strip().title(),
                    "description": str(validated_data["description"]).strip(),
                    "confidence": float(validated_data["confidence"]),
                    "outfit_suggestions": str(validated_data.get("outfit_suggestions", "")).strip(),
                    "model_version": self.model_name
                }
                return normalized
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to parse or validate Gemini vision response (Attempt {attempt + 1}/2): {e}")
                if attempt == 1:
                    logger.error("Final attempt failed. Returning fallback data.", exc_info=True)
                    return {
                        "category": "Unknown",
                        "subcategory": "Unknown",
                        "color": "unknown",
                        "pattern": "unknown",
                        "style": "Unknown",
                        "description": "Error analyzing image",
                        "confidence": 0.0,
                        "outfit_suggestions": "Unable to generate outfit suggestions due to an error.",
                        "model_version": self.model_name
                    }
            except Exception as e:
                logger.error(f"Unexpected error calling Gemini API: {e}", exc_info=True)
                raise

        raise RuntimeError("Unreachable")

    def recommendOutfit(self, userRequest: str, wardrobe: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Recommend an outfit from the provided wardrobe based on the user's request.
        
        Returns validated JSON with {top_id, bottom_id, shoe_id, reason}.
        Retries once on malformed JSON.
        """
        prompt = self._load_prompt(self.recommend_prompt_path)
        
        wardrobe_json = json.dumps(wardrobe, indent=2)
        
        full_prompt = f"{prompt}\n\nUSER REQUEST:\n{userRequest}\n\nWARDROBE:\n{wardrobe_json}"
        
        required_keys = ["top_id", "bottom_id", "shoe_id", "reason"]
        
        for attempt in range(2):
            try:
                payload = {
                    "contents": [
                        {
                            "parts": [
                                {"text": full_prompt}
                            ]
                        }
                    ],
                    "generationConfig": {
                        "responseMimeType": "application/json",
                        "temperature": 0.2
                    }
                }
                
                response = httpx.post(
                    self.api_url,
                    params={"key": settings.gemini_api_key},
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                response_json = response.json()
                
                if "candidates" not in response_json or not response_json["candidates"]:
                    raise ValueError(f"Empty response candidates from Gemini: {response_json}")
                    
                candidate = response_json["candidates"][0]
                if "content" not in candidate or "parts" not in candidate["content"] or not candidate["content"]["parts"]:
                    raise ValueError(f"No content parts in candidate: {candidate}")
                    
                response_text = candidate["content"]["parts"][0].get("text", "")
                if not response_text:
                    raise ValueError("Empty text response from Gemini.")
                    
                validated_data = self._parse_and_validate_json(response_text, required_keys)
                
                # Store only normalized data
                normalized = {
                    "top_id": str(validated_data["top_id"]),
                    "bottom_id": str(validated_data["bottom_id"]),
                    "shoe_id": str(validated_data["shoe_id"]),
                    "reason": str(validated_data["reason"]).strip()
                }
                return normalized
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to parse or validate Gemini recommendation response (Attempt {attempt + 1}/2): {e}")
                if attempt == 1:
                    logger.error("Final attempt failed for outfit recommendation.", exc_info=True)
                    raise RuntimeError("Failed to generate outfit recommendation.") from e
            except Exception as e:
                logger.error(f"Unexpected error calling Gemini API for recommendation: {e}", exc_info=True)
                raise
                
        raise RuntimeError("Unreachable")

