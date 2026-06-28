"""
Velour API — Recommendation Repository.

Handles database transactions for saving generated outfits,
persisting recommendation scores, and updating history.
"""

import uuid
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.enums import RecommendationAction
from app.models.recommendation import Outfit, OutfitItem, Recommendation, RecommendationHistory
from app.recommendations.generator import OutfitRecommendationResult


class RecommendationRepository:
    """Repository for persisting generated recommendations to the DB."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_recommendation(
        self, 
        user_id: uuid.UUID, 
        result: OutfitRecommendationResult,
        context_snapshot: dict
    ) -> Recommendation:
        """Save a generated outfit and its recommendation scores.
        
        This implicitly creates an `Outfit` (is_user_created=False), links the 
        items, and then creates the `Recommendation` tracker.
        """
        # 1. Create the Outfit
        outfit = Outfit(
            id=uuid.uuid4(),
            user_id=user_id,
            name="Generated Outfit",
            is_user_created=False
        )
        self.session.add(outfit)
        
        # 2. Add the Items
        for item in result.items:
            outfit_item = OutfitItem(
                id=uuid.uuid4(),
                outfit_id=outfit.id,
                wardrobe_item_id=item.id
            )
            self.session.add(outfit_item)
            
        # 3. Save the Recommendation
        rec = Recommendation(
            id=uuid.uuid4(),
            user_id=user_id,
            outfit_id=outfit.id,
            score_color_harmony=result.scores["score_color_harmony"],
            score_occasion=result.scores["score_occasion"],
            score_weather=result.scores["score_weather"],
            score_preferences=result.scores["score_preferences"],
            score_recency=result.scores["score_recency"],
            overall_score=result.overall_score,
            reasons=result.reasons,
            context_snapshot=context_snapshot
        )
        self.session.add(rec)
        
        # 4. Save Initial History (GENERATED)
        history = RecommendationHistory(
            id=uuid.uuid4(),
            recommendation_id=rec.id,
            action=RecommendationAction.GENERATED
        )
        self.session.add(history)
        
        await self.session.commit()
        await self.session.refresh(rec)
        return rec

    async def record_action(self, recommendation_id: uuid.UUID, action: RecommendationAction) -> None:
        """Record a user action (e.g. ACCEPTED) on a recommendation."""
        history = RecommendationHistory(
            id=uuid.uuid4(),
            recommendation_id=recommendation_id,
            action=action
        )
        self.session.add(history)
        await self.session.commit()

    async def get_recently_worn_items(self, user_id: uuid.UUID, limit: int = 20) -> List[uuid.UUID]:
        """Fetch WardrobeItem IDs that were worn recently by querying history."""
        stmt = (
            select(OutfitItem.wardrobe_item_id)
            .join(Outfit, Outfit.id == OutfitItem.outfit_id)
            .join(Recommendation, Recommendation.outfit_id == Outfit.id)
            .join(RecommendationHistory, RecommendationHistory.recommendation_id == Recommendation.id)
            .where(
                Outfit.user_id == user_id,
                RecommendationHistory.action == RecommendationAction.WORN
            )
            .order_by(RecommendationHistory.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
