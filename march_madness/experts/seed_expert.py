"""Seed expert — uses historical seed-vs-seed win rates."""

from march_madness.db import queries


def seed_expert(team_a: dict, team_b: dict, db_conn) -> dict:
    """Return confidence scores based on historical seed matchup data."""
    seed_a = team_a["seed"]
    seed_b = team_b["seed"]

    if seed_a == seed_b:
        return {"team_a": 0.5, "team_b": 0.5}

    # high_seed = better seed (lower number)
    if seed_a < seed_b:
        high_seed, low_seed = seed_a, seed_b
        a_is_high = True
    else:
        high_seed, low_seed = seed_b, seed_a
        a_is_high = False

    matchup = queries.get_seed_matchup(db_conn, high_seed, low_seed)
    if matchup is None:
        return {"team_a": 0.5, "team_b": 0.5}

    high_pct = matchup["high_seed_win_pct"]
    if a_is_high:
        return {"team_a": high_pct, "team_b": 1.0 - high_pct}
    else:
        return {"team_a": 1.0 - high_pct, "team_b": high_pct}
