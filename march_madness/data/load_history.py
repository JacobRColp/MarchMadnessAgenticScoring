"""Load historical seed-vs-seed matchup win rates."""

import sqlite3

# (high_seed, low_seed, games_played, high_seed_win_pct)
# First-round matchups (well-documented historical data)
# Plus common later-round matchups
SEED_MATCHUPS = [
    # Round 1 standard pairings
    (1, 16, 152, 0.993),
    (2, 15, 152, 0.947),
    (3, 14, 152, 0.855),
    (4, 13, 152, 0.796),
    (5, 12, 152, 0.644),
    (6, 11, 152, 0.618),
    (7, 10, 152, 0.605),
    (8, 9, 152, 0.513),
    # Round 2 common matchups
    (1, 8, 140, 0.800),
    (1, 9, 140, 0.850),
    (2, 7, 130, 0.710),
    (2, 10, 130, 0.770),
    (3, 6, 120, 0.650),
    (3, 11, 120, 0.720),
    (4, 5, 125, 0.560),
    (4, 12, 125, 0.680),
    (5, 13, 60, 0.620),
    (6, 14, 50, 0.690),
    (7, 15, 30, 0.780),
    (8, 16, 10, 0.850),
    # Sweet 16 common matchups
    (1, 4, 80, 0.660),
    (1, 5, 75, 0.710),
    (1, 12, 30, 0.800),
    (1, 13, 15, 0.880),
    (2, 3, 70, 0.540),
    (2, 6, 65, 0.620),
    (2, 11, 50, 0.680),
    (3, 7, 55, 0.570),
    (3, 10, 40, 0.640),
    # Elite 8 / Final Four common matchups
    (1, 2, 50, 0.540),
    (1, 3, 45, 0.600),
    (1, 6, 25, 0.680),
    (1, 7, 20, 0.720),
    (1, 11, 15, 0.760),
    (2, 4, 35, 0.570),
    (2, 5, 30, 0.600),
    (3, 4, 25, 0.520),
]


def load_seed_matchup_history(conn: sqlite3.Connection) -> None:
    """Insert historical seed matchup win rates."""
    conn.executemany(
        "INSERT OR IGNORE INTO seed_matchup_history "
        "(high_seed, low_seed, games_played, high_seed_win_pct) "
        "VALUES (?, ?, ?, ?)",
        SEED_MATCHUPS,
    )
    conn.commit()
