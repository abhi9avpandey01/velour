"""
Velour API — Rule Engine.

Contains deterministic filter rules to prune invalid outfit combinations 
before scoring them, mitigating combinatorial explosion.
"""

from typing import List

from app.models.enums import Occasion, Season, WeatherContext
from app.models.wardrobe import WardrobeItem
from app.recommendations.context import RecommendationContext


class RuleEngine:
    """Deterministic filter rules to prevent invalid combinations."""

    @staticmethod
    def is_season_appropriate(item: WardrobeItem, context: RecommendationContext) -> bool:
        """Filter out items that completely clash with the current season."""
        if item.season == Season.ALL_SEASON:
            return True
            
        # Strict exclusion: Don't allow winter clothes in summer, and vice versa.
        if context.season == Season.SUMMER and item.season == Season.WINTER:
            return False
        if context.season == Season.WINTER and item.season == Season.SUMMER:
            return False
            
        return True

    @staticmethod
    def is_weather_appropriate(item: WardrobeItem, context: RecommendationContext) -> bool:
        """Filter out items that violate physical weather constraints."""
        # E.g., Heavy jackets in HOT weather.
        category = item.category.value.upper()
        
        if context.weather in [WeatherContext.HOT, WeatherContext.WARM]:
            if category == "OUTERWEAR" and "heavy" in (item.subcategory or "").lower():
                return False
                
        if context.weather in [WeatherContext.FREEZING]:
            if category == "TOPS" and "tank" in (item.subcategory or "").lower():
                # Allow tank tops ONLY if paired with outerwear (handled in combination rules)
                # But as a strict filter for now, we pass it and let combination rules catch it.
                pass
                
        return True

    @staticmethod
    def is_occasion_appropriate(item: WardrobeItem, context: RecommendationContext) -> bool:
        """Filter out extreme occasion mismatches (e.g. tuxedo to gym)."""
        if context.occasion == Occasion.WORKOUT and item.occasion in [Occasion.FORMAL, Occasion.BUSINESS]:
            return False
        if context.occasion == Occasion.FORMAL and item.occasion in [Occasion.WORKOUT, Occasion.LOUNGEWEAR]:
            return False
            
        return True

    @staticmethod
    def is_valid_combination(top: WardrobeItem, bottom: WardrobeItem, outerwear: WardrobeItem | None = None) -> bool:
        """Ensure the combination makes logical sense."""
        # E.g., Cannot wear a dress (which acts as a top AND bottom) WITH pants.
        if top.subcategory and "dress" in top.subcategory.lower():
            return False # Bottoms shouldn't be selected with a dress
            
        return True

    @classmethod
    def filter_valid_items(
        cls, 
        items: List[WardrobeItem], 
        context: RecommendationContext
    ) -> List[WardrobeItem]:
        """Apply all single-item rules to filter the pool."""
        valid_items = []
        for item in items:
            if not context.include_archived and item.is_archived:
                continue
                
            if not cls.is_season_appropriate(item, context):
                continue
                
            if not cls.is_weather_appropriate(item, context):
                continue
                
            if not cls.is_occasion_appropriate(item, context):
                continue
                
            valid_items.append(item)
            
        return valid_items
