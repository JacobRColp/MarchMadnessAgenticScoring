"""Aggregator — combines expert scores into a single pick per game."""


def aggregate(expert_results: list[dict], weights: list[float]) -> str:
    """Weighted average of expert scores. Returns 'team_a' or 'team_b'."""
    score_a = sum(r["team_a"] * w for r, w in zip(expert_results, weights))
    score_b = sum(r["team_b"] * w for r, w in zip(expert_results, weights))
    return "team_a" if score_a >= score_b else "team_b"
