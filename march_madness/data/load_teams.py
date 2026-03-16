"""Load 64 tournament teams and the 63-game bracket structure."""

import sqlite3

# 2025 March Madness field — 16 teams per region, (team_name, conference, seed)
TEAMS_BY_REGION = {
    "East": [
        ("Duke", "ACC", 1),
        ("Alabama", "SEC", 2),
        ("Wisconsin", "Big Ten", 3),
        ("Arizona", "Big 12", 4),
        ("Oregon", "Big Ten", 5),
        ("BYU", "Big 12", 6),
        ("St. Mary's", "WCC", 7),
        ("UConn", "Big East", 8),
        ("Baylor", "Big 12", 9),
        ("Vanderbilt", "SEC", 10),
        ("VCU", "A-10", 11),
        ("Liberty", "CUSA", 12),
        ("Yale", "Ivy", 13),
        ("Lipscomb", "ASUN", 14),
        ("Robert Morris", "Horizon", 15),
        ("American", "Patriot", 16),
    ],
    "West": [
        ("Florida", "SEC", 1),
        ("St. John's", "Big East", 2),
        ("Texas Tech", "Big 12", 3),
        ("Maryland", "Big Ten", 4),
        ("Memphis", "AAC", 5),
        ("Missouri", "SEC", 6),
        ("Kansas", "Big 12", 7),
        ("UNC", "ACC", 8),
        ("UCF", "Big 12", 9),
        ("Arkansas", "SEC", 10),
        ("Drake", "MVC", 11),
        ("Colorado St.", "MWC", 12),
        ("Grand Canyon", "WAC", 13),
        ("N. Kentucky", "Horizon", 14),
        ("Omaha", "Summit", 15),
        ("Norfolk St.", "MEAC", 16),
    ],
    "South": [
        ("Auburn", "SEC", 1),
        ("Michigan St.", "Big Ten", 2),
        ("Iowa St.", "Big 12", 3),
        ("Texas A&M", "SEC", 4),
        ("Michigan", "Big Ten", 5),
        ("Ole Miss", "SEC", 6),
        ("Marquette", "Big East", 7),
        ("Louisville", "ACC", 8),
        ("Georgia", "SEC", 9),
        ("New Mexico", "MWC", 10),
        ("San Diego St.", "MWC", 11),
        ("UC San Diego", "Big West", 12),
        ("High Point", "Big South", 13),
        ("Troy", "Sun Belt", 14),
        ("S. Dakota St.", "Summit", 15),
        ("Mt. St. Mary's", "MAAC", 16),
    ],
    "Midwest": [
        ("Houston", "Big 12", 1),
        ("Tennessee", "SEC", 2),
        ("Kentucky", "SEC", 3),
        ("Purdue", "Big Ten", 4),
        ("Clemson", "ACC", 5),
        ("Illinois", "Big Ten", 6),
        ("UCLA", "Big Ten", 7),
        ("Gonzaga", "WCC", 8),
        ("Georgia Tech", "ACC", 9),
        ("Creighton", "Big East", 10),
        ("McNeese", "Southland", 11),
        ("NC Wilmington", "CAA", 12),
        ("Vermont", "AE", 13),
        ("Montana", "Big Sky", 14),
        ("Wofford", "SoCon", 15),
        ("SIU Edwardsville", "OVC", 16),
    ],
}

# Standard first-round bracket pairings by seed (within each region)
ROUND1_SEED_PAIRS = [(1, 16), (8, 9), (5, 12), (4, 13), (6, 11), (3, 14), (7, 10), (2, 15)]


def load_teams(conn: sqlite3.Connection) -> None:
    """Insert all 64 teams. team_id assigned sequentially by region."""
    teams = []
    team_id = 1
    for region, roster in TEAMS_BY_REGION.items():
        for name, conf, seed in roster:
            teams.append((team_id, name, conf, seed, region))
            team_id += 1
    conn.executemany(
        "INSERT OR IGNORE INTO teams (team_id, team_name, conference, seed, region) VALUES (?, ?, ?, ?, ?)",
        teams,
    )
    conn.commit()


def _seed_to_team_id(region_offset: int, seed: int) -> int:
    """Map a seed to its team_id within a region. Seeds are stored at index (seed-1)."""
    return region_offset + seed


def load_bracket(conn: sqlite3.Connection) -> None:
    """Insert the 63-game bracket structure.

    Round 1: slot_a/slot_b are team_ids.
    Rounds 2-6: slot_a/slot_b are game_ids from the previous round.
    """
    games = []
    game_id = 1
    regions = list(TEAMS_BY_REGION.keys())

    # -- Round 1: 8 games per region = 32 games --
    round1_game_ids = {}  # (region_index, pair_index) -> game_id
    for r_idx, region in enumerate(regions):
        region_offset = r_idx * 16  # team_ids: 1-16, 17-32, 33-48, 49-64
        for p_idx, (seed_a, seed_b) in enumerate(ROUND1_SEED_PAIRS):
            team_a_id = region_offset + seed_a
            team_b_id = region_offset + seed_b
            games.append((game_id, 1, region, team_a_id, team_b_id))
            round1_game_ids[(r_idx, p_idx)] = game_id
            game_id += 1

    # -- Round 2: winners of adjacent round-1 games play each other --
    # Pairs: (game 0 vs game 1), (game 2 vs game 3), (game 4 vs game 5), (game 6 vs game 7)
    round2_game_ids = {}
    for r_idx, region in enumerate(regions):
        for p_idx in range(4):
            slot_a = round1_game_ids[(r_idx, p_idx * 2)]
            slot_b = round1_game_ids[(r_idx, p_idx * 2 + 1)]
            games.append((game_id, 2, region, slot_a, slot_b))
            round2_game_ids[(r_idx, p_idx)] = game_id
            game_id += 1

    # -- Round 3 (Sweet 16): winners of adjacent round-2 games --
    round3_game_ids = {}
    for r_idx, region in enumerate(regions):
        for p_idx in range(2):
            slot_a = round2_game_ids[(r_idx, p_idx * 2)]
            slot_b = round2_game_ids[(r_idx, p_idx * 2 + 1)]
            games.append((game_id, 3, region, slot_a, slot_b))
            round3_game_ids[(r_idx, p_idx)] = game_id
            game_id += 1

    # -- Round 4 (Elite 8): winners of the two Sweet 16 games per region --
    round4_game_ids = {}
    for r_idx, region in enumerate(regions):
        slot_a = round3_game_ids[(r_idx, 0)]
        slot_b = round3_game_ids[(r_idx, 1)]
        games.append((game_id, 4, region, slot_a, slot_b))
        round4_game_ids[r_idx] = game_id
        game_id += 1

    # -- Round 5 (Final Four): East vs West, South vs Midwest --
    ff_pairs = [(0, 1), (2, 3)]  # region index pairs
    round5_game_ids = {}
    for ff_idx, (r_a, r_b) in enumerate(ff_pairs):
        slot_a = round4_game_ids[r_a]
        slot_b = round4_game_ids[r_b]
        games.append((game_id, 5, None, slot_a, slot_b))
        round5_game_ids[ff_idx] = game_id
        game_id += 1

    # -- Round 6 (Championship) --
    games.append((game_id, 6, None, round5_game_ids[0], round5_game_ids[1]))

    conn.executemany(
        "INSERT OR IGNORE INTO tournament_bracket (game_id, round, region, slot_a, slot_b) VALUES (?, ?, ?, ?, ?)",
        games,
    )
    conn.commit()
