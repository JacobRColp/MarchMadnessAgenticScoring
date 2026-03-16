"""Efficiency expert — compares adjusted offensive and defensive efficiency."""

from march_madness.db import queries
from march_madness.config import SEASON


def efficiency_expert(team_a: dict, team_b: dict, db_conn) -> dict:
    """Return confidence scores based on net efficiency comparison."""
    stats_a = queries.get_season_stats(db_conn, team_a["team_id"], SEASON)
    stats_b = queries.get_season_stats(db_conn, team_b["team_id"], SEASON)

    if stats_a is None or stats_b is None:
        return {"team_a": 0.5, "team_b": 0.5}

    net_a = stats_a["adj_eff_off"] - stats_a["adj_eff_def"]
    net_b = stats_b["adj_eff_off"] - stats_b["adj_eff_def"]

    diff = net_a - net_b
    # Scale: 40 points of net efficiency difference maps to near-certainty
    score_a = 0.5 + diff / 80.0
    score_a = max(0.05, min(0.95, score_a))

    return {"team_a": score_a, "team_b": 1.0 - score_a}
