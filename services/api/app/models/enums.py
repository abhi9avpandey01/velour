"""
Velour API — Application Enums.

Defines all core enums used across the application.
These are python str enums, ensuring they are stored and serialized as strings.
"""

from enum import Enum


class Category(str, Enum):
    """Primary category for a wardrobe item."""
    TOPS = "Tops"
    BOTTOMS = "Bottoms"
    OUTERWEAR = "Outerwear"
    DRESSES = "Dresses"
    FOOTWEAR = "Footwear"
    ACCESSORIES = "Accessories"


class Season(str, Enum):
    """Season for a wardrobe item."""
    SUMMER = "Summer"
    WINTER = "Winter"
    MONSOON = "Monsoon"
    ALL_SEASON = "AllSeason"


class Occasion(str, Enum):
    """Occasion for a wardrobe item."""
    CASUAL = "Casual"
    FORMAL = "Formal"
    PARTY = "Party"
    SPORTS = "Sports"
    TRAVEL = "Travel"
    BUSINESS = "Business"
    TRADITIONAL = "Traditional"


class Pattern(str, Enum):
    """Pattern or print of a wardrobe item."""
    SOLID = "Solid"
    STRIPED = "Striped"
    CHECKED = "Checked"
    FLORAL = "Floral"
    GRAPHIC = "Graphic"
    PRINTED = "Printed"
    PLAIN = "Plain"


class UploadStatus(str, Enum):
    """Status of the image upload to Supabase."""
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ProcessingStatus(str, Enum):
    """Status of the background image processing (thumbnails, compression)."""
    NOT_STARTED = "NOT_STARTED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AIStatus(str, Enum):
    """Status of the AI classification pipeline."""
    WAITING = "WAITING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class RecommendationAction(str, Enum):
    """Track user feedback on recommendations."""
    GENERATED = "GENERATED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    MODIFIED = "MODIFIED"
    WORN = "WORN"


class WeatherContext(str, Enum):
    """Abstracted weather contexts for rules engine."""
    FREEZING = "Freezing"
    COLD = "Cold"
    MILD = "Mild"
    WARM = "Warm"
    HOT = "Hot"


class PreferenceSource(str, Enum):
    """Source of a user preference."""
    MANUAL = "MANUAL"
    LEARNED = "LEARNED"


class ChangedBy(str, Enum):
    """Actor who changed a preference."""
    USER = "USER"
    AI = "AI"
