"""
Velour API — Recommendations Endpoints.

REST APIs for generating and tracking outfit recommendations.
"""

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_recommendation_repository, get_wardrobe_repository
from app.db.session import get_db_session
from app.models.enums import RecommendationAction
from app.models.user import User
from app.recommendations.context import RecommendationContext
from app.recommendations.generator import RecommendationGenerator
from app.repositories.recommendation_repository import RecommendationRepository
from app.repositories.wardrobe_repository import WardrobeRepository
from app.schemas.common import ApiResponse
from app.schemas.recommendations import GenerateRecommendationsRequest, RecommendationResponse

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.post(
    "/generate",
    response_model=ApiResponse[List[RecommendationResponse]],
    summary="Generate deterministic outfit recommendations",
)
async def generate_recommendations(
    request: GenerateRecommendationsRequest,
    current_user: User = Depends(get_current_user),
    rec_repo: RecommendationRepository = Depends(get_recommendation_repository),
    wardrobe_repo: WardrobeRepository = Depends(get_wardrobe_repository),
) -> ApiResponse[List[RecommendationResponse]]:
    """Generates a list of outfit recommendations based on rules and context."""
    # 1. Fetch recently worn items to penalize them
    recent_ids = await rec_repo.get_recently_worn_items(current_user.id)
    
    # 2. Build the engine context
    context = RecommendationContext(
        user_id=current_user.id,
        weather=request.weather,
        temperature_celsius=request.temperature_celsius,
        season=request.season,
        occasion=request.occasion,
        prefer_favorites=request.prefer_favorites,
        include_archived=request.include_archived,
        recently_worn_item_ids=recent_ids,
    )
    
    # 3. Fetch the full wardrobe
    wardrobe_items = await wardrobe_repo.list_by_user(
        user_id=current_user.id,
        limit=1000 # Assume reasonable max for deterministic combinatorics
    )
    
    if not wardrobe_items:
        raise HTTPException(status_code=400, detail="Wardrobe is empty.")
    
    # 4. Generate & Score
    generator_results = RecommendationGenerator.generate(wardrobe_items, context)
    
    if not generator_results:
        raise HTTPException(status_code=404, detail="No valid combinations found for this context.")
    
    # 5. Persist the generated recommendations
    responses = []
    for res in generator_results:
        saved_rec = await rec_repo.save_recommendation(
            user_id=current_user.id,
            result=res,
            context_snapshot=request.model_dump(mode="json")
        )
        # Manually construct response to include relationships if needed
        responses.append(RecommendationResponse.model_validate(saved_rec))
        
    return ApiResponse.ok(responses)


@router.post(
    "/{recommendation_id}/accept",
    response_model=ApiResponse[dict],
    summary="Accept a recommendation",
)
async def accept_recommendation(
    recommendation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    repo: RecommendationRepository = Depends(get_recommendation_repository),
) -> ApiResponse[dict]:
    """Records user acceptance of an outfit."""
    # Note: Real implementation should verify recommendation belongs to user
    await repo.record_action(recommendation_id, RecommendationAction.ACCEPTED)
    return ApiResponse.ok({"status": "accepted"})


@router.post(
    "/{recommendation_id}/reject",
    response_model=ApiResponse[dict],
    summary="Reject a recommendation",
)
async def reject_recommendation(
    recommendation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    repo: RecommendationRepository = Depends(get_recommendation_repository),
) -> ApiResponse[dict]:
    """Records user rejection of an outfit."""
    await repo.record_action(recommendation_id, RecommendationAction.REJECTED)
    return ApiResponse.ok({"status": "rejected"})
