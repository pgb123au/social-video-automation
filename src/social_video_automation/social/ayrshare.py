"""Ayrshare social media posting service."""

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

AYRSHARE_API_URL = "https://api.ayrshare.com"


class AyrsharePoster(SocialPoster):
    """Social media poster using Ayrshare API."""

    poster_name = "ayrshare"

    PLATFORM_MAP = {
        SocialPlatform.INSTAGRAM: "instagram",
        SocialPlatform.TIKTOK: "tiktok",
        SocialPlatform.YOUTUBE: "youtube",
        SocialPlatform.FACEBOOK: "facebook",
        SocialPlatform.TWITTER: "twitter",
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
                base_url=AYRSHARE_API_URL,
                headers={
                    "Authorization": f"Bearer {self.settings.social.ayrshare_api_key}",
                    "Content-Type": "application/json",
                },
                timeout=120.0,
            )
        return self._client

    async def is_available(self) -> bool:
        """Check if Ayrshare is available."""
        if not self.settings.social.ayrshare_api_key:
            return False
        try:
            response = await self.client.get("/api/user")
            return response.status_code == 200
        except Exception as e:
            logger.warning("Ayrshare unavailable", error=str(e))
            return False

    async def get_connected_accounts(self) -> list[dict]:
        """Get list of connected social media accounts."""
        response = await self.client.get("/api/user")
        response.raise_for_status()
        data = response.json()

        # Extract connected platforms
        accounts = []
        for platform in data.get("activeSocialAccounts", []):
            accounts.append({
                "platform": platform,
                "connected": True,
            })
        return accounts

    async def post(self, request: PostRequest) -> list[PostResult]:
        """Post content to multiple platforms."""
        # Build the post payload
        payload = self._build_payload(request)

        logger.info(
            "Posting to Ayrshare",
            platforms=[p.value for p in request.platforms],
            has_video=bool(request.video_url),
        )

        response = await self.client.post("/api/post", json=payload)

        results = []
        if response.status_code == 200:
            data = response.json()
            results = self._parse_response(data, request.platforms)
        else:
            error = response.json().get("message", "Unknown error")
            for platform in request.platforms:
                results.append(PostResult(
                    platform=platform,
                    success=False,
                    error=error,
                ))

        return results

    def _build_payload(self, request: PostRequest) -> dict:
        """Build Ayrshare post payload."""
        platforms = [self.PLATFORM_MAP[p] for p in request.platforms]

        payload: dict = {
            "post": request.full_caption,
            "platforms": platforms,
        }

        # Add video
        if request.video_url:
            payload["mediaUrls"] = [request.video_url]
            payload["isVideo"] = True

        # Add images
        if request.image_urls:
            payload["mediaUrls"] = request.image_urls

        # Add scheduling
        if request.scheduled_time:
            payload["scheduleDate"] = request.scheduled_time.isoformat()

        # Platform-specific options
        if SocialPlatform.YOUTUBE in request.platforms:
            payload["youTubeOptions"] = {
                "title": request.youtube_options.get("title", ""),
                "visibility": request.youtube_options.get("visibility", "public"),
                "shorts": True,  # Default to Shorts for short videos
            }

        if SocialPlatform.TIKTOK in request.platforms:
            payload["tikTokOptions"] = {
                "allowComment": request.tiktok_options.get("allow_comments", True),
                "allowDuet": request.tiktok_options.get("allow_duet", True),
                "allowStitch": request.tiktok_options.get("allow_stitch", True),
            }

        if SocialPlatform.INSTAGRAM in request.platforms:
            payload["instagramOptions"] = {
                "reels": True,  # Post as Reels for video content
            }

        return payload

    def _parse_response(
        self, data: dict, platforms: list[SocialPlatform]
    ) -> list[PostResult]:
        """Parse Ayrshare response into PostResults."""
        results = []

        # Check for overall success
        if data.get("status") == "success":
            for platform in platforms:
                platform_key = self.PLATFORM_MAP[platform]
                platform_data = data.get("postIds", {}).get(platform_key, {})

                results.append(PostResult(
                    platform=platform,
                    success=True,
                    post_id=platform_data.get("id", data.get("id")),
                    post_url=platform_data.get("postUrl"),
                    scheduled=bool(data.get("scheduleDate")),
                    metadata={"ayrshare_response": platform_data},
                ))
        else:
            # Handle errors
            errors = data.get("errors", [])
            for platform in platforms:
                platform_key = self.PLATFORM_MAP[platform]
                platform_error = next(
                    (e for e in errors if e.get("platform") == platform_key),
                    None
                )

                results.append(PostResult(
                    platform=platform,
                    success=platform_error is None,
                    error=platform_error.get("message") if platform_error else None,
                    post_id=data.get("id"),
                ))

        return results

    async def get_post_analytics(self, post_id: str, platform: SocialPlatform) -> dict:
        """Get analytics for a specific post."""
        response = await self.client.get(
            "/api/analytics/post",
            params={
                "id": post_id,
                "platforms": [self.PLATFORM_MAP[platform]],
            }
        )
        response.raise_for_status()
        return response.json()

    async def delete_post(self, post_id: str) -> bool:
        """Delete a scheduled or published post."""
        response = await self.client.delete(
            "/api/post",
            json={"id": post_id}
        )
        return response.status_code == 200
