"""Creatomate video generation service."""

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

CREATOMATE_API_URL = "https://api.creatomate.com/v1"


class CreatomateGenerator(VideoGenerator):
    """Video generator using Creatomate API."""

    generator_name = "creatomate"

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Lazy-loaded HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=CREATOMATE_API_URL,
                headers={
                    "Authorization": f"Bearer {self.settings.video.creatomate_api_key}",
                    "Content-Type": "application/json",
                },
                timeout=60.0,
            )
        return self._client

    async def is_available(self) -> bool:
        """Check if Creatomate is available."""
        if not self.settings.video.creatomate_api_key:
            return False
        try:
            response = await self.client.get("/templates")
            return response.status_code == 200
        except Exception as e:
            logger.warning("Creatomate unavailable", error=str(e))
            return False

    async def list_templates(self) -> list[dict]:
        """List available Creatomate templates."""
        response = await self.client.get("/templates")
        response.raise_for_status()
        return response.json()

    async def generate(self, request: VideoRequest) -> VideoResult:
        """Generate video using Creatomate."""
        # Build the render request
        render_data = self._build_render_request(request)

        # Start the render job
        response = await self.client.post("/renders", json=render_data)
        response.raise_for_status()
        render_info = response.json()

        render_id = render_info[0]["id"] if isinstance(render_info, list) else render_info["id"]

        # Poll for completion
        result = await self._wait_for_completion(render_id)

        return VideoResult(
            video_url=result["url"],
            video_id=render_id,
            duration=result.get("duration", request.duration),
            format=VideoFormat.MP4,
            resolution=request.resolution,
            file_size=result.get("file_size"),
            thumbnail_url=result.get("snapshot_url"),
            generator=self.generator_name,
            metadata={"creatomate_data": result},
        )

    def _build_render_request(self, request: VideoRequest) -> dict:
        """Build Creatomate render request."""
        if request.template_id:
            # Template-based render
            return {
                "template_id": request.template_id,
                "modifications": request.template_variables,
                "output_format": request.format.value,
            }

        # Dynamic video composition
        elements = []

        # Add text elements from script
        text_element = {
            "type": "text",
            "text": request.script[:500],  # Limit text length
            "font_family": "Inter",
            "font_weight": "600",
            "font_size": "48 vmin",
            "fill_color": request.brand_colors.get("primary", "#FFFFFF"),
            "x": "50%",
            "y": "50%",
            "x_anchor": "50%",
            "y_anchor": "50%",
            "animations": [
                {"type": "text-appear", "time": "start", "duration": 1}
            ],
        }
        elements.append(text_element)

        # Add background
        background = {
            "type": "shape",
            "shape": "rectangle",
            "fill_color": request.brand_colors.get("secondary", "#1A1A2E"),
            "width": "100%",
            "height": "100%",
        }

        # Add logo if provided
        if request.logo_url:
            logo_element = {
                "type": "image",
                "source": request.logo_url,
                "width": "20%",
                "x": "10%",
                "y": "10%",
            }
            elements.append(logo_element)

        # Add voiceover if text provided
        audio_elements = []
        if request.voiceover_text:
            audio_elements.append({
                "type": "audio",
                "source": "tts",
                "text": request.voiceover_text,
                "voice": request.voiceover_voice,
            })

        # Add background music if provided
        if request.background_music:
            audio_elements.append({
                "type": "audio",
                "source": request.background_music,
                "volume": "30%",  # Lower volume under voiceover
            })

        return {
            "source": {
                "output_format": request.format.value,
                "width": int(request.resolution.split("x")[0]),
                "height": int(request.resolution.split("x")[1]),
                "duration": request.duration,
                "frame_rate": request.fps,
                "elements": [background] + elements + audio_elements,
            }
        }

    async def _wait_for_completion(
        self,
        render_id: str,
        timeout: int = 300,
        poll_interval: int = 5,
    ) -> dict:
        """Wait for render to complete."""
        elapsed = 0
        while elapsed < timeout:
            response = await self.client.get(f"/renders/{render_id}")
            response.raise_for_status()
            result = response.json()

            status = result.get("status")
            logger.info("Render status", render_id=render_id, status=status)

            if status == "succeeded":
                return result
            elif status == "failed":
                raise RuntimeError(f"Render failed: {result.get('error_message')}")

            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        raise TimeoutError(f"Render {render_id} timed out after {timeout} seconds")

    async def get_status(self, video_id: str) -> dict:
        """Get render status."""
        response = await self.client.get(f"/renders/{video_id}")
        response.raise_for_status()
        return response.json()
