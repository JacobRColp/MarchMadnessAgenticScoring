"""Aggregator — combines expert scores into a single pick per game."""

import random


def aggregate(expert_results: list[dict], weights: list[float]) -> str:
    """Weighted average of expert scores. Returns 'team_a' or 'team_b'."""
    score_a = sum(r["team_a"] * w for r, w in zip(expert_results, weights))
    score_b = sum(r["team_b"] * w for r, w in zip(expert_results, weights))
    return "team_a" if score_a >= score_b else "team_b"


def aggregate_stochastic(expert_results: list[dict], weights: list[float]) -> str:
    """Monte Carlo aggregator — samples winner proportional to weighted scores."""
    score_a = sum(r["team_a"] * w for r, w in zip(expert_results, weights))
    total = sum(
        sum(r[k] * w for r, w in zip(expert_results, weights))
        for k in ["team_a", "team_b"]
    )
    prob_a = score_a / total
    return "team_a" if random.random() < prob_a else "team_b"
