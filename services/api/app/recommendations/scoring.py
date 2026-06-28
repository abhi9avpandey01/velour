"""
Velour API — Scoring Engine.

Calculates numerical scores for valid outfit combinations based on
color harmony, occasion matching, and user preferences.
"""

from typing import List, Tuple

from app.models.wardrobe import WardrobeItem
from app.recommendations.context import RecommendationContext

# Configurable weights (could be moved to database or settings later)
WEIGHTS = {
    "color_harmony": 0.25,
    "occasion": 0.35,
    "weather": 0.25,
    "preferences": 0.10,
    "recency": 0.05,
}

class ScoringEngine:
    """Evaluates valid outfits and generates explainable scores."""

    @staticmethod
    def _score_color_harmony(items: List[WardrobeItem], explanations: List[str]) -> float:
        """Score based on basic color rules (monochrome, complementary).
        
        Since true color matching requires computer vision (which we store in AI Metadata),
        this baseline engine relies on string matching the 'color' column.
        """
        colors = [i.color.lower() for i in items if i.color]
        if not colors:
            return 50.0  # Neutral score if no colors defined
            
        unique_colors = set(colors)
        
        # Monochrome is safe
        if len(unique_colors) == 1:
            explanations.append("Features a clean, monochromatic color scheme.")
            return 90.0
            
        # Lots of colors usually clash unless styled well
        if len(unique_colors) > 3:
            explanations.append("Uses a highly vibrant, multi-color palette.")
            return 40.0
            
        explanations.append("Uses a balanced color palette.")
        return 75.0

    @staticmethod
    def _score_occasion(items: List[WardrobeItem], context: RecommendationContext, explanations: List[str]) -> float:
        """Score how well the items match the target occasion."""
        matches = [1 for i in items if i.occasion == context.occasion]
        score = (len(matches) / len(items)) * 100.0
        
        if score > 80:
            explanations.append(f"Perfectly matches the {context.occasion.value.lower()} occasion.")
        elif score > 40:
            explanations.append(f"Suitable for a {context.occasion.value.lower()} setting.")
            
        return score

    @staticmethod
    def _score_preferences(items: List[WardrobeItem], context: RecommendationContext, explanations: List[str]) -> float:
        """Boost score if items are marked as user favorites."""
        if not context.prefer_favorites:
            return 50.0
            
        favorites = [1 for i in items if i.is_favorite]
        if favorites:
            explanations.append(f"Includes {len(favorites)} of your favorite pieces.")
            return 100.0
            
        return 50.0

    @staticmethod
    def _score_recency(items: List[WardrobeItem], context: RecommendationContext, explanations: List[str]) -> float:
        """Penalize outfits that contain items worn recently."""
        recent_count = sum(1 for i in items if i.id in context.recently_worn_item_ids)
        
        if recent_count > 0:
            explanations.append("Features items you've worn recently.")
            return max(0.0, 100.0 - (recent_count * 30.0))
            
        explanations.append("Provides a fresh look you haven't worn recently.")
        return 100.0

    @classmethod
    def evaluate_outfit(
        cls, 
        items: List[WardrobeItem], 
        context: RecommendationContext
    ) -> Tuple[float, dict[str, float], List[str]]:
        """Calculate the final weighted score and generate explanations.
        
        Returns:
            Tuple of (overall_score, component_scores_dict, explanations_list)
        """
        explanations: List[str] = []
        
        c_harmony = cls._score_color_harmony(items, explanations)
        c_occasion = cls._score_occasion(items, context, explanations)
        c_weather = 100.0  # Assumes RuleEngine already strictly filtered out invalid weather items
        c_prefs = cls._score_preferences(items, context, explanations)
        c_recency = cls._score_recency(items, context, explanations)
        
        overall_score = (
            (c_harmony * WEIGHTS["color_harmony"]) +
            (c_occasion * WEIGHTS["occasion"]) +
            (c_weather * WEIGHTS["weather"]) +
            (c_prefs * WEIGHTS["preferences"]) +
            (c_recency * WEIGHTS["recency"])
        )
        
        scores = {
            "score_color_harmony": c_harmony,
            "score_occasion": c_occasion,
            "score_weather": c_weather,
            "score_preferences": c_prefs,
            "score_recency": c_recency,
        }
        
        # Deduplicate explanations
        explanations = list(dict.fromkeys(explanations))
        
        return round(overall_score, 2), scores, explanations
