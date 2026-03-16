"""Momentum expert — weights recent performance and conference tournament results."""

from march_madness.db import queries
from march_madness.config import SEASON

CONF_TOURNEY_BONUS = {
    "champion": 0.15,
    "finalist": 0.10,
    "semis": 0.05,
    "early_exit": 0.0,
}

TREND_BONUS = {
    "improving": 0.05,
    "stable": 0.0,
    "declining": -0.05,
}


def _momentum_score(stats: dict) -> float:
    """Compute a raw momentum score (0-1 range) for one team."""
    score = stats["last10_win_pct"]
    score += CONF_TOURNEY_BONUS.get(stats["conf_tourney_result"], 0.0)
    score += TREND_BONUS.get(stats["scoring_trend"], 0.0)
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
