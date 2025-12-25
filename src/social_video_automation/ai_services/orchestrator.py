"""AI Orchestrator - Coordinates multiple AI services for content generation."""

import asyncio
import random
from enum import Enum

import structlog

from social_video_automation.ai_services.base import (
    AIService,
    ContentRequest,
    ContentResponse,
)
from social_video_automation.ai_services.chatgpt import ChatGPTService
from social_video_automation.ai_services.gemini import GeminiService
from social_video_automation.ai_services.grok import GrokService

logger = structlog.get_logger()


class SelectionStrategy(str, Enum):
    """Strategy for selecting which AI service to use."""

    ROUND_ROBIN = "round_robin"  # Rotate between services
    RANDOM = "random"  # Random selection
    PRIORITY = "priority"  # Use first available in priority order
    ENSEMBLE = "ensemble"  # Get responses from all and pick best
    PARALLEL = "parallel"  # Get all responses and return all


class AIOrchestrator:
    """Orchestrates multiple AI services for content generation."""

    def __init__(self) -> None:
        self.services: dict[str, AIService] = {
            "chatgpt": ChatGPTService(),
            "gemini": GeminiService(),
            "grok": GrokService(),
        }
        self._priority_order = ["chatgpt", "gemini", "grok"]
        self._round_robin_index = 0

    async def get_available_services(self) -> list[str]:
        """Get list of available (configured and working) services."""
        available = []
        checks = await asyncio.gather(
            *[service.is_available() for service in self.services.values()],
            return_exceptions=True,
        )

        for name, is_available in zip(self.services.keys(), checks):
            if is_available is True:
                available.append(name)

        logger.info("Available AI services", services=available)
        return available

    async def generate_content(
        self,
        request: ContentRequest,
        strategy: SelectionStrategy = SelectionStrategy.PRIORITY,
        preferred_service: str | None = None,
    ) -> ContentResponse | list[ContentResponse]:
        """Generate content using the specified strategy."""
        available = await self.get_available_services()

        if not available:
            raise RuntimeError("No AI services available. Check API key configuration.")

        if preferred_service and preferred_service in available:
            return await self.services[preferred_service].generate_content(request)

        match strategy:
            case SelectionStrategy.PRIORITY:
                return await self._priority_generate(request, available)
            case SelectionStrategy.ROUND_ROBIN:
                return await self._round_robin_generate(request, available)
            case SelectionStrategy.RANDOM:
                return await self._random_generate(request, available)
            case SelectionStrategy.ENSEMBLE:
                return await self._ensemble_generate(request, available)
            case SelectionStrategy.PARALLEL:
                return await self._parallel_generate(request, available)

    async def _priority_generate(
        self, request: ContentRequest, available: list[str]
    ) -> ContentResponse:
        """Generate using first available service in priority order."""
        for service_name in self._priority_order:
            if service_name in available:
                logger.info("Using priority service", service=service_name)
                return await self.services[service_name].generate_content(request)

        # Fallback to any available
        service_name = available[0]
        return await self.services[service_name].generate_content(request)

    async def _round_robin_generate(
        self, request: ContentRequest, available: list[str]
    ) -> ContentResponse:
        """Generate using round-robin selection."""
        service_name = available[self._round_robin_index % len(available)]
        self._round_robin_index += 1
        logger.info("Using round-robin service", service=service_name)
        return await self.services[service_name].generate_content(request)

    async def _random_generate(
        self, request: ContentRequest, available: list[str]
    ) -> ContentResponse:
        """Generate using random selection."""
        service_name = random.choice(available)
        logger.info("Using random service", service=service_name)
        return await self.services[service_name].generate_content(request)

    async def _ensemble_generate(
        self, request: ContentRequest, available: list[str]
    ) -> ContentResponse:
        """Generate using all services and pick the best response."""
        responses = await self._parallel_generate(request, available)

        # For now, pick the longest response as "best"
        # Could be enhanced with quality scoring
        best = max(responses, key=lambda r: len(r.content))
        logger.info(
            "Ensemble selected best response",
            service=best.ai_service,
            length=len(best.content),
        )
        return best

    async def _parallel_generate(
        self, request: ContentRequest, available: list[str]
    ) -> list[ContentResponse]:
        """Generate using all available services in parallel."""
        tasks = [
            self.services[name].generate_content(request)
            for name in available
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        responses = []
        for name, result in zip(available, results):
            if isinstance(result, ContentResponse):
                responses.append(result)
            else:
                logger.warning("Service failed", service=name, error=str(result))

        if not responses:
            raise RuntimeError("All AI services failed to generate content")

        return responses

    async def generate_video_content_package(
        self,
        topic: str,
        platform: str,
        brand_context: dict | None = None,
    ) -> dict[str, ContentResponse]:
        """Generate a complete content package for a video."""
        from social_video_automation.ai_services.base import ContentType

        if brand_context is None:
            from social_video_automation.config import get_settings
            settings = get_settings()
            brand_context = {
                "name": settings.brand.name,
                "tagline": settings.brand.tagline,
                "tone": settings.brand.tone,
            }

        content_types = [
            ContentType.VIDEO_SCRIPT,
            ContentType.CAPTION,
            ContentType.HASHTAGS,
            ContentType.THUMBNAIL_PROMPT,
        ]

        tasks = []
        for content_type in content_types:
            request = ContentRequest(
                content_type=content_type,
                topic=topic,
                platform=platform,
                brand_context=brand_context,
            )
            tasks.append(self.generate_content(request))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        package = {}
        for content_type, result in zip(content_types, results):
            if isinstance(result, ContentResponse):
                package[content_type.value] = result
            else:
                logger.error(
                    "Failed to generate content",
                    content_type=content_type.value,
                    error=str(result),
                )

        return package
