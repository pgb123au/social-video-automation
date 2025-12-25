"""Tests for social media posting."""

import pytest

from social_video_automation.social.base import (
    PostRequest,
    SocialPlatform,
)


class TestPostRequest:
    """Tests for PostRequest dataclass."""

    def test_create_request(self):
        """Test creating a post request."""
        request = PostRequest(
            platforms=[SocialPlatform.INSTAGRAM, SocialPlatform.TIKTOK],
            caption="Check out our new gear!",
        )

        assert len(request.platforms) == 2
        assert SocialPlatform.INSTAGRAM in request.platforms
        assert request.caption == "Check out our new gear!"

    def test_full_caption_without_hashtags(self):
        """Test full caption without hashtags."""
        request = PostRequest(
            platforms=[SocialPlatform.INSTAGRAM],
            caption="Test caption",
        )

        assert request.full_caption == "Test caption"

    def test_full_caption_with_hashtags(self):
        """Test full caption with hashtags."""
        request = PostRequest(
            platforms=[SocialPlatform.INSTAGRAM],
            caption="Test caption",
            hashtags=["australian", "sports", "#cricket"],
        )

        full = request.full_caption
        assert "Test caption" in full
        assert "#australian" in full
        assert "#sports" in full
        assert "#cricket" in full

    def test_request_with_video(self):
        """Test request with video URL."""
        request = PostRequest(
            platforms=[SocialPlatform.YOUTUBE],
            caption="New video!",
            video_url="https://example.com/video.mp4",
            youtube_options={"title": "My Video Title"},
        )

        assert request.video_url == "https://example.com/video.mp4"
        assert request.youtube_options["title"] == "My Video Title"


class TestSocialPlatform:
    """Tests for SocialPlatform enum."""

    def test_platforms(self):
        """Test platform values."""
        assert SocialPlatform.INSTAGRAM.value == "instagram"
        assert SocialPlatform.TIKTOK.value == "tiktok"
        assert SocialPlatform.YOUTUBE.value == "youtube"
        assert SocialPlatform.FACEBOOK.value == "facebook"
        assert SocialPlatform.TWITTER.value == "twitter"
        assert SocialPlatform.LINKEDIN.value == "linkedin"
