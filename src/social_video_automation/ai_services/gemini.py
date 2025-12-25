"""Google Gemini service for content generation."""

import structlog
from google import generativeai as genai

from social_video_automation.ai_services.base import (
    AIService,
    ContentRequest,
    ContentResponse,
    ContentType,
)
from social_video_automation.config import get_settings

logger = structlog.get_logger()


class GeminiService(AIService):
    """Gemini service using Google AI API."""

    service_name = "gemini"

    def __init__(self) -> None:
        self.settings = get_settings()
        self._configured = False
        self._model: genai.GenerativeModel | None = None

    def _ensure_configured(self) -> None:
        """Ensure Gemini is configured."""
        if not self._configured and self.settings.ai.google_ai_api_key:
            genai.configure(api_key=self.settings.ai.google_ai_api_key)
            self._configured = True

    @property
    def model(self) -> genai.GenerativeModel:
        """Lazy-loaded Gemini model."""
        self._ensure_configured()
        if self._model is None:
            self._model = genai.GenerativeModel("gemini-2.0-flash")
        return self._model

    async def is_available(self) -> bool:
        """Check if Gemini service is available."""
        if not self.settings.ai.google_ai_api_key:
            return False
        try:
            self._ensure_configured()
            return True
        except Exception as e:
            logger.warning("Gemini service unavailable", error=str(e))
            return False

    async def generate_content(self, request: ContentRequest) -> ContentResponse:
        """Generate content using Gemini."""
        prompt = self._build_full_prompt(request)

        response = await self.model.generate_content_async(
            prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=request.max_length or 1000,
                temperature=0.7,
            ),
        )

        content = response.text if response.text else ""

        return ContentResponse(
            content=content,
            content_type=request.content_type,
            ai_service=self.service_name,
            tokens_used=0,  # Gemini doesn't expose token count the same way
            metadata={
                "model": "gemini-2.0-flash",
                "platform": request.platform,
            },
        )

    def _build_full_prompt(self, request: ContentRequest) -> str:
        """Build complete prompt for Gemini."""
        brand_context = self._build_brand_prompt(request.brand_context)
        platform_context = self._build_platform_context(request.platform)

        content_type_instructions = {
            ContentType.VIDEO_SCRIPT: """
Create an engaging video script for social media. The script should:
- Hook viewers in the first 2 seconds
- Include visual direction in [VISUAL] tags
- Include voiceover/audio in [AUDIO] tags
- Include on-screen text in [TEXT] tags
- Be optimized for the target platform
""",
            ContentType.CAPTION: """
Write an engaging social media caption that:
- Starts with a compelling hook
- Provides value or entertainment
- Ends with a call-to-action
- Feels authentic and on-brand
""",
            ContentType.HASHTAGS: """
Generate a strategic mix of hashtags:
- 3-5 highly popular hashtags (1M+ posts)
- 5-7 medium hashtags (100K-1M posts)
- 3-5 niche hashtags (10K-100K posts)
- All relevant to the content and brand
""",
            ContentType.THUMBNAIL_PROMPT: """
Create a detailed AI image generation prompt for a video thumbnail:
- Describe composition, colors, and style
- Include text overlay suggestions
- Make it visually striking and clickable
- Match the brand aesthetic
""",
            ContentType.CONTENT_IDEA: """
Generate creative content ideas that:
- Align with current social media trends
- Match the brand voice and values
- Have viral potential
- Are practical to execute
""",
        }

        return f"""
{content_type_instructions.get(request.content_type, "Generate creative content.")}

BRAND CONTEXT:
{brand_context}

PLATFORM: {request.platform}
{platform_context}

TOPIC: {request.topic}

{f"STYLE: {', '.join(request.style_hints)}" if request.style_hints else ""}
{f"ADDITIONAL CONTEXT: {request.additional_context}" if request.additional_context else ""}
{f"MAX LENGTH: {request.max_length} characters" if request.max_length else ""}

Generate the {request.content_type.value} now:
"""
