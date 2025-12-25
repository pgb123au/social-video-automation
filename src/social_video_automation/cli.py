"""CLI for Social Video Automation."""

import asyncio
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

app = typer.Typer(
    name="sva",
    help="Social Video Automation - AI-powered video generation and social posting for PeterMat",
    no_args_is_help=True,
)
console = Console()


def run_async(coro):
    """Run async function in sync context."""
    return asyncio.run(coro)


@app.command()
def generate(
    topic: Annotated[str, typer.Argument(help="Topic for the video content")],
    platforms: Annotated[
        str, typer.Option("--platforms", "-p", help="Comma-separated platforms")
    ] = "instagram,tiktok,youtube",
    schedule: Annotated[
        str | None, typer.Option("--schedule", "-s", help="Schedule: optimal, morning, evening")
    ] = None,
    no_post: Annotated[
        bool, typer.Option("--no-post", help="Generate content but don't post")
    ] = False,
    no_video: Annotated[
        bool, typer.Option("--no-video", help="Generate content but skip video creation")
    ] = False,
):
    """Generate and post video content to social media."""
    from social_video_automation.content import ContentPipeline

    platform_list = [p.strip() for p in platforms.split(",")]

    console.print(Panel(
        f"[bold blue]Generating content for:[/] {topic}\n"
        f"[bold]Platforms:[/] {', '.join(platform_list)}\n"
        f"[bold]Schedule:[/] {schedule or 'Immediate'}",
        title="🎬 Social Video Automation",
    ))

    async def run():
        pipeline = ContentPipeline()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Running pipeline...", total=None)

            result = await pipeline.run(
                topic=topic,
                platforms=platform_list,
                schedule=schedule,
                generate_video=not no_video,
                post_content=not no_post,
            )

            progress.update(task, completed=True)

        # Display results
        if result.success:
            console.print("\n[bold green]✓ Pipeline completed successfully![/]\n")
        else:
            console.print("\n[bold yellow]⚠ Pipeline completed with issues[/]\n")

        # Show generated content
        if result.script:
            console.print(Panel(
                result.script.content[:500] + "..." if len(result.script.content) > 500 else result.script.content,
                title="📝 Generated Script",
                subtitle=f"via {result.script.ai_service}",
            ))

        if result.caption:
            console.print(Panel(
                result.caption.content,
                title="💬 Caption",
            ))

        # Show video results
        if result.videos:
            table = Table(title="🎥 Generated Videos")
            table.add_column("Platform")
            table.add_column("Status")
            table.add_column("URL")

            for platform, video in result.videos.items():
                table.add_row(
                    platform,
                    "[green]✓ Generated[/]",
                    video.video_url[:50] + "..." if len(video.video_url) > 50 else video.video_url,
                )

            console.print(table)

        # Show posting results
        if result.post_results:
            table = Table(title="📤 Posting Results")
            table.add_column("Platform")
            table.add_column("Status")
            table.add_column("Post URL")

            for platform, pr in result.post_results.items():
                status = "[green]✓ Posted[/]" if pr.success else f"[red]✗ {pr.error}[/]"
                url = pr.post_url or "-"
                table.add_row(platform, status, url[:50] + "..." if len(url) > 50 else url)

            console.print(table)

        # Show errors
        if result.errors:
            console.print("\n[bold red]Errors:[/]")
            for error in result.errors:
                console.print(f"  • {error}")

        # Show duration
        if result.duration_seconds:
            console.print(f"\n[dim]Total duration: {result.duration_seconds:.1f}s[/]")

    run_async(run())


@app.command()
def content(
    topic: Annotated[str, typer.Argument(help="Topic for content generation")],
    platform: Annotated[
        str, typer.Option("--platform", "-p", help="Target platform")
    ] = "instagram",
):
    """Generate content only (script, caption, hashtags) without video."""
    from social_video_automation.content import ContentPipeline

    console.print(f"[bold]Generating content for:[/] {topic}")

    async def run():
        pipeline = ContentPipeline()
        content = await pipeline.generate_content_only(topic=topic, platform=platform)

        for content_type, response in content.items():
            console.print(Panel(
                response.content,
                title=f"📝 {content_type.replace('_', ' ').title()}",
                subtitle=f"via {response.ai_service}",
            ))

    run_async(run())


@app.command()
def status():
    """Check status of all configured services."""
    from social_video_automation.ai_services import AIOrchestrator
    from social_video_automation.social import SocialManager
    from social_video_automation.video import VideoManager

    console.print(Panel("[bold]Checking service status...[/]", title="🔍 Status Check"))

    async def run():
        # Check AI services
        ai = AIOrchestrator()
        ai_available = await ai.get_available_services()

        table = Table(title="AI Services")
        table.add_column("Service")
        table.add_column("Status")

        for service in ["chatgpt", "gemini", "grok"]:
            status = "[green]✓ Available[/]" if service in ai_available else "[red]✗ Not configured[/]"
            table.add_row(service.upper(), status)

        console.print(table)

        # Check video services
        video = VideoManager()
        video_available = await video.get_available_generators()

        table = Table(title="Video Generators")
        table.add_column("Service")
        table.add_column("Status")

        for service in ["creatomate", "heygen"]:
            status = "[green]✓ Available[/]" if service in video_available else "[red]✗ Not configured[/]"
            table.add_row(service.title(), status)

        console.print(table)

        # Check social services
        social = SocialManager()
        social_available = await social.get_available_posters()

        table = Table(title="Social Media Posters")
        table.add_column("Service")
        table.add_column("Status")

        for service in ["ayrshare", "late"]:
            status = "[green]✓ Available[/]" if service in social_available else "[red]✗ Not configured[/]"
            table.add_row(service.title(), status)

        console.print(table)

        # Check connected accounts
        if social_available:
            accounts = await social.get_all_connected_accounts()
            for poster, accts in accounts.items():
                if accts:
                    console.print(f"\n[bold]{poster.title()} Connected Accounts:[/]")
                    for acct in accts:
                        console.print(f"  • {acct.get('platform', acct)}")

    run_async(run())


@app.command()
def ideas(
    theme: Annotated[
        str | None, typer.Option("--theme", "-t", help="Content theme")
    ] = None,
    count: Annotated[
        int, typer.Option("--count", "-c", help="Number of ideas to generate")
    ] = 5,
):
    """Generate content ideas for PeterMat."""
    from social_video_automation.ai_services import AIOrchestrator
    from social_video_automation.ai_services.base import ContentRequest, ContentType
    from social_video_automation.config import get_settings

    settings = get_settings()
    theme = theme or settings.brand.content_themes[0]

    console.print(f"[bold]Generating {count} content ideas for theme:[/] {theme}")

    async def run():
        ai = AIOrchestrator()

        request = ContentRequest(
            content_type=ContentType.CONTENT_IDEA,
            topic=f"Generate {count} unique video content ideas about: {theme}",
            platform="instagram",
            brand_context={
                "name": settings.brand.name,
                "tagline": settings.brand.tagline,
                "tone": settings.brand.tone,
            },
            additional_context=f"Focus on themes: {', '.join(settings.brand.content_themes)}",
        )

        response = await ai.generate_content(request)

        console.print(Panel(
            response.content,
            title="💡 Content Ideas",
            subtitle=f"via {response.ai_service}",
        ))

    run_async(run())


@app.command()
def init():
    """Initialize configuration and show setup instructions."""
    console.print(Panel("""
[bold]Social Video Automation Setup[/]

1. Copy .env.example to .env:
   [dim]cp .env.example .env[/]

2. Configure your API keys in .env:
   • OPENAI_API_KEY - For ChatGPT content generation
   • GOOGLE_AI_API_KEY - For Gemini content generation
   • XAI_API_KEY - For Grok content generation
   • CREATOMATE_API_KEY - For video generation
   • HEYGEN_API_KEY - For AI avatar videos
   • AYRSHARE_API_KEY - For social media posting
   • LATE_API_KEY - Alternative social media API

3. Run status check:
   [dim]sva status[/]

4. Generate your first content:
   [dim]sva generate "Australian cricket gear review"[/]
""", title="🚀 Getting Started"))


if __name__ == "__main__":
    app()
