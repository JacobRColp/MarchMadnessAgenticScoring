"""Load season stats and recent stats for all 64 teams.

Stats are hardcoded and correlated with seed — higher seeds have better numbers.
"""

import sqlite3

# (team_id, adj_eff_off, adj_eff_def, adj_tempo, win_pct, sos)
# Ordered by team_id 1-64 (East 1-16, West 17-32, South 33-48, Midwest 49-64)
SEASON_STATS = [
    # East
    (1, 121.5, 89.2, 68.1, 0.91, 11.5),   # Duke (1)
    (2, 120.8, 90.5, 70.3, 0.88, 10.8),   # Alabama (2)
    (3, 117.2, 92.1, 65.4, 0.85, 9.2),    # Wisconsin (3)
    (4, 118.0, 93.5, 68.7, 0.83, 9.8),    # Arizona (4)
    (5, 114.5, 94.8, 67.2, 0.79, 8.1),    # Oregon (5)
    (6, 113.8, 95.0, 66.5, 0.77, 7.5),    # BYU (6)
    (7, 112.0, 96.2, 64.8, 0.75, 6.9),    # St. Mary's (7)
    (8, 111.2, 97.5, 69.0, 0.72, 7.2),    # UConn (8)
    (9, 110.5, 97.8, 67.8, 0.70, 6.5),    # Baylor (9)
    (10, 109.0, 98.5, 66.2, 0.68, 5.8),   # Vanderbilt (10)
    (11, 108.2, 99.0, 68.5, 0.65, 4.5),   # VCU (11)
    (12, 107.5, 99.8, 69.2, 0.72, 3.2),   # Liberty (12)
    (13, 105.8, 100.5, 65.0, 0.70, 2.0),  # Yale (13)
    (14, 103.2, 102.0, 67.5, 0.62, 0.5),  # Lipscomb (14)
    (15, 100.5, 104.8, 66.0, 0.55, -1.2), # Robert Morris (15)
    (16, 97.0, 107.5, 68.0, 0.48, -3.5),  # American (16)
    # West
    (17, 122.0, 88.5, 69.5, 0.92, 12.0),  # Florida (1)
    (18, 119.5, 91.0, 70.0, 0.87, 10.2),  # St. John's (2)
    (19, 116.8, 92.8, 66.0, 0.84, 9.5),   # Texas Tech (3)
    (20, 115.5, 93.0, 67.8, 0.82, 8.8),   # Maryland (4)
    (21, 114.0, 95.2, 71.5, 0.78, 7.8),   # Memphis (5)
    (22, 112.5, 95.5, 67.0, 0.76, 7.0),   # Missouri (6)
    (23, 111.8, 96.5, 68.2, 0.74, 6.5),   # Kansas (7)
    (24, 110.0, 97.0, 69.5, 0.71, 6.8),   # UNC (8)
    (25, 109.5, 98.0, 68.0, 0.69, 6.0),   # UCF (9)
    (26, 108.8, 98.2, 70.5, 0.67, 5.5),   # Arkansas (10)
    (27, 107.0, 99.5, 66.8, 0.66, 4.0),   # Drake (11)
    (28, 106.5, 100.0, 67.5, 0.71, 2.8),  # Colorado St. (12)
    (29, 104.5, 101.0, 65.5, 0.68, 1.5),  # Grand Canyon (13)
    (30, 102.0, 103.0, 66.5, 0.60, -0.5), # N. Kentucky (14)
    (31, 99.5, 105.5, 67.0, 0.53, -2.0),  # Omaha (15)
    (32, 96.5, 108.0, 69.0, 0.46, -4.0),  # Norfolk St. (16)
    # South
    (33, 123.0, 88.0, 67.5, 0.93, 12.5),  # Auburn (1)
    (34, 119.0, 90.8, 69.0, 0.86, 10.5),  # Michigan St. (2)
    (35, 117.5, 91.5, 66.5, 0.85, 9.8),   # Iowa St. (3)
    (36, 116.0, 93.2, 68.0, 0.82, 9.0),   # Texas A&M (4)
    (37, 113.5, 94.5, 69.5, 0.78, 8.2),   # Michigan (5)
    (38, 112.8, 95.8, 67.5, 0.76, 7.2),   # Ole Miss (6)
    (39, 111.5, 96.0, 68.8, 0.74, 6.8),   # Marquette (7)
    (40, 110.8, 97.2, 70.0, 0.71, 6.5),   # Louisville (8)
    (41, 109.2, 98.0, 67.0, 0.69, 5.8),   # Georgia (9)
    (42, 108.5, 98.8, 69.5, 0.67, 5.0),   # New Mexico (10)
    (43, 107.8, 99.2, 68.0, 0.66, 4.2),   # San Diego St. (11)
    (44, 106.0, 100.5, 66.5, 0.70, 2.5),  # UC San Diego (12)
    (45, 104.0, 101.5, 67.0, 0.67, 1.8),  # High Point (13)
    (46, 102.5, 102.5, 68.5, 0.61, 0.0),  # Troy (14)
    (47, 100.0, 105.0, 66.5, 0.54, -1.5), # S. Dakota St. (15)
    (48, 96.0, 108.5, 67.5, 0.45, -4.5),  # Mt. St. Mary's (16)
    # Midwest
    (49, 121.0, 87.5, 66.5, 0.92, 12.2),  # Houston (1)
    (50, 120.0, 90.0, 68.5, 0.89, 11.0),  # Tennessee (2)
    (51, 118.5, 91.8, 69.0, 0.86, 10.0),  # Kentucky (3)
    (52, 116.5, 92.5, 67.5, 0.83, 9.5),   # Purdue (4)
    (53, 114.2, 94.0, 66.8, 0.80, 8.5),   # Clemson (5)
    (54, 113.0, 95.2, 68.0, 0.77, 7.5),   # Illinois (6)
    (55, 112.2, 96.0, 69.2, 0.75, 7.0),   # UCLA (7)
    (56, 111.0, 96.8, 70.5, 0.73, 6.8),   # Gonzaga (8)
    (57, 109.8, 97.5, 67.5, 0.70, 6.2),   # Georgia Tech (9)
    (58, 108.0, 98.5, 68.5, 0.68, 5.5),   # Creighton (10)
    (59, 107.5, 99.0, 69.0, 0.67, 3.8),   # McNeese (11)
    (60, 106.2, 100.2, 66.0, 0.70, 2.5),  # NC Wilmington (12)
    (61, 104.8, 101.0, 65.5, 0.69, 2.0),  # Vermont (13)
    (62, 101.5, 103.5, 67.0, 0.58, -1.0), # Montana (14)
    (63, 99.0, 105.2, 66.5, 0.52, -2.5),  # Wofford (15)
    (64, 95.5, 109.0, 68.0, 0.44, -5.0),  # SIU Edwardsville (16)
]

# (team_id, last10_win_pct, conf_tourney_result, scoring_trend)
RECENT_STATS = [
    # East
    (1, 0.90, "champion", "improving"),
    (2, 0.80, "finalist", "stable"),
    (3, 0.80, "semis", "improving"),
    (4, 0.70, "semis", "stable"),
    (5, 0.70, "early_exit", "improving"),
    (6, 0.60, "early_exit", "stable"),
    (7, 0.80, "champion", "stable"),
    (8, 0.60, "early_exit", "declining"),
    (9, 0.70, "semis", "stable"),
    (10, 0.50, "early_exit", "improving"),
    (11, 0.70, "champion", "improving"),
    (12, 0.80, "champion", "stable"),
    (13, 0.70, "champion", "stable"),
    (14, 0.60, "champion", "improving"),
    (15, 0.50, "champion", "stable"),
    (16, 0.40, "early_exit", "declining"),
    # West
    (17, 0.90, "champion", "improving"),
    (18, 0.80, "champion", "stable"),
    (19, 0.70, "semis", "stable"),
    (20, 0.80, "finalist", "improving"),
    (21, 0.70, "champion", "stable"),
    (22, 0.60, "early_exit", "declining"),
    (23, 0.60, "early_exit", "stable"),
    (24, 0.50, "early_exit", "declining"),
    (25, 0.70, "semis", "improving"),
    (26, 0.60, "early_exit", "stable"),
    (27, 0.80, "champion", "improving"),
    (28, 0.70, "champion", "stable"),
    (29, 0.80, "champion", "improving"),
    (30, 0.50, "champion", "stable"),
    (31, 0.40, "champion", "declining"),
    (32, 0.30, "early_exit", "declining"),
    # South
    (33, 1.00, "champion", "improving"),
    (34, 0.80, "finalist", "stable"),
    (35, 0.70, "semis", "stable"),
    (36, 0.70, "semis", "improving"),
    (37, 0.60, "early_exit", "declining"),
    (38, 0.70, "early_exit", "improving"),
    (39, 0.60, "early_exit", "stable"),
    (40, 0.70, "semis", "improving"),
    (41, 0.60, "early_exit", "stable"),
    (42, 0.50, "early_exit", "declining"),
    (43, 0.70, "finalist", "stable"),
    (44, 0.80, "champion", "improving"),
    (45, 0.70, "champion", "stable"),
    (46, 0.50, "champion", "declining"),
    (47, 0.60, "champion", "stable"),
    (48, 0.40, "finalist", "declining"),
    # Midwest
    (49, 0.90, "champion", "stable"),
    (50, 0.80, "finalist", "improving"),
    (51, 0.70, "semis", "improving"),
    (52, 0.80, "semis", "stable"),
    (53, 0.70, "early_exit", "stable"),
    (54, 0.60, "early_exit", "improving"),
    (55, 0.50, "early_exit", "declining"),
    (56, 0.70, "champion", "stable"),
    (57, 0.60, "semis", "improving"),
    (58, 0.50, "early_exit", "stable"),
    (59, 0.80, "champion", "improving"),
    (60, 0.70, "champion", "stable"),
    (61, 0.80, "champion", "improving"),
    (62, 0.50, "champion", "stable"),
    (63, 0.40, "champion", "declining"),
    (64, 0.30, "early_exit", "declining"),
]


def load_season_stats(conn: sqlite3.Connection, season: int) -> None:
    """Insert season stats for all 64 teams."""
    rows = [(tid, season, off, dfn, tempo, wpct, sos) for tid, off, dfn, tempo, wpct, sos in SEASON_STATS]
    conn.executemany(
        "INSERT OR IGNORE INTO team_season_stats "
        "(team_id, season, adj_eff_off, adj_eff_def, adj_tempo, win_pct, sos) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()


def load_recent_stats(conn: sqlite3.Connection, season: int) -> None:
    """Insert recent stats for all 64 teams."""
    rows = [(tid, season, l10, ctr, trend) for tid, l10, ctr, trend in RECENT_STATS]
    conn.executemany(
        "INSERT OR IGNORE INTO team_recent_stats "
        "(team_id, season, last10_win_pct, conf_tourney_result, scoring_trend) "
        "VALUES (?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
