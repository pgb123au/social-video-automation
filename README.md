# Social Video Automation

AI-powered video generation and social media auto-posting system for PeterMat Australian Sporting Brand.

## Overview

This system automates the entire content creation pipeline:

1. **AI Content Generation** - Uses ChatGPT, Gemini, and Grok to generate video scripts, captions, and hashtags
2. **Video Production** - Generates videos using Creatomate or HeyGen APIs
3. **Social Posting** - Auto-posts to Instagram, TikTok, YouTube, and Facebook via Ayrshare or Late

## Features

- Multi-AI orchestration (ChatGPT, Gemini, Grok) with fallback and parallel generation
- Platform-optimized video generation (9:16 for Reels/Shorts, etc.)
- Scheduled posting with optimal timing per platform
- Brand-consistent content generation
- CLI for easy operation

## Installation

```bash
# Clone or navigate to the project
cd /Users/peterball/Projects/social-video-automation

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -e ".[dev]"
```

## Configuration

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Configure your API keys in `.env`:

```env
# AI Services (at least one required)
OPENAI_API_KEY=sk-...          # ChatGPT
GOOGLE_AI_API_KEY=...          # Gemini
XAI_API_KEY=...                # Grok

# Video Generation (at least one required)
CREATOMATE_API_KEY=...         # Creatomate
HEYGEN_API_KEY=...             # HeyGen (for AI avatars)

# Social Posting (at least one required)
AYRSHARE_API_KEY=...           # Ayrshare (recommended)
LATE_API_KEY=...               # Late.dev (alternative)
```

3. Check your configuration:

```bash
sva status
```

## Usage

### Generate and Post Content

```bash
# Generate content and post immediately
sva generate "Australian cricket gear review"

# Generate for specific platforms
sva generate "New AFL season preview" --platforms instagram,tiktok

# Schedule with optimal timing per platform
sva generate "Summer sports essentials" --schedule optimal

# Generate content only (no video/posting)
sva generate "Product spotlight" --no-video --no-post
```

### Generate Content Only

```bash
sva content "Winter training tips"
```

### Generate Content Ideas

```bash
sva ideas --theme "australian sports" --count 5
```

### Check Service Status

```bash
sva status
```

## Architecture

```
social-video-automation/
├── src/social_video_automation/
│   ├── ai_services/          # ChatGPT, Gemini, Grok integrations
│   │   ├── base.py           # Abstract base classes
│   │   ├── chatgpt.py        # OpenAI ChatGPT
│   │   ├── gemini.py         # Google Gemini
│   │   ├── grok.py           # xAI Grok
│   │   └── orchestrator.py   # Multi-AI coordination
│   ├── video/                # Video generation
│   │   ├── base.py           # Abstract base classes
│   │   ├── creatomate.py     # Creatomate API
│   │   ├── heygen.py         # HeyGen AI avatars
│   │   └── manager.py        # Video orchestration
│   ├── social/               # Social media posting
│   │   ├── base.py           # Abstract base classes
│   │   ├── ayrshare.py       # Ayrshare API
│   │   ├── late.py           # Late.dev API
│   │   └── manager.py        # Posting orchestration
│   ├── content/              # Content pipeline
│   │   └── pipeline.py       # End-to-end orchestration
│   ├── config/               # Configuration
│   │   └── settings.py       # Pydantic settings
│   └── cli.py                # CLI commands
```

## API Keys Setup

### ChatGPT (OpenAI)
- Get your API key at: https://platform.openai.com/api-keys
- Uses GPT-4o for content generation

### Gemini (Google)
- Get your API key at: https://makersuite.google.com/app/apikey
- Uses Gemini 2.0 Flash

### Grok (xAI)
- Get your API key at: https://x.ai/api
- Uses Grok-3

### Creatomate
- Sign up at: https://creatomate.com
- Supports template-based and dynamic video generation

### HeyGen
- Sign up at: https://heygen.com
- For AI avatar videos with text-to-speech

### Ayrshare
- Sign up at: https://ayrshare.com
- Unified API for all social platforms

### Late.dev
- Sign up at: https://getlate.dev
- Alternative unified social API

## Scheduling Options

- `optimal` - Posts at optimal times for each platform (AEDT)
  - Instagram: 12:00 PM
  - TikTok: 7:00 PM
  - YouTube: 3:00 PM
  - Facebook: 1:00 PM
- `morning` - Posts at 9:00 AM
- `evening` - Posts at 7:00 PM

## Brand Configuration

Default PeterMat brand settings in `.env`:

```env
BRAND_NAME=PeterMat
BRAND_TAGLINE="Born from the land. Built for performance."
BRAND_TONE=professional,sporty,australian,authentic
TARGET_PLATFORMS=instagram,tiktok,youtube,facebook
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check .

# Run type checker
mypy src/
```

## License

MIT

## Author

Peter Ball
