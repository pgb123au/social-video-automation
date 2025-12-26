"""Viral hook templates proven to drive engagement."""

VIRAL_HOOKS = {
    "curiosity_gap": [
        "You won't believe what happened when...",
        "I tested {product} for 30 days and...",
        "The secret that top athletes don't want you to know",
        "Nobody is talking about this...",
        "Here's why you're doing it wrong",
        "This changed everything for me",
    ],
    "controversy": [
        "Unpopular opinion: {topic}",
        "I'm calling it - {bold_claim}",
        "Everyone is wrong about {topic}",
        "The truth about {topic} that nobody tells you",
        "Why I quit {common_thing} and what I do instead",
    ],
    "transformation": [
        "How I went from {before} to {after}",
        "30 days ago I couldn't {action}. Now...",
        "Watch this transformation",
        "Before and after using {product}",
        "My {timeframe} journey",
    ],
    "tutorial": [
        "How to {action} in {time}",
        "The only guide you need for {topic}",
        "Stop doing {wrong_thing}. Do this instead",
        "3 tips that changed my {skill}",
        "{Number} things I wish I knew before {action}",
    ],
    "storytelling": [
        "I was today years old when I learned...",
        "POV: You're {scenario}",
        "Day in my life as a {role}",
        "Things went wrong when...",
        "The moment I realised...",
    ],
    "australian_sports": [
        "Aussie cricket gear that's actually worth it",
        "Why Australian athletes are switching to...",
        "Beach training essentials for Aussie summer",
        "What your local footy coach doesn't tell you",
        "The gear that survived a full AFL season",
        "From backyard cricket to the big leagues",
        "Outback-tested, city-approved",
        "Fair dinkum sports gear review",
    ],
}

# Platform-specific hook styles
HOOK_STYLES = {
    "tiktok": {
        "max_length": 50,
        "style": "punchy",
        "emoji_use": "moderate",
        "preferred_types": ["curiosity_gap", "controversy", "tutorial"],
    },
    "instagram_reels": {
        "max_length": 60,
        "style": "polished",
        "emoji_use": "heavy",
        "preferred_types": ["transformation", "storytelling", "tutorial"],
    },
    "youtube_shorts": {
        "max_length": 70,
        "style": "informative",
        "emoji_use": "light",
        "preferred_types": ["tutorial", "curiosity_gap", "transformation"],
    },
    "facebook": {
        "max_length": 80,
        "style": "conversational",
        "emoji_use": "moderate",
        "preferred_types": ["storytelling", "australian_sports", "transformation"],
    },
}
