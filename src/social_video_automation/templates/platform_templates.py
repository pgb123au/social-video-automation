"""Platform-specific content templates for PeterMat."""

PLATFORM_TEMPLATES = {
    "tiktok": {
        "video_specs": {
            "aspect_ratio": "9:16",
            "max_duration": 180,
            "optimal_duration": 30,
            "resolution": "1080x1920",
        },
        "caption_template": """{hook}

{body}

{cta}

{hashtags}""",
        "hashtag_strategy": {
            "total": 5,
            "branded": 1,  # #PeterMat
            "niche": 2,    # #AustralianSports #CricketGear
            "trending": 2, # Platform trending tags
        },
        "best_posting_times_aedt": ["19:00", "12:00", "21:00"],
        "content_types": [
            "quick_tip",
            "product_demo",
            "behind_scenes",
            "user_generated",
            "trend_participation",
        ],
    },
    "instagram_reels": {
        "video_specs": {
            "aspect_ratio": "9:16",
            "max_duration": 90,
            "optimal_duration": 15,
            "resolution": "1080x1920",
        },
        "caption_template": """{hook}

{body}

.
.
.
{hashtags}

{cta}""",
        "hashtag_strategy": {
            "total": 20,
            "branded": 2,
            "niche": 10,
            "trending": 5,
            "location": 3,  # #Sydney #Melbourne #Australia
        },
        "best_posting_times_aedt": ["12:00", "17:00", "20:00"],
        "content_types": [
            "aesthetic_showcase",
            "transformation",
            "tutorial",
            "lifestyle",
            "collaboration",
        ],
    },
    "youtube_shorts": {
        "video_specs": {
            "aspect_ratio": "9:16",
            "max_duration": 60,
            "optimal_duration": 45,
            "resolution": "1080x1920",
        },
        "caption_template": """{hook}

{body}

{cta}

#shorts {hashtags}""",
        "hashtag_strategy": {
            "total": 5,
            "branded": 1,
            "niche": 3,
            "trending": 1,
        },
        "best_posting_times_aedt": ["15:00", "18:00", "20:00"],
        "content_types": [
            "educational",
            "how_to",
            "review",
            "comparison",
            "myth_busting",
        ],
    },
    "facebook": {
        "video_specs": {
            "aspect_ratio": "9:16",
            "max_duration": 60,
            "optimal_duration": 30,
            "resolution": "1080x1920",
        },
        "caption_template": """{hook}

{body}

{cta}

{hashtags}""",
        "hashtag_strategy": {
            "total": 3,
            "branded": 1,
            "niche": 2,
            "trending": 0,
        },
        "best_posting_times_aedt": ["13:00", "16:00", "19:00"],
        "content_types": [
            "community_focused",
            "local_events",
            "testimonials",
            "educational",
            "live_events",
        ],
    },
}

# PeterMat branded hashtags
BRANDED_HASHTAGS = [
    "#PeterMat",
    "#BornFromTheLand",
    "#BuiltForPerformance",
    "#AussieAthlete",
    "#PeterMatGear",
]

# Australian sports niche hashtags
NICHE_HASHTAGS = {
    "cricket": [
        "#AustraliaCricket",
        "#CricketAustralia",
        "#CricketGear",
        "#TestCricket",
        "#BBL",
    ],
    "afl": [
        "#AFL",
        "#AFLFooty",
        "#AussieRules",
        "#FootyGear",
    ],
    "rugby": [
        "#RugbyAustralia",
        "#Wallabies",
        "#NRL",
        "#RugbyUnion",
    ],
    "swimming": [
        "#SwimAustralia",
        "#AussieSwimmers",
        "#SwimmingLife",
    ],
    "general": [
        "#AustralianSports",
        "#AussieSport",
        "#AustralianAthlete",
        "#SportAustralia",
        "#MadeInAustralia",
        "#AustralianMade",
        "#SupportLocal",
    ],
}

# Location hashtags
LOCATION_HASHTAGS = [
    "#Sydney",
    "#Melbourne",
    "#Brisbane",
    "#Perth",
    "#Adelaide",
    "#Australia",
    "#DownUnder",
    "#Straya",
]
