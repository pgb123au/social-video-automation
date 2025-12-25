"""Base classes for social media posting."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path


class SocialPlatform(str, Enum):
    """Supported social media platforms."""

    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    THREADS = "threads"
    PINTEREST = "pinterest"


@dataclass
class PostRequest:
    """Request for social media post."""

    platforms: list[SocialPlatform]
    caption: str
    hashtags: list[str] = field(default_factory=list)

    # Media
    video_url: str | None = None
    video_path: Path | None = None
    image_urls: list[str] = field(default_factory=list)
    image_paths: list[Path] = field(default_factory=list)

    # Scheduling
    scheduled_time: datetime | None = None  # None = post immediately
    timezone: str = "Australia/Melbourne"

    # Platform-specific options
    instagram_options: dict = field(default_factory=dict)
    tiktok_options: dict = field(default_factory=dict)
    youtube_options: dict = field(default_factory=dict)
    facebook_options: dict = field(default_factory=dict)

    @property
    def full_caption(self) -> str:
        """Get caption with hashtags appended."""
        if not self.hashtags:
            return self.caption
        hashtag_str = " ".join(f"#{tag.lstrip('#')}" for tag in self.hashtags)
        return f"{self.caption}\n\n{hashtag_str}"


@dataclass
class PostResult:
    """Result from posting to social media."""

    platform: SocialPlatform
    success: bool
    post_id: str | None = None
    post_url: str | None = None
    error: str | None = None
    scheduled: bool = False
    scheduled_time: datetime | None = None
    metadata: dict = field(default_factory=dict)


class SocialPoster(ABC):
    """Abstract base class for social media posters."""

    poster_name: str = "base"

    @abstractmethod
    async def post(self, request: PostRequest) -> list[PostResult]:
        """Post content to social media platforms."""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the poster is available and configured."""
        pass

    @abstractmethod
    async def get_connected_accounts(self) -> list[dict]:
        """Get list of connected social media accounts."""
        pass

    @abstractmethod
    async def get_post_analytics(self, post_id: str, platform: SocialPlatform) -> dict:
        """Get analytics for a specific post."""
        pass
