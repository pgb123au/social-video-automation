"""ChatGPT (OpenAI) service for content generation."""

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


class ChatGPTService(AIService):
    """ChatGPT service using OpenAI API."""

    service_name = "chatgpt"

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client: AsyncOpenAI | None = None

    @property
    def client(self) -> AsyncOpenAI:
        """Lazy-loaded OpenAI client."""
        if self._client is None:
            self._client = AsyncOpenAI(api_key=self.settings.ai.openai_api_key)
        return self._client

    async def is_available(self) -> bool:
        """Check if ChatGPT service is available."""
        if not self.settings.ai.openai_api_key:
            return False
        try:
            await self.client.models.list()
            return True
        except Exception as e:
            logger.warning("ChatGPT service unavailable", error=str(e))
            return False

    async def generate_content(self, request: ContentRequest) -> ContentResponse:
        """Generate content using ChatGPT."""
        system_prompt = self._build_system_prompt(request)
        user_prompt = self._build_user_prompt(request)

        response = await self.client.chat.completions.create(
            model="gpt-4o",
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
                "model": "gpt-4o",
                "platform": request.platform,
            },
        )

    def _build_system_prompt(self, request: ContentRequest) -> str:
        """Build system prompt for ChatGPT."""
        brand_context = self._build_brand_prompt(request.brand_context)
        platform_context = self._build_platform_context(request.platform)

        content_type_instructions = {
            ContentType.VIDEO_SCRIPT: """
You are a creative video script writer for social media. Write engaging, concise scripts
that capture attention immediately. Include visual cues and timing suggestions.
Format: [VISUAL] description | [AUDIO/VO] narration | [TEXT] on-screen text
""",
            ContentType.CAPTION: """
You are a social media caption writer. Write engaging captions that drive engagement.
Include a hook, value, and call-to-action. Keep it authentic and on-brand.
""",
            ContentType.HASHTAGS: """
You are a hashtag strategist. Generate relevant, trending hashtags that maximize reach
while staying authentic to the brand. Mix popular and niche hashtags.
""",
            ContentType.THUMBNAIL_PROMPT: """
You are an AI image prompt engineer. Create detailed prompts for AI image generation
that will create compelling video thumbnails. Be specific about composition and style.
""",
            ContentType.CONTENT_IDEA: """
You are a content strategist. Generate creative, engaging content ideas that align
with current trends while staying true to the brand voice.
""",
        }

        return f"""
{content_type_instructions.get(request.content_type, "")}

{brand_context}

Platform Context: {platform_context}
"""

    def _build_user_prompt(self, request: ContentRequest) -> str:
        """Build user prompt for the request."""
        prompt = f"Create {request.content_type.value} about: {request.topic}"

        if request.style_hints:
            prompt += f"\n\nStyle: {', '.join(request.style_hints)}"

        if request.additional_context:
            prompt += f"\n\nAdditional context: {request.additional_context}"

        if request.max_length:
            prompt += f"\n\nKeep it under {request.max_length} characters."

        return prompt
