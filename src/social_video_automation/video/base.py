"""Base classes for video generation."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class VideoFormat(str, Enum):
    """Supported video formats."""

    MP4 = "mp4"
    MOV = "mov"
    WEBM = "webm"


class AspectRatio(str, Enum):
    """Common social media aspect ratios."""

    PORTRAIT_9_16 = "9:16"  # TikTok, Reels, Shorts
    SQUARE_1_1 = "1:1"  # Instagram Feed
    LANDSCAPE_16_9 = "16:9"  # YouTube
    PORTRAIT_4_5 = "4:5"  # Instagram Feed


@dataclass
class VideoRequest:
    """Request for video generation."""

    script: str
    platform: str
    title: str = ""
    aspect_ratio: AspectRatio = AspectRatio.PORTRAIT_9_16
    duration: int = 30  # seconds
    resolution: str = "1080x1920"
    fps: int = 30
    format: VideoFormat = VideoFormat.MP4

    # Visual elements
    background_music: str | None = None
    voiceover_text: str | None = None
    voiceover_voice: str = "default"
    brand_colors: dict[str, str] = field(default_factory=dict)
    logo_url: str | None = None

    # Template-based options
    template_id: str | None = None
    template_variables: dict = field(default_factory=dict)

    # AI-generated visuals
    image_prompts: list[str] = field(default_factory=list)


@dataclass
class VideoResult:
    """Result from video generation."""

    video_url: str
    video_id: str
    duration: float
    format: VideoFormat
    resolution: str
    file_size: int | None = None
    thumbnail_url: str | None = None
    local_path: Path | None = None
    metadata: dict = field(default_factory=dict)
    generator: str = ""


class VideoGenerator(ABC):
    """Abstract base class for video generators."""

    generator_name: str = "base"

    @abstractmethod
    async def generate(self, request: VideoRequest) -> VideoResult:
        """Generate a video from the request."""
        pass

    @abstractmethod
    async def get_status(self, video_id: str) -> dict:
        """Get the status of a video generation job."""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the generator is available and configured."""
        pass

    @abstractmethod
    async def list_templates(self) -> list[dict]:
        """List available video templates."""
        pass
