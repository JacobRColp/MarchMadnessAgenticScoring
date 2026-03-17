"""Bracket engine — simulates the entire tournament round by round."""

import sqlite3

from march_madness.db import queries
from march_madness.engine.aggregator import aggregate, aggregate_stochastic
from march_madness.config import ROUND_NAMES, EXPERT_WEIGHTS


def simulate_tournament(
    conn: sqlite3.Connection,
    experts: list,
    weights: list[float],
    stochastic: bool = False,
) -> dict:
    """Run the full tournament simulation (First Four + 6 rounds).

    Returns a dict mapping game_id -> winning team dict.
    """
    winners = {}  # game_id -> team dict

    for round_num in range(0, 7):
        matchups = queries.get_round_matchups(conn, round_num)
        if not matchups:
            continue

        round_name = ROUND_NAMES.get(round_num, f"Round {round_num}")
        print(f"\n{'=' * 50}")
        print(f"  {round_name}")
        print(f"{'=' * 50}")

        for game in matchups:
            game_id = game["game_id"]
            slot_a = game["slot_a"]
            slot_b = game["slot_b"]

            # Resolve slots to team dicts.
            # Check winners first (handles First Four game_ids in Round 1
            # and later-round game_ids). Fall back to direct team lookup.
            if slot_a in winners:
                team_a = winners[slot_a]
            else:
                team_a = queries.get_team(conn, slot_a)

            if slot_b in winners:
                team_b = winners[slot_b]
            else:
                team_b = queries.get_team(conn, slot_b)

            # Run all experts
            results = [expert(team_a, team_b, conn) for expert in experts]

            # Aggregate and pick winner
            agg_fn = aggregate_stochastic if stochastic else aggregate
            winner_key = agg_fn(results, weights)
            winner = team_a if winner_key == "team_a" else team_b
            loser = team_b if winner_key == "team_a" else team_a

            winners[game_id] = winner

            # Display
            region = f" [{game['region']}]" if game["region"] else ""
            print(
                f"  ({team_a['seed']}) {team_a['team_name']:<20s} vs "
                f"({team_b['seed']}) {team_b['team_name']:>20s}"
                f"  ->  {winner['team_name']}{region}"
            )

    return winners
