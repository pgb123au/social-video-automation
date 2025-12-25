"""Base classes for AI services."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ContentType(str, Enum):
    """Type of content to generate."""

    VIDEO_SCRIPT = "video_script"
    CAPTION = "caption"
    HASHTAGS = "hashtags"
    THUMBNAIL_PROMPT = "thumbnail_prompt"
    CONTENT_IDEA = "content_idea"


@dataclass
class ContentRequest:
    """Request for AI-generated content."""

    content_type: ContentType
    topic: str
    platform: str  # instagram, tiktok, youtube, etc.
    brand_context: dict[str, Any] = field(default_factory=dict)
    max_length: int | None = None
    style_hints: list[str] = field(default_factory=list)
    additional_context: str = ""


@dataclass
class ContentResponse:
    """Response from AI content generation."""

    content: str
    content_type: ContentType
    metadata: dict[str, Any] = field(default_factory=dict)
    ai_service: str = ""
    tokens_used: int = 0


class AIService(ABC):
    """Abstract base class for AI services."""

    service_name: str = "base"

    @abstractmethod
    async def generate_content(self, request: ContentRequest) -> ContentResponse:
        """Generate content based on the request."""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the service is available and configured."""
        pass

    def _build_brand_prompt(self, brand_context: dict[str, Any]) -> str:
        """Build brand-specific prompt context."""
        brand_name = brand_context.get("name", "PeterMat")
        tagline = brand_context.get("tagline", "Born from the land. Built for performance.")
        tone = brand_context.get("tone", ["professional", "sporty", "australian"])

        return f"""
Brand: {brand_name}
Tagline: "{tagline}"
Tone: {', '.join(tone)}
Focus: Australian sporting excellence, quality craftsmanship, authentic Australian experience
"""

    def _build_platform_context(self, platform: str) -> str:
        """Build platform-specific context."""
        contexts = {
            "instagram": "Instagram Reels: Short, engaging, visually striking. Use trending audio cues. 15-60 seconds.",
            "tiktok": "TikTok: Fast-paced, trend-aware, authentic. Hook in first 2 seconds. 15-60 seconds.",
            "youtube": "YouTube Shorts: Educational or entertaining. Clear value proposition. Up to 60 seconds.",
            "facebook": "Facebook Reels: Broader audience, slightly longer form acceptable. 15-90 seconds.",
        }
        return contexts.get(platform, "General social media video content.")
