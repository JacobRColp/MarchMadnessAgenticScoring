"""Load tournament teams from CSV and build the bracket structure.

Handles 68 teams including 4 First Four play-in matchups.
"""

import csv
import sqlite3
from collections import defaultdict

from march_madness import config

# Standard first-round bracket pairings by seed (within each region)
ROUND1_SEED_PAIRS = [(1, 16), (8, 9), (5, 12), (4, 13), (6, 11), (3, 14), (7, 10), (2, 15)]

# Game IDs start at 1001 to avoid collision with team_ids (1-68)
_GAME_ID_START = 1001


def load_teams(conn: sqlite3.Connection) -> None:
    """Read teams from CSV, detect First Four, insert all 68 teams."""
    teams_by_region_seed = defaultdict(list)

    with open(config.TEAM_SUMMARY_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            teams_by_region_seed[(row["region"], int(row["seed"]))].append(row)

    # Detect First Four: any (region, seed) with 2 teams
    first_four_keys = {
        key for key, teams in teams_by_region_seed.items() if len(teams) == 2
    }

    # Assign team_ids sequentially, ordered by region then seed
    team_id = 1
    rows_to_insert = []
    for region in config.REGIONS:
        for seed in range(1, 17):
            key = (region, seed)
            for team_row in teams_by_region_seed.get(key, []):
                is_ff = 1 if key in first_four_keys else 0
                rows_to_insert.append((
                    team_id,
                    team_row["team"],
                    int(team_row["espn_id"]),
                    seed,
                    region,
                    is_ff,
                ))
                team_id += 1

    conn.executemany(
        "INSERT OR IGNORE INTO teams "
        "(team_id, team_name, espn_id, seed, region, is_first_four) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        rows_to_insert,
    )
    conn.commit()


def load_bracket(conn: sqlite3.Connection) -> None:
    """Build the tournament bracket: First Four (round 0) + 63 main games.

    Round 0: slot_a/slot_b are team_ids of play-in teams.
    Round 1: slot_a/slot_b are team_ids OR First Four game_ids.
    Rounds 2-6: slot_a/slot_b are game_ids from the previous round.
    """
    games = []
    game_id = _GAME_ID_START

    # -- Round 0: First Four play-in games --
    # Find pairs of teams that share the same (region, seed) with is_first_four=1
    ff_rows = conn.execute(
        "SELECT team_id, seed, region FROM teams WHERE is_first_four = 1 "
        "ORDER BY region, seed, team_id"
    ).fetchall()

    # Group into pairs
    ff_pairs = defaultdict(list)
    for row in ff_rows:
        ff_pairs[(row["region"], row["seed"])].append(row["team_id"])

    first_four_game_ids = {}  # (region, seed) -> game_id
    for (region, seed), team_ids in ff_pairs.items():
        if len(team_ids) == 2:
            games.append((game_id, 0, region, team_ids[0], team_ids[1]))
            first_four_game_ids[(region, seed)] = game_id
            game_id += 1

    # -- Build lookup: (region, seed) -> team_id for non-First-Four teams --
    non_ff_rows = conn.execute(
        "SELECT team_id, seed, region FROM teams WHERE is_first_four = 0 "
        "ORDER BY region, seed"
    ).fetchall()

    seed_to_team = {}  # (region, seed) -> team_id
    for row in non_ff_rows:
        seed_to_team[(row["region"], row["seed"])] = row["team_id"]

    # -- Round 1: 8 games per region = 32 games --
    round1_game_ids = {}  # (region_index, pair_index) -> game_id
    for r_idx, region in enumerate(config.REGIONS):
        for p_idx, (seed_a, seed_b) in enumerate(ROUND1_SEED_PAIRS):
            # Resolve each seed to either a team_id or a First Four game_id
            key_a = (region, seed_a)
            key_b = (region, seed_b)

            slot_a = first_four_game_ids.get(key_a, seed_to_team.get(key_a))
            slot_b = first_four_game_ids.get(key_b, seed_to_team.get(key_b))

            if slot_a is None or slot_b is None:
                raise ValueError(
                    f"Cannot resolve bracket slot for {region} seeds {seed_a} vs {seed_b}"
                )

            games.append((game_id, 1, region, slot_a, slot_b))
            round1_game_ids[(r_idx, p_idx)] = game_id
            game_id += 1

    # -- Round 2: winners of adjacent round-1 games --
    round2_game_ids = {}
    for r_idx, region in enumerate(config.REGIONS):
        for p_idx in range(4):
            slot_a = round1_game_ids[(r_idx, p_idx * 2)]
            slot_b = round1_game_ids[(r_idx, p_idx * 2 + 1)]
            games.append((game_id, 2, region, slot_a, slot_b))
            round2_game_ids[(r_idx, p_idx)] = game_id
            game_id += 1

    # -- Round 3 (Sweet 16) --
    round3_game_ids = {}
    for r_idx, region in enumerate(config.REGIONS):
        for p_idx in range(2):
            slot_a = round2_game_ids[(r_idx, p_idx * 2)]
            slot_b = round2_game_ids[(r_idx, p_idx * 2 + 1)]
            games.append((game_id, 3, region, slot_a, slot_b))
            round3_game_ids[(r_idx, p_idx)] = game_id
            game_id += 1

    # -- Round 4 (Elite 8) --
    round4_game_ids = {}
    for r_idx, region in enumerate(config.REGIONS):
        slot_a = round3_game_ids[(r_idx, 0)]
        slot_b = round3_game_ids[(r_idx, 1)]
        games.append((game_id, 4, region, slot_a, slot_b))
        round4_game_ids[r_idx] = game_id
        game_id += 1

    # -- Round 5 (Final Four): East vs West, South vs Midwest --
    ff_matchups = [(0, 1), (2, 3)]
    round5_game_ids = {}
    for ff_idx, (r_a, r_b) in enumerate(ff_matchups):
        slot_a = round4_game_ids[r_a]
        slot_b = round4_game_ids[r_b]
        games.append((game_id, 5, None, slot_a, slot_b))
        round5_game_ids[ff_idx] = game_id
        game_id += 1

    # -- Round 6 (Championship) --
    games.append((game_id, 6, None, round5_game_ids[0], round5_game_ids[1]))

    conn.executemany(
        "INSERT OR IGNORE INTO tournament_bracket "
        "(game_id, round, region, slot_a, slot_b) VALUES (?, ?, ?, ?, ?)",
        games,
    )
    conn.commit()
