"""Chaos expert — injects controlled randomness to generate bracket-busting upsets."""

import random


def chaos_expert(team_a: dict, team_b: dict, db_conn) -> dict:
    """Return confidence scores with random upset potential.

    Larger seed gaps make upsets less likely but still possible.
    """
    seed_a = team_a["seed"]
    seed_b = team_b["seed"]
    seed_diff = abs(seed_a - seed_b)

    if seed_diff == 0:
        # Equal seeds — pure coin flip with slight random lean
        score_a = random.uniform(0.35, 0.65)
        return {"team_a": score_a, "team_b": 1.0 - score_a}

    # Determine who's the favorite (lower seed = better)
    a_is_favorite = seed_a < seed_b

    # Upset probability decreases with seed gap
    # 1 seed diff -> ~0.45 upset chance, 15 seed diff -> ~0.08
    upset_chance = max(0.08, 0.50 - seed_diff * 0.03)

    if random.random() < upset_chance:
        # Upset! Favor the underdog
        underdog_score = random.uniform(0.55, 0.80)
    else:
        # Chalk — favor the favorite
        underdog_score = random.uniform(0.20, 0.45)

    if a_is_favorite:
        return {"team_a": 1.0 - underdog_score, "team_b": underdog_score}
    else:
        return {"team_a": underdog_score, "team_b": 1.0 - underdog_score}
