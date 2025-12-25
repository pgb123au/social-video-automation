"""HeyGen video generation service for AI avatar videos."""

import asyncio

import httpx
import structlog

from social_video_automation.config import get_settings
from social_video_automation.video.base import (
    VideoFormat,
    VideoGenerator,
    VideoRequest,
    VideoResult,
)

logger = structlog.get_logger()

HEYGEN_API_URL = "https://api.heygen.com/v2"


class HeyGenGenerator(VideoGenerator):
    """Video generator using HeyGen API for AI avatar videos."""

    generator_name = "heygen"

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Lazy-loaded HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=HEYGEN_API_URL,
                headers={
                    "X-Api-Key": self.settings.video.heygen_api_key,
                    "Content-Type": "application/json",
                },
                timeout=60.0,
            )
        return self._client

    async def is_available(self) -> bool:
        """Check if HeyGen is available."""
        if not self.settings.video.heygen_api_key:
            return False
        try:
            response = await self.client.get("/avatars")
            return response.status_code == 200
        except Exception as e:
            logger.warning("HeyGen unavailable", error=str(e))
            return False

    async def list_templates(self) -> list[dict]:
        """List available HeyGen templates."""
        response = await self.client.get("/templates")
        response.raise_for_status()
        data = response.json()
        return data.get("data", {}).get("templates", [])

    async def list_avatars(self) -> list[dict]:
        """List available AI avatars."""
        response = await self.client.get("/avatars")
        response.raise_for_status()
        data = response.json()
        return data.get("data", {}).get("avatars", [])

    async def list_voices(self) -> list[dict]:
        """List available voices."""
        response = await self.client.get("/voices")
        response.raise_for_status()
        data = response.json()
        return data.get("data", {}).get("voices", [])

    async def generate(self, request: VideoRequest) -> VideoResult:
        """Generate AI avatar video using HeyGen."""
        video_data = self._build_video_request(request)

        # Create video
        response = await self.client.post("/video/generate", json=video_data)
        response.raise_for_status()
        result = response.json()

        video_id = result.get("data", {}).get("video_id")
        if not video_id:
            raise RuntimeError("Failed to get video_id from HeyGen response")

        # Wait for completion
        final_result = await self._wait_for_completion(video_id)

        return VideoResult(
            video_url=final_result["video_url"],
            video_id=video_id,
            duration=final_result.get("duration", request.duration),
            format=VideoFormat.MP4,
            resolution=request.resolution,
            thumbnail_url=final_result.get("thumbnail_url"),
            generator=self.generator_name,
            metadata={"heygen_data": final_result},
        )

    def _build_video_request(self, request: VideoRequest) -> dict:
        """Build HeyGen video request."""
        # Parse resolution
        width, height = map(int, request.resolution.split("x"))

        # Build video input
        video_input = {
            "character": {
                "type": "avatar",
                "avatar_id": request.template_variables.get(
                    "avatar_id", "Anna_public_3_20240108"  # Default avatar
                ),
                "avatar_style": "normal",
            },
            "voice": {
                "type": "text",
                "input_text": request.voiceover_text or request.script,
                "voice_id": request.template_variables.get(
                    "voice_id", "1bd001e7e50f421d891986aad5158bc8"  # Default voice
                ),
            },
        }

        # Add background if specified
        if request.brand_colors:
            video_input["background"] = {
                "type": "color",
                "value": request.brand_colors.get("secondary", "#1A1A2E"),
            }

        return {
            "video_inputs": [video_input],
            "dimension": {
                "width": width,
                "height": height,
            },
            "aspect_ratio": request.aspect_ratio.value.replace(":", "x"),
        }

    async def _wait_for_completion(
        self,
        video_id: str,
        timeout: int = 600,  # HeyGen can take longer
        poll_interval: int = 10,
    ) -> dict:
        """Wait for video generation to complete."""
        elapsed = 0
        while elapsed < timeout:
            response = await self.client.get(f"/video_status.get?video_id={video_id}")
            response.raise_for_status()
            result = response.json()

            status = result.get("data", {}).get("status")
            logger.info("HeyGen video status", video_id=video_id, status=status)

            if status == "completed":
                return result.get("data", {})
            elif status == "failed":
                error = result.get("data", {}).get("error")
                raise RuntimeError(f"Video generation failed: {error}")

            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        raise TimeoutError(f"Video {video_id} timed out after {timeout} seconds")

    async def get_status(self, video_id: str) -> dict:
        """Get video generation status."""
        response = await self.client.get(f"/video_status.get?video_id={video_id}")
        response.raise_for_status()
        return response.json().get("data", {})
