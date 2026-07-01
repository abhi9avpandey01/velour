import asyncio
import io
import json
from PIL import Image

from app.services.ai_service import AIService
from app.core.config import settings

def test_ai():
    print("Initializing AIService...")
    print(f"Loaded Gemini Key: {'[SET]' if settings.gemini_api_key and settings.gemini_api_key != 'gemini-placeholder' else '[NOT SET]'}")
    
    ai_service = AIService()
    
    # Test 1: recommendOutfit
    print("\n--- Testing recommendOutfit ---")
    dummy_wardrobe = [
        {"id": "11111111-1111-1111-1111-111111111111", "category": "Tops", "color": "white", "style": "casual", "name": "White T-Shirt"},
        {"id": "22222222-2222-2222-2222-222222222222", "category": "Bottoms", "color": "blue", "style": "casual", "name": "Blue Jeans"},
        {"id": "33333333-3333-3333-3333-333333333333", "category": "Shoes", "color": "black", "style": "casual", "name": "Black Sneakers"}
    ]
    user_request = "I need something casual for a sunny day."
    
    try:
        rec_result = ai_service.recommendOutfit(user_request, dummy_wardrobe)
        print("Recommendation Success!")
        print(json.dumps(rec_result, indent=2))
    except Exception as e:
        print(f"Recommendation Failed: {e}")

    # Test 2: analyzeClothing
    print("\n--- Testing analyzeClothing ---")
    try:
        # Create a dummy solid blue image
        img = Image.new('RGB', (200, 200), color = 'blue')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes = img_bytes.getvalue()
        
        vision_result = ai_service.analyzeClothing(img_bytes)
        print("Vision Extraction Success!")
        print(json.dumps(vision_result, indent=2))
    except Exception as e:
        print(f"Vision Extraction Failed: {e}")

if __name__ == "__main__":
    test_ai()
