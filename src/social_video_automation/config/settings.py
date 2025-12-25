"""Application settings using Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AISettings(BaseSettings):
    """AI service API keys and configuration."""

    openai_api_key: str = Field(default="", description="OpenAI API key for ChatGPT")
    google_ai_api_key: str = Field(default="", description="Google AI API key for Gemini")
    xai_api_key: str = Field(default="", description="xAI API key for Grok")


class VideoSettings(BaseSettings):
    """Video generation settings."""

    creatomate_api_key: str = Field(default="", description="Creatomate API key")
    heygen_api_key: str = Field(default="", description="HeyGen API key")
    default_resolution: str = Field(default="1080x1920", description="Default video resolution")
    default_fps: int = Field(default=30, description="Default frames per second")
    default_duration: int = Field(default=30, description="Default video duration in seconds")


class SocialSettings(BaseSettings):
    """Social media posting settings."""

    ayrshare_api_key: str = Field(default="", description="Ayrshare API key")
    late_api_key: str = Field(default="", description="Late.dev API key")
    target_platforms: list[str] = Field(
        default=["instagram", "tiktok", "youtube", "facebook"],
        description="Target social platforms",
    )


class BrandSettings(BaseSettings):
    """PeterMat brand configuration."""

    name: str = Field(default="PeterMat", description="Brand name")
    tagline: str = Field(
        default="Born from the land. Built for performance.",
        description="Brand tagline",
    )
    tone: list[str] = Field(
        default=["professional", "sporty", "australian", "authentic"],
        description="Brand tone keywords",
    )
    colors: dict[str, str] = Field(
        default={
            "primary": "#FF6B35",
            "secondary": "#1A1A2E",
            "accent": "#F7931E",
        },
        description="Brand colors",
    )
    content_themes: list[str] = Field(
        default=[
            "australian sports",
            "athletic performance",
            "outdoor adventure",
            "team spirit",
            "quality craftsmanship",
        ],
        description="Content themes to focus on",
    )


class Settings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Environment
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Application environment",
    )
    log_level: str = Field(default="INFO", description="Logging level")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis URL")

    # Nested settings
    ai: AISettings = Field(default_factory=AISettings)
    video: VideoSettings = Field(default_factory=VideoSettings)
    social: SocialSettings = Field(default_factory=SocialSettings)
    brand: BrandSettings = Field(default_factory=BrandSettings)


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
