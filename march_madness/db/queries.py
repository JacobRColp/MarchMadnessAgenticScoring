"""Centralized database access. All SQL queries live here."""

import sqlite3
from pathlib import Path

SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def init_db(db_path: str) -> sqlite3.Connection:
    """Create the database and tables. Returns an open connection."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA_PATH.read_text())
    return conn


def get_team(conn: sqlite3.Connection, team_id: int) -> dict | None:
    row = conn.execute("SELECT * FROM teams WHERE team_id = ?", (team_id,)).fetchone()
    return dict(row) if row else None


def get_season_stats(conn: sqlite3.Connection, team_id: int, season: int) -> dict | None:
    row = conn.execute(
        "SELECT * FROM team_season_stats WHERE team_id = ? AND season = ?",
        (team_id, season),
    ).fetchone()
    return dict(row) if row else None


def get_recent_stats(conn: sqlite3.Connection, team_id: int, season: int) -> dict | None:
    row = conn.execute(
        "SELECT * FROM team_recent_stats WHERE team_id = ? AND season = ?",
        (team_id, season),
    ).fetchone()
    return dict(row) if row else None


def get_team_by_espn_id(conn: sqlite3.Connection, espn_id: int) -> dict | None:
    row = conn.execute("SELECT * FROM teams WHERE espn_id = ?", (espn_id,)).fetchone()
    return dict(row) if row else None


def get_seed_matchup(conn: sqlite3.Connection, high_seed: int, low_seed: int) -> dict | None:
    row = conn.execute(
        "SELECT * FROM seed_matchup_history WHERE high_seed = ? AND low_seed = ?",
        (high_seed, low_seed),
    ).fetchone()
    return dict(row) if row else None


def get_round_matchups(conn: sqlite3.Connection, round_num: int) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM tournament_bracket WHERE round = ? ORDER BY game_id",
        (round_num,),
    ).fetchall()
    return [dict(r) for r in rows]
