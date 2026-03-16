"""Central configuration for the March Madness Bracket Builder."""

DB_PATH = "march_madness.db"
SEASON = 2025

# Expert weights (must sum to 1.0)
EXPERT_WEIGHTS = {
    "seed": 0.15,
    "efficiency": 0.40,
    "momentum": 0.20,
    "chaos": 0.25,
}

ROUND_NAMES = {
    1: "Round of 64",
    2: "Round of 32",
    3: "Sweet 16",
    4: "Elite 8",
    5: "Final Four",
    6: "Championship",
}

REGIONS = ["East", "West", "South", "Midwest"]
