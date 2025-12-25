"""Content Pipeline - End-to-end content generation and posting."""

from dataclasses import dataclass, field
from datetime import datetime

import structlog

from social_video_automation.ai_services import AIOrchestrator
from social_video_automation.ai_services.base import ContentResponse, ContentType
from social_video_automation.config import get_settings
from social_video_automation.social import SocialManager
from social_video_automation.social.base import PostResult
from social_video_automation.video import VideoManager
from social_video_automation.video.base import VideoResult

logger = structlog.get_logger()


@dataclass
class PipelineResult:
    """Result from the full content pipeline."""

    topic: str
    platforms: list[str]

    # Generated content
    script: ContentResponse | None = None
    caption: ContentResponse | None = None
    hashtags: ContentResponse | None = None
    thumbnail_prompt: ContentResponse | None = None

    # Video results by platform
    videos: dict[str, VideoResult] = field(default_factory=dict)

    # Posting results by platform
    post_results: dict[str, PostResult] = field(default_factory=dict)

    # Timing
    started_at: datetime | None = None
    completed_at: datetime | None = None

    # Errors
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """Check if pipeline completed successfully."""
        return (
            self.script is not None
            and len(self.videos) > 0
            and len(self.post_results) > 0
            and all(r.success for r in self.post_results.values())
        )

    @property
    def duration_seconds(self) -> float | None:
        """Get pipeline duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class ContentPipeline:
    """Orchestrates the full content creation and posting pipeline."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.ai = AIOrchestrator()
        self.video = VideoManager()
        self.social = SocialManager()

    async def run(
        self,
        topic: str,
        platforms: list[str] | None = None,
        schedule: str | None = None,  # None = immediate, "optimal", "morning", "evening"
        generate_video: bool = True,
        post_content: bool = True,
    ) -> PipelineResult:
        """Run the full content pipeline."""
        if platforms is None:
            platforms = self.settings.social.target_platforms

        result = PipelineResult(
            topic=topic,
            platforms=platforms,
            started_at=datetime.now(),
        )

        logger.info(
            "Starting content pipeline",
            topic=topic,
            platforms=platforms,
            schedule=schedule,
        )

        try:
            # Step 1: Generate content using AI services
            await self._generate_content(result)

            # Step 2: Generate videos (if enabled)
            if generate_video and result.script:
                await self._generate_videos(result)

            # Step 3: Post to social media (if enabled)
            if post_content and result.videos:
                await self._post_content(result, schedule)

        except Exception as e:
            logger.error("Pipeline error", error=str(e))
            result.errors.append(str(e))

        result.completed_at = datetime.now()

        logger.info(
            "Pipeline completed",
            success=result.success,
            duration=result.duration_seconds,
            errors=result.errors,
        )

        return result

    async def _generate_content(self, result: PipelineResult) -> None:
        """Generate content using AI services."""
        logger.info("Generating content", topic=result.topic)

        brand_context = {
            "name": self.settings.brand.name,
            "tagline": self.settings.brand.tagline,
            "tone": self.settings.brand.tone,
        }

        # Generate content package for the primary platform
        primary_platform = result.platforms[0] if result.platforms else "instagram"

        content_package = await self.ai.generate_video_content_package(
            topic=result.topic,
            platform=primary_platform,
            brand_context=brand_context,
        )

        # Store results
        result.script = content_package.get(ContentType.VIDEO_SCRIPT.value)
        result.caption = content_package.get(ContentType.CAPTION.value)
        result.hashtags = content_package.get(ContentType.HASHTAGS.value)
        result.thumbnail_prompt = content_package.get(ContentType.THUMBNAIL_PROMPT.value)

        if result.script:
            logger.info(
                "Content generated",
                script_length=len(result.script.content),
                ai_service=result.script.ai_service,
            )
        else:
            result.errors.append("Failed to generate video script")

    async def _generate_videos(self, result: PipelineResult) -> None:
        """Generate videos for all platforms."""
        if not result.script:
            result.errors.append("No script available for video generation")
            return

        logger.info("Generating videos", platforms=result.platforms)

        # Generate for all platforms
        videos = await self.video.generate_for_all_platforms(
            script=result.script.content,
            title=result.topic,
            voiceover_text=result.script.content,
            platforms=result.platforms,
        )

        result.videos = videos

        if videos:
            logger.info(
                "Videos generated",
                count=len(videos),
                platforms=list(videos.keys()),
            )
        else:
            result.errors.append("Failed to generate any videos")

    async def _post_content(self, result: PipelineResult, schedule: str | None) -> None:
        """Post content to social media."""
        if not result.videos:
            result.errors.append("No videos available for posting")
            return

        if not result.caption:
            result.errors.append("No caption available for posting")
            return

        # Parse hashtags
        hashtags = []
        if result.hashtags:
            # Extract hashtags from the generated content
            hashtag_content = result.hashtags.content
            hashtags = [
                tag.strip().lstrip("#")
                for tag in hashtag_content.split()
                if tag.startswith("#") or not any(c in tag for c in " \n")
            ][:15]  # Limit to 15 hashtags

        logger.info("Posting content", schedule=schedule, hashtag_count=len(hashtags))

        # Post each video to its platform
        for platform, video in result.videos.items():
            try:
                post_results = await self.social.post(
                    caption=result.caption.content,
                    hashtags=hashtags,
                    video_url=video.video_url,
                    platforms=[platform],
                    youtube_title=result.topic if platform == "youtube" else "",
                )

                for pr in post_results:
                    result.post_results[pr.platform.value] = pr

            except Exception as e:
                logger.error("Posting failed", platform=platform, error=str(e))
                result.errors.append(f"Failed to post to {platform}: {e}")

    async def generate_content_only(
        self,
        topic: str,
        platform: str = "instagram",
    ) -> dict[str, ContentResponse]:
        """Generate content without video/posting."""
        brand_context = {
            "name": self.settings.brand.name,
            "tagline": self.settings.brand.tagline,
            "tone": self.settings.brand.tone,
        }

        return await self.ai.generate_video_content_package(
            topic=topic,
            platform=platform,
            brand_context=brand_context,
        )

    async def generate_video_only(
        self,
        script: str,
        platform: str = "instagram",
    ) -> VideoResult:
        """Generate video without posting."""
        return await self.video.generate_video(
            script=script,
            platform=platform,
            download=True,
        )

    async def post_existing_video(
        self,
        video_url: str,
        caption: str,
        hashtags: list[str],
        platforms: list[str] | None = None,
        schedule: str | None = None,
    ) -> dict[str, PostResult]:
        """Post an existing video to social media."""
        return await self.social.post_video_package(
            video_url=video_url,
            caption=caption,
            hashtags=hashtags,
            platforms=platforms,
            schedule=schedule,
        )
