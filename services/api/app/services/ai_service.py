"""
Velour API — Unified AI Service using Google Gemini.

Handles vision extraction and outfit recommendation.
"""

import io
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

import google.generativeai as genai
from PIL import Image

from app.core.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """Reusable service for interacting with Google Gemini."""

    def __init__(self) -> None:
        if not settings.gemini_api_key or settings.gemini_api_key == "gemini-placeholder":
            logger.warning("Gemini API key is missing or set to placeholder.")
        
        genai.configure(api_key=settings.gemini_api_key)
        # We use gemini-1.5-pro which supports both vision and text tasks well.
        self.model_name = "gemini-1.5-pro"
        
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

        model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={"response_mime_type": "application/json", "temperature": 0.0}
        )
        
        required_keys = ["category", "color", "pattern", "style", "description", "confidence"]
        
        for attempt in range(2):
            try:
                response = model.generate_content([prompt, image])
                if not response.text:
                    raise ValueError("Empty response from Gemini.")
                    
                validated_data = self._parse_and_validate_json(response.text, required_keys)
                
                # Store only normalized data
                normalized = {
                    "category": str(validated_data["category"]).strip().title(),
                    "color": str(validated_data["color"]).strip().lower(),
                    "pattern": str(validated_data["pattern"]).strip().lower(),
                    "style": str(validated_data["style"]).strip().title(),
                    "description": str(validated_data["description"]).strip(),
                    "confidence": float(validated_data["confidence"]),
                    "model_version": self.model_name
                }
                return normalized
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to parse or validate Gemini vision response (Attempt {attempt + 1}/2): {e}")
                if attempt == 1:
                    logger.error("Final attempt failed. Returning fallback data.", exc_info=True)
                    return {
                        "category": "Unknown",
                        "color": "unknown",
                        "pattern": "unknown",
                        "style": "Unknown",
                        "description": "Error analyzing image",
                        "confidence": 0.0,
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
        
        model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={"response_mime_type": "application/json", "temperature": 0.2}
        )
        
        required_keys = ["top_id", "bottom_id", "shoe_id", "reason"]
        
        for attempt in range(2):
            try:
                response = model.generate_content(full_prompt)
                if not response.text:
                    raise ValueError("Empty response from Gemini.")
                    
                validated_data = self._parse_and_validate_json(response.text, required_keys)
                
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
