# Social Video Automation API Reference

## CLI Commands

### `sva generate`

Generate and post video content to social media.

```bash
sva generate <topic> [options]
```

**Arguments:**
- `topic` (required): Topic for the video content

**Options:**
- `--platforms, -p`: Comma-separated platforms (default: `instagram,tiktok,youtube`)
- `--schedule, -s`: Schedule timing - `optimal`, `morning`, or `evening`
- `--no-post`: Generate content but don't post
- `--no-video`: Generate content but skip video creation

**Examples:**
```bash
# Generate and post immediately
sva generate "Australian cricket gear review"

# Specific platforms with optimal scheduling
sva generate "AFL season preview" --platforms instagram,tiktok --schedule optimal

# Content and video only (no posting)
sva generate "Summer essentials" --no-post
```

---

### `sva content`

Generate content only (script, caption, hashtags) without video.

```bash
sva content <topic> [options]
```

**Arguments:**
- `topic` (required): Topic for content generation

**Options:**
- `--platform, -p`: Target platform (default: `instagram`)

**Examples:**
```bash
sva content "Winter training tips"
sva content "New product launch" --platform tiktok
```

---

### `sva ideas`

Generate content ideas for PeterMat.

```bash
sva ideas [options]
```

**Options:**
- `--theme, -t`: Content theme
- `--count, -c`: Number of ideas to generate (default: 5)

**Examples:**
```bash
sva ideas --theme "australian sports" --count 10
sva ideas --theme "product reviews"
```

---

### `sva status`

Check status of all configured services.

```bash
sva status
```

Shows availability of:
- AI Services (ChatGPT, Gemini, Grok)
- Video Generators (Creatomate, HeyGen)
- Social Media Posters (Ayrshare, Late)
- Connected social accounts

---

### `sva init`

Show setup instructions and configuration guide.

```bash
sva init
```

---

## Python API

### ContentPipeline

Main orchestration class for the content generation pipeline.

```python
from social_video_automation.content import ContentPipeline

pipeline = ContentPipeline()

# Full pipeline
result = await pipeline.run(
    topic="Australian cricket gear",
    platforms=["instagram", "tiktok"],
    schedule="optimal",
    generate_video=True,
    post_content=True,
)

# Content only
content = await pipeline.generate_content_only(
    topic="Product review",
    platform="instagram",
)
```

### AIOrchestrator

Multi-AI coordination for content generation.

```python
from social_video_automation.ai_services import AIOrchestrator
from social_video_automation.ai_services.base import ContentRequest, ContentType

ai = AIOrchestrator()

# Check available services
services = await ai.get_available_services()

# Generate content
request = ContentRequest(
    content_type=ContentType.VIDEO_SCRIPT,
    topic="Summer sports gear",
    platform="instagram",
    brand_context={"name": "PeterMat", "tone": "professional,sporty"},
)
response = await ai.generate_content(request)
```

### VideoManager

Video generation orchestration.

```python
from social_video_automation.video import VideoManager

video = VideoManager()

# Check available generators
generators = await video.get_available_generators()

# Generate video
result = await video.generate(
    script="Your video script here",
    platform="instagram",
    style="dynamic",
)
```

### SocialManager

Social media posting orchestration.

```python
from social_video_automation.social import SocialManager

social = SocialManager()

# Check available posters
posters = await social.get_available_posters()

# Get connected accounts
accounts = await social.get_all_connected_accounts()

# Post content
result = await social.post(
    video_url="https://...",
    caption="Your caption #hashtags",
    platforms=["instagram", "tiktok"],
    schedule_time=None,  # or datetime for scheduled post
)
```

---

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | One AI required | ChatGPT API key |
| `GOOGLE_AI_API_KEY` | One AI required | Gemini API key |
| `XAI_API_KEY` | One AI required | Grok API key |
| `CREATOMATE_API_KEY` | One video required | Creatomate API key |
| `HEYGEN_API_KEY` | One video required | HeyGen API key |
| `AYRSHARE_API_KEY` | One social required | Ayrshare API key |
| `LATE_API_KEY` | One social required | Late.dev API key |

### Brand Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `BRAND_NAME` | PeterMat | Brand name for content |
| `BRAND_TAGLINE` | Born from the land... | Brand tagline |
| `BRAND_TONE` | professional,sporty,australian | Content tone |
| `TARGET_PLATFORMS` | instagram,tiktok,youtube,facebook | Default platforms |

---

## Scheduling

| Option | Description |
|--------|-------------|
| `optimal` | Platform-specific optimal times (AEDT) |
| `morning` | 9:00 AM AEDT |
| `evening` | 7:00 PM AEDT |

### Optimal Times by Platform

| Platform | Time (AEDT) |
|----------|-------------|
| Instagram | 12:00 PM |
| TikTok | 7:00 PM |
| YouTube | 3:00 PM |
| Facebook | 1:00 PM |
