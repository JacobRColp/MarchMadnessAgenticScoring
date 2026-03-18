"""Central configuration for the March Madness Bracket Builder."""

from pathlib import Path

DB_PATH = "march_madness.db"
SEASON = 2026

# CSV data paths
_PROJECT_ROOT = Path(__file__).parent.parent
TEAM_SUMMARY_CSV = _PROJECT_ROOT / "notebooks" / "march_madness_2026_team_summary.csv"
RAW_BOXSCORES_CSV = _PROJECT_ROOT / "notebooks" / "march_madness_2026_raw_boxscores.csv"

# Women's bracket data
WOMENS_TEAM_SUMMARY_CSV = _PROJECT_ROOT / "notebooks" / "womens_march_madness_2026_team_summary.csv"
WOMENS_RAW_BOXSCORES_CSV = _PROJECT_ROOT / "notebooks" / "womens_march_madness_2026_raw_boxscores.csv"
WOMENS_REGIONS = ["Fort Worth 1", "Fort Worth 2", "Sacramento 1", "Sacramento 2"]

# Expert weights (must sum to 1.0)
EXPERT_WEIGHTS = {
    "seed": 0.25,
    "efficiency": 0.40,
    "momentum": 0.25,
    "chaos": 0.10,
}

ROUND_NAMES = {
    0: "First Four",
    1: "Round of 64",
    2: "Round of 32",
    3: "Sweet 16",
    4: "Elite 8",
    5: "Final Four",
    6: "Championship",
}

REGIONS = ["East", "West", "South", "Midwest"]


def set_womens():
    """Switch all config to use women's bracket data."""
    global TEAM_SUMMARY_CSV, RAW_BOXSCORES_CSV, REGIONS, DB_PATH
    TEAM_SUMMARY_CSV = WOMENS_TEAM_SUMMARY_CSV
    RAW_BOXSCORES_CSV = WOMENS_RAW_BOXSCORES_CSV
    REGIONS = WOMENS_REGIONS
    DB_PATH = "womens_march_madness.db"
