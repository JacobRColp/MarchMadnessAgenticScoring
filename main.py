"""March Madness Bracket Builder — entry point.

Usage:
    python main.py              # random bracket (different each run)
    python main.py --seed 42    # reproducible bracket
"""

import argparse
import os
import random

from march_madness import config
from march_madness.db import queries
from march_madness.data.load_teams import load_teams, load_bracket
from march_madness.data.load_stats import load_season_stats, load_recent_stats
from march_madness.data.load_history import load_seed_matchup_history
from march_madness.experts import EXPERTS
from march_madness.engine.bracket_engine import simulate_tournament


def main():
    parser = argparse.ArgumentParser(description="Simulate a March Madness bracket")
    parser.add_argument("--seed", type=int, help="Random seed for reproducible results")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    # Fresh database each run
    if os.path.exists(config.DB_PATH):
        os.remove(config.DB_PATH)

    conn = queries.init_db(config.DB_PATH)

    # Load all data
    load_teams(conn)
    load_bracket(conn)
    load_season_stats(conn, config.SEASON)
    load_recent_stats(conn, config.SEASON)
    load_seed_matchup_history(conn)

    # Build weights list (same order as EXPERTS)
    weights = [
        config.EXPERT_WEIGHTS["seed"],
        config.EXPERT_WEIGHTS["efficiency"],
        config.EXPERT_WEIGHTS["momentum"],
        config.EXPERT_WEIGHTS["chaos"],
    ]

    print("March Madness Bracket Builder")
    print(f"Season: {config.SEASON}")
    if args.seed is not None:
        print(f"Random seed: {args.seed}")

    # Simulate
    winners = simulate_tournament(conn, EXPERTS, weights)

    # The last game (highest game_id) determines the champion
    champion = winners[max(winners)]
    print(f"\n{'*' * 50}")
    print(f"  CHAMPION: ({champion['seed']}) {champion['team_name']}")
    print(f"{'*' * 50}")

    conn.close()


if __name__ == "__main__":
    main()
