"""Momentum expert — weights recent performance and shooting trends."""

from march_madness.db import queries
from march_madness.config import SEASON

TREND_BONUS = {
    "improving": 0.05,
    "stable": 0.0,
    "declining": -0.05,
}


def _momentum_score(stats: dict) -> float:
    """Compute a raw momentum score (0-1 range) for one team."""
    score = stats["last10_win_pct"]
    score += TREND_BONUS.get(stats["scoring_trend"], 0.0)

    # Small bonus for recent hot shooting (FG% above 0.44 baseline)
    recent_fg = stats.get("recent_fg_pct") or 0.0
    shoot_bonus = (recent_fg - 0.44) * 0.5
    score += max(-0.05, min(0.10, shoot_bonus))

    return max(0.0, min(1.0, score))


def momentum_expert(team_a: dict, team_b: dict, db_conn) -> dict:
    """Return confidence scores based on recent team performance."""
    stats_a = queries.get_recent_stats(db_conn, team_a["team_id"], SEASON)
    stats_b = queries.get_recent_stats(db_conn, team_b["team_id"], SEASON)

    if stats_a is None or stats_b is None:
        return {"team_a": 0.5, "team_b": 0.5}

    mom_a = _momentum_score(stats_a)
    mom_b = _momentum_score(stats_b)

    total = mom_a + mom_b
    if total == 0:
        return {"team_a": 0.5, "team_b": 0.5}

    return {"team_a": mom_a / total, "team_b": mom_b / total}
