"""
Velour API — Recommendation Generator.

The core coordinator that builds combinations, applies rules, scores them,
and ranks the final output.
"""

import itertools
from typing import List, Tuple

from app.models.enums import Category
from app.models.wardrobe import WardrobeItem
from app.recommendations.context import RecommendationContext
from app.recommendations.rules import RuleEngine
from app.recommendations.scoring import ScoringEngine


class OutfitRecommendationResult:
    def __init__(
        self, 
        items: List[WardrobeItem], 
        overall_score: float, 
        scores: dict[str, float], 
        reasons: List[str]
    ):
        self.items = items
        self.overall_score = overall_score
        self.scores = scores
        self.reasons = reasons


class RecommendationGenerator:
    """Generates outfit combinations using deterministic rules and scoring."""

    @staticmethod
    def generate(
        wardrobe: List[WardrobeItem], 
        context: RecommendationContext,
        max_results: int = 5
    ) -> List[OutfitRecommendationResult]:
        """Generate the top ranked outfits for a given wardrobe and context."""
        
        # 1. First Pass Filter: Remove completely invalid items based on season/weather
        valid_items = RuleEngine.filter_valid_items(wardrobe, context)
        
        # 2. Segregate by category
        tops = [i for i in valid_items if i.category == Category.TOPS]
        bottoms = [i for i in valid_items if i.category == Category.BOTTOMS]
        outerwear = [i for i in valid_items if i.category == Category.OUTERWEAR]
        
        # Also support one-piece items (dresses/jumpsuits)
        one_pieces = [i for i in valid_items if i.category == Category.DRESSES]
        
        combinations: List[List[WardrobeItem]] = []
        
        # Build Top + Bottom (+ Optional Outerwear)
        for t in tops:
            for b in bottoms:
                if RuleEngine.is_valid_combination(t, b):
                    combinations.append([t, b])
                    # Add outerwear variant
                    for o in outerwear:
                        combinations.append([t, b, o])
                        
        # Build One-Piece (+ Optional Outerwear)
        for op in one_pieces:
            combinations.append([op])
            for o in outerwear:
                combinations.append([op, o])
                
        # 3. Score all combinations
        scored_results = []
        for combo in combinations:
            overall, scores, reasons = ScoringEngine.evaluate_outfit(combo, context)
            scored_results.append(OutfitRecommendationResult(combo, overall, scores, reasons))
            
        # 4. Rank and truncate
        scored_results.sort(key=lambda x: x.overall_score, reverse=True)
        return scored_results[:max_results]
