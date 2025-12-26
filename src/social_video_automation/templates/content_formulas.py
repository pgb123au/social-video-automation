"""Proven content formulas for viral social media content."""

CONTENT_FORMULAS = {
    "problem_agitate_solve": {
        "description": "Identify a problem, agitate it, then present solution",
        "structure": [
            "Hook: State the common problem",
            "Agitate: Show why it's worse than they think",
            "Solve: Present PeterMat product as solution",
            "CTA: Drive to action",
        ],
        "example": {
            "hook": "Your cricket bat grip is costing you runs",
            "agitate": "Every slip, every missed shot - it adds up",
            "solve": "PeterMat grips are designed for Aussie conditions",
            "cta": "Link in bio for match-ready gear",
        },
        "best_for": ["product_launch", "pain_point_content"],
    },
    "before_after_bridge": {
        "description": "Show transformation with product as the bridge",
        "structure": [
            "Before: Show the struggle",
            "After: Show the success",
            "Bridge: Explain how PeterMat helped",
        ],
        "example": {
            "before": "Struggling with beach training in summer",
            "after": "Now I train harder, longer",
            "bridge": "PeterMat's cooling gear changed the game",
        },
        "best_for": ["transformation", "testimonial"],
    },
    "hook_story_offer": {
        "description": "Hook attention, tell a story, make an offer",
        "structure": [
            "Hook: Pattern interrupt opening",
            "Story: Personal or customer story",
            "Offer: Clear value proposition",
        ],
        "example": {
            "hook": "I almost gave up on competitive swimming",
            "story": "Until I found gear that could handle Australian chlorine",
            "offer": "Get 20% off your first PeterMat order",
        },
        "best_for": ["storytelling", "promotional"],
    },
    "myth_buster": {
        "description": "Challenge common beliefs with facts",
        "structure": [
            "Myth: State the common belief",
            "Truth: Reveal the reality",
            "Proof: Show evidence/demonstration",
            "Action: What to do instead",
        ],
        "example": {
            "myth": "Expensive gear = better performance",
            "truth": "It's about gear designed for YOUR conditions",
            "proof": "PeterMat tested in 45°C Australian summers",
            "action": "Stop overpaying. Start performing.",
        },
        "best_for": ["educational", "controversy"],
    },
    "listicle": {
        "description": "Numbered list of tips, products, or ideas",
        "structure": [
            "Hook: Promise specific number of items",
            "List: Deliver each item with value",
            "Recap: Summarise key takeaway",
            "CTA: Next step",
        ],
        "example": {
            "hook": "5 Aussie sports essentials for summer",
            "list": ["UV-protective gear", "Cooling fabrics", "etc."],
            "recap": "Summer sorted with PeterMat",
            "cta": "Save this for later",
        },
        "best_for": ["educational", "product_showcase"],
    },
    "day_in_life": {
        "description": "Show authentic behind-the-scenes content",
        "structure": [
            "Morning: Start of routine",
            "Activity: Main sports/training content",
            "PeterMat moment: Natural product integration",
            "Evening: Wind down with brand mention",
        ],
        "example": {
            "morning": "5am beach run",
            "activity": "Afternoon cricket training",
            "petermat": "Love how this gear handles both",
            "evening": "Recovery with the right kit",
        },
        "best_for": ["lifestyle", "authentic_content"],
    },
}

# Content pillars for PeterMat
CONTENT_PILLARS = {
    "product": {
        "weight": 0.3,  # 30% of content
        "types": [
            "product_showcase",
            "product_demo",
            "new_arrivals",
            "feature_highlight",
        ],
    },
    "education": {
        "weight": 0.25,
        "types": [
            "tips_and_tricks",
            "how_to_guides",
            "gear_maintenance",
            "sport_techniques",
        ],
    },
    "community": {
        "weight": 0.25,
        "types": [
            "user_generated",
            "athlete_spotlights",
            "customer_stories",
            "local_events",
        ],
    },
    "entertainment": {
        "weight": 0.15,
        "types": [
            "trends",
            "memes",
            "challenges",
            "behind_scenes",
        ],
    },
    "brand": {
        "weight": 0.05,
        "types": [
            "brand_story",
            "values",
            "sustainability",
            "team",
        ],
    },
}

# Optimal posting frequency
POSTING_SCHEDULE = {
    "tiktok": {"daily": 2, "weekly": 14},
    "instagram_reels": {"daily": 1, "weekly": 7},
    "youtube_shorts": {"daily": 1, "weekly": 5},
    "facebook": {"daily": 1, "weekly": 5},
}

# Engagement tactics
ENGAGEMENT_TACTICS = {
    "call_to_action": [
        "Double tap if you agree!",
        "Save this for later",
        "Tag someone who needs this",
        "Follow for more Aussie sports tips",
        "Comment your favourite below",
        "Share with your team",
        "Link in bio",
        "Drop a comment if you've tried this",
    ],
    "questions": [
        "What's your go-to training gear?",
        "Have you tried this?",
        "Team cricket or team footy?",
        "Where do you train in summer?",
        "What's missing from your gear bag?",
    ],
    "controversy_starters": [
        "Agree or disagree?",
        "Hot take:",
        "Unpopular opinion:",
        "Change my mind:",
    ],
}
