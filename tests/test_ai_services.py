"""Tests for AI services."""

import pytest

from social_video_automation.ai_services.base import ContentRequest, ContentType


class TestContentRequest:
    """Tests for ContentRequest dataclass."""

    def test_create_request(self):
        """Test creating a content request."""
        request = ContentRequest(
            content_type=ContentType.VIDEO_SCRIPT,
            topic="Australian cricket gear",
            platform="instagram",
        )

        assert request.content_type == ContentType.VIDEO_SCRIPT
        assert request.topic == "Australian cricket gear"
        assert request.platform == "instagram"
        assert request.brand_context == {}
        assert request.style_hints == []

    def test_request_with_brand_context(self):
        """Test request with brand context."""
        request = ContentRequest(
            content_type=ContentType.CAPTION,
            topic="New product launch",
            platform="tiktok",
            brand_context={
                "name": "PeterMat",
                "tone": ["sporty", "australian"],
            },
        )

        assert request.brand_context["name"] == "PeterMat"
        assert "sporty" in request.brand_context["tone"]


class TestContentType:
    """Tests for ContentType enum."""

    def test_content_types(self):
        """Test all content types exist."""
        assert ContentType.VIDEO_SCRIPT.value == "video_script"
        assert ContentType.CAPTION.value == "caption"
        assert ContentType.HASHTAGS.value == "hashtags"
        assert ContentType.THUMBNAIL_PROMPT.value == "thumbnail_prompt"
        assert ContentType.CONTENT_IDEA.value == "content_idea"
