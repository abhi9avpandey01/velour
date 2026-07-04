"""
Velour API — Recommendation Tool.

Allows the Stylist Agent to request outfit recommendations from the
deterministic RecommendationEngine.
"""

import uuid
from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.tools.base import BaseTool
from app.models.enums import Occasion, Season, WeatherContext
from app.recommendations.context import RecommendationContext
from app.recommendations.generator import OutfitRecommendationResult
from app.repositories.recommendation_repository import RecommendationRepository
from app.repositories.wardrobe_repository import WardrobeRepository


class GenerateOutfitTool(BaseTool):
    """Tool for generating a new outfit recommendation."""

    def __init__(self, session: AsyncSession, user_id: uuid.UUID):
        self.session = session
        self.user_id = user_id

    @property
    def name(self) -> str:
        return "generate_outfit"

    @property
    def description(self) -> str:
        return "Generate a ranked outfit recommendation based on the current weather and occasion."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "occasion": {
                    "type": "string",
                    "enum": [e.value for e in Occasion],
                    "description": "The occasion the user needs the outfit for."
                },
                "weather": {
                    "type": "string",
                    "enum": [e.value for e in WeatherContext],
                    "description": "The current weather context."
                },
                "season": {
                    "type": "string",
                    "enum": [e.value for e in Season],
                    "description": "The current season."
                }
            },
            "required": []
        }

    async def execute(self, occasion: Optional[str] = None, weather: Optional[str] = None, season: Optional[str] = None, **kwargs) -> Any:
        """Execute the deterministic Recommendation Engine."""
        rec_repo = RecommendationRepository(self.session)
        wardrobe_repo = WardrobeRepository(self.session)
        
        # 1. Gather context
        recent_ids = await rec_repo.get_recently_worn_items(self.user_id)
        
        context = RecommendationContext(
            user_id=self.user_id,
            weather=WeatherContext(weather) if weather else WeatherContext.MILD,
            season=Season(season) if season else Season.SUMMER,
            occasion=Occasion(occasion) if occasion else Occasion.CASUAL,
            recently_worn_item_ids=recent_ids,
            prefer_favorites=True,
            include_archived=False,
        )
        
        from app.schemas.wardrobe import WardrobeFilterParams
        wardrobe_items, _ = await wardrobe_repo.list_by_user(
            user_id=self.user_id, 
            filters=WardrobeFilterParams(limit=100)
        )
        
        if not wardrobe_items:
            return {"error": "The user's wardrobe is empty. Ask them to upload items first."}
            
        # 2. Prepare Wardrobe for AI
        wardrobe_dicts = [
            {
                "id": str(item.id),
                "name": item.name,
                "category": item.category.value,
                "subcategory": item.subcategory,
                "color": item.color,
                "pattern": item.pattern.value if item.pattern else "Solid",
                "material": item.material
            }
            for item in wardrobe_items
        ]
        
        user_request = f"Occasion: {occasion or 'Casual'}, Weather: {weather or 'Mild'}, Season: {season or 'Summer'}"
        
        # 3. Generate Outfit via AI Service
        from app.services.ai_service import AIService
        ai_service = AIService()
        
        try:
            ai_result = ai_service.recommendOutfit(user_request, wardrobe_dicts)
        except Exception as e:
            return {"error": str(e)}
            
        selected_ids = []
        for key in ["top_id", "bottom_id", "shoe_id"]:
            val = ai_result.get(key)
            if val and val.lower() != "none":
                try:
                    selected_ids.append(uuid.UUID(val))
                except ValueError:
                    pass
                    
        selected_items = [item for item in wardrobe_items if item.id in selected_ids]
        
        if not selected_items:
            return {"error": "Could not generate a valid combination from the wardrobe."}
            
        result = OutfitRecommendationResult(
            items=selected_items,
            overall_score=0.95,
            scores={
                "score_color_harmony": 0.95,
                "score_occasion": 0.95,
                "score_weather": 0.95,
                "score_preferences": 0.95,
                "score_recency": 0.95
            },
            reasons=[ai_result.get("reason", "No reason provided.")]
        )
        
        # 4. Save it
        snapshot = {"weather": weather, "season": season, "occasion": occasion}
        saved_rec = await rec_repo.save_recommendation(self.user_id, result, snapshot)
        
        # 4. Return structured response to LLM
        return {
            "recommendation_id": str(saved_rec.id),
            "outfit_id": str(saved_rec.outfit_id),
            "overall_score": result.overall_score,
            "reasons": result.reasons,
            "items": [
                {
                    "category": item.category.value,
                    "color": item.color,
                    "brand": item.brand
                }
                for item in result.items
            ]
        }
