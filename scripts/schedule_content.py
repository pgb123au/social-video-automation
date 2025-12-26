#!/usr/bin/env python3
"""Automated content scheduling for PeterMat social media."""

import asyncio
import random
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from social_video_automation.templates import (
    CONTENT_FORMULAS,
    PLATFORM_TEMPLATES,
    VIRAL_HOOKS,
)
from social_video_automation.templates.content_formulas import (
    CONTENT_PILLARS,
    POSTING_SCHEDULE,
)

AEDT = ZoneInfo("Australia/Sydney")


def get_next_posting_times(platform: str, days: int = 7) -> list[datetime]:
    """Generate optimal posting times for the next N days."""
    template = PLATFORM_TEMPLATES.get(platform, {})
    best_times = template.get("best_posting_times_aedt", ["12:00"])
    daily_posts = POSTING_SCHEDULE.get(platform, {}).get("daily", 1)

    posting_times = []
    now = datetime.now(AEDT)

    for day_offset in range(days):
        date = now + timedelta(days=day_offset)
        times_to_use = best_times[:daily_posts]

        for time_str in times_to_use:
            hour, minute = map(int, time_str.split(":"))
            post_time = date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if post_time > now:
                posting_times.append(post_time)

    return posting_times


def generate_content_calendar(days: int = 7) -> dict:
    """Generate a content calendar balancing all pillars."""
    calendar = {}

    for platform in PLATFORM_TEMPLATES:
        calendar[platform] = []
        posting_times = get_next_posting_times(platform, days)

        for post_time in posting_times:
            # Select content pillar based on weights
            pillar = random.choices(
                list(CONTENT_PILLARS.keys()),
                weights=[p["weight"] for p in CONTENT_PILLARS.values()],
            )[0]

            # Select content type from pillar
            content_type = random.choice(CONTENT_PILLARS[pillar]["types"])

            # Select a formula
            formula = random.choice(list(CONTENT_FORMULAS.keys()))

            # Select a hook style
            hook_category = random.choice(
                PLATFORM_TEMPLATES[platform].get(
                    "content_types", ["tutorial"]
                )
            )

            calendar[platform].append({
                "scheduled_time": post_time.isoformat(),
                "pillar": pillar,
                "content_type": content_type,
                "formula": formula,
                "status": "scheduled",
            })

    return calendar


def print_calendar(calendar: dict) -> None:
    """Print calendar in readable format."""
    print("\n" + "=" * 60)
    print("PETERMAT CONTENT CALENDAR")
    print("=" * 60)

    for platform, posts in calendar.items():
        print(f"\n📱 {platform.upper()}")
        print("-" * 40)
        for post in posts:
            time = datetime.fromisoformat(post["scheduled_time"])
            print(f"  {time.strftime('%a %d %b %H:%M')}")
            print(f"    Pillar: {post['pillar']}")
            print(f"    Type: {post['content_type']}")
            print(f"    Formula: {post['formula']}")
            print()


async def main():
    """Generate and display content calendar."""
    print("Generating 7-day content calendar for PeterMat...")
    calendar = generate_content_calendar(days=7)
    print_calendar(calendar)

    # Save to file
    output_dir = Path(__file__).parent.parent / "calendars"
    output_dir.mkdir(exist_ok=True)

    import json
    output_file = output_dir / f"calendar_{datetime.now().strftime('%Y%m%d')}.json"
    with open(output_file, "w") as f:
        json.dump(calendar, f, indent=2, default=str)

    print(f"\n✅ Calendar saved to: {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
