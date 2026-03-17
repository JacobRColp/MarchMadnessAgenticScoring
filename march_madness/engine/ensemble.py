"""Ensemble runner — runs the stochastic tournament many times and picks
winners by plurality vote to reduce single-run bias."""

from collections import Counter

from march_madness.config import ROUND_NAMES
from march_madness.engine.bracket_engine import simulate_tournament


def run_ensemble(conn, experts, weights, iterations=100):
    """Run *iterations* stochastic tournaments and return consensus results.

    Returns a dict with:
        consensus_winners : dict[game_id -> team_dict]  (same shape as
            simulate_tournament, so callers can use it interchangeably)
        win_counts : dict[game_id -> Counter[team_name -> count]]
    """
    # Collect per-game vote tallies: game_id -> Counter(team_name -> count)
    vote_tallies = {}          # game_id -> Counter
    team_lookup = {}           # (game_id, team_name) -> team_dict

    for i in range(iterations):
        winners = simulate_tournament(
            conn, experts, weights, stochastic=True, quiet=True,
        )
        for game_id, team in winners.items():
            name = team["team_name"]
            vote_tallies.setdefault(game_id, Counter())[name] += 1
            team_lookup[(game_id, name)] = team

    # Build consensus bracket (per-slot plurality winner)
    consensus_winners = {}
    for game_id, tally in vote_tallies.items():
        best_name = tally.most_common(1)[0][0]
        consensus_winners[game_id] = team_lookup[(game_id, best_name)]

    # Build round -> [game_ids] mapping from the bracket table
    round_games = {}
    rows = conn.execute(
        "SELECT game_id, round FROM tournament_bracket ORDER BY round, game_id"
    ).fetchall()
    for row in rows:
        round_games.setdefault(row["round"], []).append(row["game_id"])

    # Display summary with win percentages
    print(f"\nEnsemble results ({iterations} iterations)")
    for round_num in sorted(round_games):
        game_ids = round_games[round_num]
        # Only show rounds that produced winners
        if not any(gid in consensus_winners for gid in game_ids):
            continue
        round_name = ROUND_NAMES.get(round_num, f"Round {round_num}")
        print(f"\n{'=' * 50}")
        print(f"  {round_name}")
        print(f"{'=' * 50}")
        for gid in game_ids:
            if gid not in consensus_winners:
                continue
            team = consensus_winners[gid]
            tally = vote_tallies[gid]
            wins = tally[team["team_name"]]
            pct = wins / iterations * 100
            print(
                f"  ({team['seed']}) {team['team_name']:<24s}"
                f"  {wins}/{iterations}  ({pct:.0f}%)"
            )

    return {
        "consensus_winners": consensus_winners,
        "win_counts": dict(vote_tallies),
    }
