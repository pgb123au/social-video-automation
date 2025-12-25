"""Late.dev social media posting service."""

import httpx
import structlog

from social_video_automation.config import get_settings
from social_video_automation.social.base import (
    PostRequest,
    PostResult,
    SocialPlatform,
    SocialPoster,
)

logger = structlog.get_logger()

LATE_API_URL = "https://api.getlate.dev"


class LatePoster(SocialPoster):
    """Social media poster using Late.dev API."""

    poster_name = "late"

    PLATFORM_MAP = {
        SocialPlatform.INSTAGRAM: "instagram",
        SocialPlatform.TIKTOK: "tiktok",
        SocialPlatform.YOUTUBE: "youtube",
        SocialPlatform.FACEBOOK: "facebook",
        SocialPlatform.TWITTER: "x",  # Late uses "x" for Twitter
        SocialPlatform.LINKEDIN: "linkedin",
        SocialPlatform.THREADS: "threads",
        SocialPlatform.PINTEREST: "pinterest",
    }

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Lazy-loaded HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=LATE_API_URL,
                headers={
                    "Authorization": f"Bearer {self.settings.social.late_api_key}",
                    "Content-Type": "application/json",
                },
                timeout=120.0,
            )
        return self._client

    async def is_available(self) -> bool:
        """Check if Late is available."""
        if not self.settings.social.late_api_key:
            return False
        try:
            response = await self.client.get("/v1/accounts")
            return response.status_code == 200
        except Exception as e:
            logger.warning("Late unavailable", error=str(e))
            return False

    async def get_connected_accounts(self) -> list[dict]:
        """Get list of connected social media accounts."""
        response = await self.client.get("/v1/accounts")
        response.raise_for_status()
        return response.json().get("data", [])

    async def post(self, request: PostRequest) -> list[PostResult]:
        """Post content using Late API."""
        results = []

        # Late requires posting to each platform separately
        for platform in request.platforms:
            result = await self._post_to_platform(request, platform)
            results.append(result)

        return results

    async def _post_to_platform(
        self, request: PostRequest, platform: SocialPlatform
    ) -> PostResult:
        """Post to a single platform."""
        payload = self._build_payload(request, platform)

        logger.info("Posting to Late", platform=platform.value)

        try:
            response = await self.client.post("/v1/posts", json=payload)

            if response.status_code in (200, 201):
                data = response.json()
                return PostResult(
                    platform=platform,
                    success=True,
                    post_id=data.get("data", {}).get("id"),
                    post_url=data.get("data", {}).get("url"),
                    scheduled=request.scheduled_time is not None,
                    scheduled_time=request.scheduled_time,
                    metadata={"late_response": data},
                )
            else:
                error_data = response.json()
                return PostResult(
                    platform=platform,
                    success=False,
                    error=error_data.get("message", f"HTTP {response.status_code}"),
                )

        except Exception as e:
            logger.error("Failed to post", platform=platform.value, error=str(e))
            return PostResult(
                platform=platform,
                success=False,
                error=str(e),
            )

    def _build_payload(self, request: PostRequest, platform: SocialPlatform) -> dict:
        """Build Late post payload."""
        platform_key = self.PLATFORM_MAP[platform]

        payload: dict = {
            "platform": platform_key,
            "text": request.full_caption,
        }

        # Add media
        if request.video_url:
            payload["media"] = [{
                "type": "video",
                "url": request.video_url,
            }]
        elif request.image_urls:
            payload["media"] = [
                {"type": "image", "url": url} for url in request.image_urls
            ]

        # Add scheduling
        if request.scheduled_time:
            payload["scheduledFor"] = request.scheduled_time.isoformat()

        # Platform-specific options
        if platform == SocialPlatform.YOUTUBE:
            payload["youtube"] = {
                "title": request.youtube_options.get("title", ""),
                "privacyStatus": request.youtube_options.get("visibility", "public"),
                "isShort": True,
            }

        if platform == SocialPlatform.TIKTOK:
            payload["tiktok"] = {
                "privacyLevel": "PUBLIC_TO_EVERYONE",
                "allowComments": request.tiktok_options.get("allow_comments", True),
                "allowDuet": request.tiktok_options.get("allow_duet", True),
                "allowStitch": request.tiktok_options.get("allow_stitch", True),
            }

        if platform == SocialPlatform.INSTAGRAM:
            payload["instagram"] = {
                "contentType": "REELS" if request.video_url else "FEED",
            }

        return payload

    async def get_post_analytics(self, post_id: str, platform: SocialPlatform) -> dict:
        """Get analytics for a specific post."""
        response = await self.client.get(f"/v1/posts/{post_id}/analytics")
        response.raise_for_status()
        return response.json()

    async def delete_post(self, post_id: str) -> bool:
        """Delete a post."""
        response = await self.client.delete(f"/v1/posts/{post_id}")
        return response.status_code in (200, 204)

    async def get_scheduled_posts(self) -> list[dict]:
        """Get all scheduled posts."""
        response = await self.client.get("/v1/posts", params={"status": "scheduled"})
        response.raise_for_status()
        return response.json().get("data", [])
