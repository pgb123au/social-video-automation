"""Tests for video generation."""

import pytest

from social_video_automation.video.base import (
    AspectRatio,
    VideoFormat,
    VideoRequest,
)


class TestVideoRequest:
    """Tests for VideoRequest dataclass."""

    def test_default_values(self):
        """Test default values for video request."""
        request = VideoRequest(
            script="Test script",
            platform="instagram",
        )

        assert request.script == "Test script"
        assert request.platform == "instagram"
        assert request.aspect_ratio == AspectRatio.PORTRAIT_9_16
        assert request.duration == 30
        assert request.fps == 30
        assert request.format == VideoFormat.MP4

    def test_custom_values(self):
        """Test custom values for video request."""
        request = VideoRequest(
            script="Test script",
            platform="youtube",
            aspect_ratio=AspectRatio.LANDSCAPE_16_9,
            duration=60,
            resolution="1920x1080",
        )

        assert request.aspect_ratio == AspectRatio.LANDSCAPE_16_9
        assert request.duration == 60
        assert request.resolution == "1920x1080"


class TestAspectRatio:
    """Tests for AspectRatio enum."""

    def test_aspect_ratios(self):
        """Test aspect ratio values."""
        assert AspectRatio.PORTRAIT_9_16.value == "9:16"
        assert AspectRatio.SQUARE_1_1.value == "1:1"
        assert AspectRatio.LANDSCAPE_16_9.value == "16:9"
        assert AspectRatio.PORTRAIT_4_5.value == "4:5"


class TestVideoFormat:
    """Tests for VideoFormat enum."""

    def test_formats(self):
        """Test video format values."""
        assert VideoFormat.MP4.value == "mp4"
        assert VideoFormat.MOV.value == "mov"
        assert VideoFormat.WEBM.value == "webm"
