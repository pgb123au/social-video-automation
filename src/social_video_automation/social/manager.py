"""Social Manager - Orchestrates social media posting."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import structlog

from social_video_automation.config import get_settings
from social_video_automation.social.ayrshare import AyrsharePoster
from social_video_automation.social.base import (
    PostRequest,
    PostResult,
    SocialPlatform,
    SocialPoster,
)
from social_video_automation.social.late import LatePoster

logger = structlog.get_logger()


class SocialManager:
    """Manages social media posting across services."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.posters: dict[str, SocialPoster] = {
            "ayrshare": AyrsharePoster(),
            "late": LatePoster(),
        }

    async def get_available_posters(self) -> list[str]:
        """Get list of available social media posters."""
        available = []
        for name, poster in self.posters.items():
            if await poster.is_available():
                available.append(name)
        return available

    async def get_all_connected_accounts(self) -> dict[str, list[dict]]:
        """Get connected accounts from all available posters."""
        accounts = {}
        for name, poster in self.posters.items():
            if await poster.is_available():
                accounts[name] = await poster.get_connected_accounts()
        return accounts

    async def post(
        self,
        caption: str,
        hashtags: list[str] | None = None,
        video_url: str | None = None,
        platforms: list[str] | None = None,
        scheduled_time: datetime | None = None,
        preferred_poster: str | None = None,
        youtube_title: str = "",
    ) -> list[PostResult]:
        """Post content to social media platforms."""
        available = await self.get_available_posters()

        if not available:
            raise RuntimeError("No social media posters available. Check API configuration.")

        # Select poster
        if preferred_poster and preferred_poster in available:
            poster_name = preferred_poster
        else:
            # Prefer Ayrshare for multi-platform posting
            poster_name = "ayrshare" if "ayrshare" in available else available[0]

        poster = self.posters[poster_name]

        # Convert platform strings to enum
        if platforms is None:
            platforms = self.settings.social.target_platforms

        platform_enums = [SocialPlatform(p) for p in platforms]

        # Build request
        request = PostRequest(
            platforms=platform_enums,
            caption=caption,
            hashtags=hashtags or [],
            video_url=video_url,
            scheduled_time=scheduled_time,
            youtube_options={"title": youtube_title} if youtube_title else {},
        )

        logger.info(
            "Posting to social media",
            poster=poster_name,
            platforms=platforms,
            scheduled=scheduled_time is not None,
        )

        results = await poster.post(request)

        # Log results
        for result in results:
            if result.success:
                logger.info(
                    "Post successful",
                    platform=result.platform.value,
                    post_id=result.post_id,
                    url=result.post_url,
                )
            else:
                logger.error(
                    "Post failed",
                    platform=result.platform.value,
                    error=result.error,
                )

        return results

    async def schedule_posts(
        self,
        caption: str,
        video_url: str,
        platforms: list[str] | None = None,
        schedule: str = "optimal",  # "optimal", "morning", "evening", "custom"
        custom_times: dict[str, datetime] | None = None,
        hashtags: list[str] | None = None,
    ) -> list[PostResult]:
        """Schedule posts with optimized timing."""
        if platforms is None:
            platforms = self.settings.social.target_platforms

        all_results = []
        tz = ZoneInfo("Australia/Melbourne")

        if schedule == "optimal":
            # Platform-specific optimal times (AEDT)
            optimal_times = {
                "instagram": 12,  # Noon
                "tiktok": 19,  # 7 PM
                "youtube": 15,  # 3 PM
                "facebook": 13,  # 1 PM
            }

            now = datetime.now(tz)
            for platform in platforms:
                optimal_hour = optimal_times.get(platform, 12)
                scheduled = now.replace(hour=optimal_hour, minute=0, second=0, microsecond=0)

                # If the time has passed today, schedule for tomorrow
                if scheduled <= now:
                    scheduled += timedelta(days=1)

                results = await self.post(
                    caption=caption,
                    hashtags=hashtags,
                    video_url=video_url,
                    platforms=[platform],
                    scheduled_time=scheduled,
                )
                all_results.extend(results)

        elif schedule == "morning":
            scheduled = datetime.now(tz).replace(hour=9, minute=0, second=0, microsecond=0)
            if scheduled <= datetime.now(tz):
                scheduled += timedelta(days=1)

            results = await self.post(
                caption=caption,
                hashtags=hashtags,
                video_url=video_url,
                platforms=platforms,
                scheduled_time=scheduled,
            )
            all_results.extend(results)

        elif schedule == "evening":
            scheduled = datetime.now(tz).replace(hour=19, minute=0, second=0, microsecond=0)
            if scheduled <= datetime.now(tz):
                scheduled += timedelta(days=1)

            results = await self.post(
                caption=caption,
                hashtags=hashtags,
                video_url=video_url,
                platforms=platforms,
                scheduled_time=scheduled,
            )
            all_results.extend(results)

        elif schedule == "custom" and custom_times:
            for platform, time in custom_times.items():
                if platform in platforms:
                    results = await self.post(
                        caption=caption,
                        hashtags=hashtags,
                        video_url=video_url,
                        platforms=[platform],
                        scheduled_time=time,
                    )
                    all_results.extend(results)

        return all_results

    async def post_video_package(
        self,
        video_url: str,
        caption: str,
        hashtags: list[str],
        thumbnail_url: str | None = None,
        youtube_title: str = "",
        platforms: list[str] | None = None,
        schedule: str | None = None,
    ) -> dict[str, PostResult]:
        """Post a complete video package to all platforms."""
        if platforms is None:
            platforms = self.settings.social.target_platforms

        if schedule:
            results = await self.schedule_posts(
                caption=caption,
                video_url=video_url,
                platforms=platforms,
                schedule=schedule,
                hashtags=hashtags,
            )
        else:
            results = await self.post(
                caption=caption,
                hashtags=hashtags,
                video_url=video_url,
                platforms=platforms,
                youtube_title=youtube_title,
            )

        # Return as dict keyed by platform
        return {r.platform.value: r for r in results}
