"""Load season and recent stats from CSV data and computed aggregates."""

import csv
import sqlite3

from march_madness import config


def load_season_stats(
    conn: sqlite3.Connection, season: int, aggregates: dict[int, dict]
) -> None:
    """Insert season stats by merging team summary CSV with boxscore aggregates."""
    # Build espn_id -> team_id lookup
    espn_to_team = {}
    for row in conn.execute("SELECT team_id, espn_id FROM teams").fetchall():
        espn_to_team[row["espn_id"]] = row["team_id"]

    rows_to_insert = []
    with open(config.TEAM_SUMMARY_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            espn_id = int(row["espn_id"])
            team_id = espn_to_team.get(espn_id)
            if team_id is None:
                continue

            agg = aggregates.get(espn_id, {})

            rows_to_insert.append((
                team_id,
                season,
                int(row["games"]),
                float(row["avg_PTS"]),
                float(row["FG_PCT"]),
                float(row["3PT_PCT"]),
                float(row["FT_PCT"]),
                float(row["avg_REB"]),
                float(row["avg_AST"]),
                float(row["avg_TO"]),
                float(row["avg_STL"]),
                float(row["avg_BLK"]),
                agg.get("opp_avg_pts", 70.0),
                agg.get("win_pct", 0.5),
            ))

    conn.executemany(
        "INSERT OR IGNORE INTO team_season_stats "
        "(team_id, season, games, avg_pts, fg_pct, three_pt_pct, ft_pct, "
        "avg_reb, avg_ast, avg_to, avg_stl, avg_blk, opp_avg_pts, win_pct) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        rows_to_insert,
    )
    conn.commit()


def load_recent_stats(
    conn: sqlite3.Connection, season: int, aggregates: dict[int, dict]
) -> None:
    """Insert recent stats from computed boxscore aggregates."""
    espn_to_team = {}
    for row in conn.execute("SELECT team_id, espn_id FROM teams").fetchall():
        espn_to_team[row["espn_id"]] = row["team_id"]

    rows_to_insert = []
    for espn_id, agg in aggregates.items():
        team_id = espn_to_team.get(espn_id)
        if team_id is None:
            continue

        rows_to_insert.append((
            team_id,
            season,
            agg.get("last10_win_pct", 0.5),
            agg.get("scoring_trend", "stable"),
            agg.get("recent_fg_pct", 0.0),
            agg.get("recent_three_pt_pct", 0.0),
        ))

    conn.executemany(
        "INSERT OR IGNORE INTO team_recent_stats "
        "(team_id, season, last10_win_pct, scoring_trend, "
        "recent_fg_pct, recent_three_pt_pct) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        rows_to_insert,
    )
    conn.commit()
