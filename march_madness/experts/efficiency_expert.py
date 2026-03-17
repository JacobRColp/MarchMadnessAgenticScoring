"""Efficiency expert — compares teams using real basketball stats."""

from march_madness.db import queries
from march_madness.config import SEASON


def _efficiency_score(stats: dict) -> float:
    """Composite efficiency score from real basketball stats.

    Components (all normalized to ~0-1 range):
      - Offensive power (avg_pts): 30%
      - Shooting efficiency (fg_pct + three_pt_pct): 25%
      - Ball security (inverse of avg_to): 15%
      - Defense (inverse of opp_avg_pts): 30%
    """
    # Offensive power: typical range ~55-90
    off_score = (stats["avg_pts"] - 55.0) / 35.0

    # Shooting efficiency: FG% (~0.38-0.52) and 3PT% (~0.28-0.42)
    shoot_score = stats["fg_pct"] * 0.6 + stats["three_pt_pct"] * 0.4

    # Ball security: fewer turnovers is better, typical range ~8-16
    to_score = 1.0 - (stats["avg_to"] - 8.0) / 8.0

    # Defense: lower opponent scoring is better, typical range ~55-85
    def_score = 1.0 - (stats["opp_avg_pts"] - 55.0) / 30.0

    composite = (
        off_score * 0.30
        + shoot_score * 0.25
        + to_score * 0.15
        + def_score * 0.30
    )
    return max(0.0, min(1.0, composite))


def efficiency_expert(team_a: dict, team_b: dict, db_conn) -> dict:
    """Return confidence scores based on composite efficiency comparison."""
    stats_a = queries.get_season_stats(db_conn, team_a["team_id"], SEASON)
    stats_b = queries.get_season_stats(db_conn, team_b["team_id"], SEASON)

    if stats_a is None or stats_b is None:
        return {"team_a": 0.5, "team_b": 0.5}

    score_a = _efficiency_score(stats_a)
    score_b = _efficiency_score(stats_b)

    diff = score_a - score_b
    # Scale so a max composite diff of ~0.5 maps to near-certainty
    confidence_a = 0.5 + diff
    confidence_a = max(0.05, min(0.95, confidence_a))

    return {"team_a": confidence_a, "team_b": 1.0 - confidence_a}
