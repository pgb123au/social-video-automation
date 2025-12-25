"""Video Manager - Orchestrates video generation services."""

import asyncio
from pathlib import Path

import httpx
import structlog

from social_video_automation.config import get_settings
from social_video_automation.video.base import (
    AspectRatio,
    VideoGenerator,
    VideoRequest,
    VideoResult,
)
from social_video_automation.video.creatomate import CreatomateGenerator
from social_video_automation.video.heygen import HeyGenGenerator

logger = structlog.get_logger()


class VideoManager:
    """Manages video generation across multiple services."""

    PLATFORM_ASPECT_RATIOS = {
        "instagram": AspectRatio.PORTRAIT_9_16,
        "tiktok": AspectRatio.PORTRAIT_9_16,
        "youtube": AspectRatio.PORTRAIT_9_16,  # For Shorts
        "youtube_long": AspectRatio.LANDSCAPE_16_9,
        "facebook": AspectRatio.PORTRAIT_9_16,
    }

    PLATFORM_DURATIONS = {
        "instagram": 30,
        "tiktok": 30,
        "youtube": 60,
        "facebook": 30,
    }

    def __init__(self) -> None:
        self.settings = get_settings()
        self.generators: dict[str, VideoGenerator] = {
            "creatomate": CreatomateGenerator(),
            "heygen": HeyGenGenerator(),
        }
        self.output_dir = Path("output/videos")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def get_available_generators(self) -> list[str]:
        """Get list of available video generators."""
        available = []
        for name, generator in self.generators.items():
            if await generator.is_available():
                available.append(name)
        return available

    async def generate_video(
        self,
        script: str,
        platform: str,
        title: str = "",
        preferred_generator: str | None = None,
        voiceover_text: str | None = None,
        download: bool = True,
    ) -> VideoResult:
        """Generate a video for the specified platform."""
        available = await self.get_available_generators()

        if not available:
            raise RuntimeError("No video generators available. Check API configuration.")

        # Select generator
        if preferred_generator and preferred_generator in available:
            generator_name = preferred_generator
        else:
            # Prefer Creatomate for quick generation, HeyGen for avatar videos
            generator_name = "creatomate" if "creatomate" in available else available[0]

        generator = self.generators[generator_name]

        # Build request with platform-specific settings
        request = VideoRequest(
            script=script,
            platform=platform,
            title=title,
            aspect_ratio=self.PLATFORM_ASPECT_RATIOS.get(
                platform, AspectRatio.PORTRAIT_9_16
            ),
            duration=self.PLATFORM_DURATIONS.get(platform, 30),
            resolution=self._get_resolution_for_aspect(
                self.PLATFORM_ASPECT_RATIOS.get(platform, AspectRatio.PORTRAIT_9_16)
            ),
            voiceover_text=voiceover_text,
            brand_colors=self.settings.brand.colors,
        )

        logger.info(
            "Generating video",
            generator=generator_name,
            platform=platform,
            duration=request.duration,
        )

        result = await generator.generate(request)

        # Download video if requested
        if download and result.video_url:
            local_path = await self._download_video(result)
            result.local_path = local_path

        return result

    async def generate_for_all_platforms(
        self,
        script: str,
        title: str = "",
        voiceover_text: str | None = None,
        platforms: list[str] | None = None,
    ) -> dict[str, VideoResult]:
        """Generate videos for multiple platforms."""
        if platforms is None:
            platforms = self.settings.social.target_platforms

        results = {}
        tasks = [
            self.generate_video(
                script=script,
                platform=platform,
                title=title,
                voiceover_text=voiceover_text,
            )
            for platform in platforms
        ]

        generated = await asyncio.gather(*tasks, return_exceptions=True)

        for platform, result in zip(platforms, generated):
            if isinstance(result, VideoResult):
                results[platform] = result
                logger.info("Video generated", platform=platform, url=result.video_url)
            else:
                logger.error("Video generation failed", platform=platform, error=str(result))

        return results

    def _get_resolution_for_aspect(self, aspect_ratio: AspectRatio) -> str:
        """Get resolution string for aspect ratio."""
        resolutions = {
            AspectRatio.PORTRAIT_9_16: "1080x1920",
            AspectRatio.SQUARE_1_1: "1080x1080",
            AspectRatio.LANDSCAPE_16_9: "1920x1080",
            AspectRatio.PORTRAIT_4_5: "1080x1350",
        }
        return resolutions.get(aspect_ratio, "1080x1920")

    async def _download_video(self, result: VideoResult) -> Path:
        """Download video to local storage."""
        filename = f"{result.video_id}.{result.format.value}"
        local_path = self.output_dir / filename

        async with httpx.AsyncClient() as client:
            response = await client.get(result.video_url, follow_redirects=True)
            response.raise_for_status()

            with open(local_path, "wb") as f:
                f.write(response.content)

        logger.info("Video downloaded", path=str(local_path))
        return local_path
