"""xAI Grok service for content generation."""

import structlog
from openai import AsyncOpenAI

from social_video_automation.ai_services.base import (
    AIService,
    ContentRequest,
    ContentResponse,
    ContentType,
)
from social_video_automation.config import get_settings

logger = structlog.get_logger()


class GrokService(AIService):
    """Grok service using xAI API (OpenAI-compatible)."""

    service_name = "grok"

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client: AsyncOpenAI | None = None

    @property
    def client(self) -> AsyncOpenAI:
        """Lazy-loaded xAI client (OpenAI-compatible)."""
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=self.settings.ai.xai_api_key,
                base_url="https://api.x.ai/v1",
            )
        return self._client

    async def is_available(self) -> bool:
        """Check if Grok service is available."""
        if not self.settings.ai.xai_api_key:
            return False
        try:
            await self.client.models.list()
            return True
        except Exception as e:
            logger.warning("Grok service unavailable", error=str(e))
            return False

    async def generate_content(self, request: ContentRequest) -> ContentResponse:
        """Generate content using Grok."""
        system_prompt = self._build_system_prompt(request)
        user_prompt = self._build_user_prompt(request)

        response = await self.client.chat.completions.create(
            model="grok-3",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=request.max_length or 1000,
            temperature=0.7,
        )

        content = response.choices[0].message.content or ""
        tokens_used = response.usage.total_tokens if response.usage else 0

        return ContentResponse(
            content=content,
            content_type=request.content_type,
            ai_service=self.service_name,
            tokens_used=tokens_used,
            metadata={
                "model": "grok-3",
                "platform": request.platform,
            },
        )

    def _build_system_prompt(self, request: ContentRequest) -> str:
        """Build system prompt for Grok."""
        brand_context = self._build_brand_prompt(request.brand_context)
        platform_context = self._build_platform_context(request.platform)

        # Grok has a more conversational, slightly edgy personality
        content_type_instructions = {
            ContentType.VIDEO_SCRIPT: """
You're creating video scripts for social media. Be bold, authentic, and engaging.
Hook viewers immediately - no slow intros. Keep it punchy and memorable.
Format: [VISUAL] | [AUDIO] | [TEXT ON SCREEN]
""",
            ContentType.CAPTION: """
Write captions that cut through the noise. Be authentic, slightly bold, but professional.
Start strong, deliver value, end with action. No fluff.
""",
            ContentType.HASHTAGS: """
Generate hashtags that actually work. Mix trending with niche.
Skip the generic garbage - focus on what drives real engagement.
""",
            ContentType.THUMBNAIL_PROMPT: """
Create an image prompt that demands attention. Be specific about:
- Composition and focal point
- Color psychology
- Text placement
- Emotional impact
""",
            ContentType.CONTENT_IDEA: """
Generate content ideas that stand out. Think about what makes people stop scrolling.
Be creative but practical. Trends matter but authenticity matters more.
""",
        }

        return f"""
{content_type_instructions.get(request.content_type, "Generate compelling content.")}

{brand_context}

Platform: {platform_context}

Be authentic to the Australian sporting brand identity. Quality, performance, the land.
"""

    def _build_user_prompt(self, request: ContentRequest) -> str:
        """Build user prompt for the request."""
        prompt = f"Create {request.content_type.value} for: {request.topic}"

        if request.style_hints:
            prompt += f"\n\nVibe: {', '.join(request.style_hints)}"

        if request.additional_context:
            prompt += f"\n\nContext: {request.additional_context}"

        if request.max_length:
            prompt += f"\n\nMax {request.max_length} characters."

        return prompt
