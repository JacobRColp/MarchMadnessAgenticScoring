"""Compute derived team stats from raw boxscore data.

Reads the raw boxscores CSV and produces per-team aggregates:
win_pct, opp_avg_pts, last10_win_pct, scoring_trend, recent shooting.
"""

import csv
from collections import defaultdict


def _safe_int(val: str, default: int = 0) -> int:
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def _safe_float(val: str, default: float = 0.0) -> float:
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def _parse_made_attempted(val: str) -> tuple[int, int]:
    """Parse '7-13' into (7, 13). Returns (0, 0) on failure."""
    if not val or "-" not in val:
        return 0, 0
    parts = val.split("-")
    if len(parts) != 2:
        return 0, 0
    return _safe_int(parts[0]), _safe_int(parts[1])


def compute_aggregates(
    boxscores_csv_path: str, team_espn_ids: set[int]
) -> dict[int, dict]:
    """Compute derived stats from raw boxscores for tournament teams.

    Args:
        boxscores_csv_path: Path to the raw boxscores CSV.
        team_espn_ids: Set of ESPN IDs for the 68 tournament teams.

    Returns:
        Dict mapping espn_id -> {win_pct, opp_avg_pts, last10_win_pct,
        scoring_trend, recent_fg_pct, recent_three_pt_pct}.
    """
    # Step 1: Aggregate player rows into game-level team totals
    # Key: (game_id, team_espn_id) -> {pts, fgm, fga, 3pm, 3pa, date}
    game_team_totals = defaultdict(lambda: {
        "pts": 0, "fgm": 0, "fga": 0, "tpm": 0, "tpa": 0, "date": ""
    })

    # Deduplicate: games appear multiple times when scraped from both teams' schedules
    seen_player_rows = set()

    with open(boxscores_csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dedup_key = (row["game_id"], row["player_id"])
            if dedup_key in seen_player_rows:
                continue
            seen_player_rows.add(dedup_key)

            game_id = row["game_id"]
            espn_id = _safe_int(row["team_id"])
            key = (game_id, espn_id)

            game_team_totals[key]["pts"] += _safe_int(row["PTS"])
            fgm, fga = _parse_made_attempted(row["FG"])
            game_team_totals[key]["fgm"] += fgm
            game_team_totals[key]["fga"] += fga
            tpm, tpa = _parse_made_attempted(row["3PT"])
            game_team_totals[key]["tpm"] += tpm
            game_team_totals[key]["tpa"] += tpa

            if row["game_date"]:
                game_team_totals[key]["date"] = row["game_date"]

    # Step 2: Group by game_id to find opponents and determine W/L
    games_by_id = defaultdict(list)  # game_id -> [(espn_id, totals), ...]
    for (game_id, espn_id), totals in game_team_totals.items():
        games_by_id[game_id].append((espn_id, totals))

    # Step 3: Build per-team game records
    # team_games[espn_id] = sorted list of {date, pts, opp_pts, won, fgm, fga, tpm, tpa}
    team_games = defaultdict(list)

    for game_id, teams_in_game in games_by_id.items():
        if len(teams_in_game) != 2:
            continue  # skip games without exactly 2 teams

        (id_a, tot_a), (id_b, tot_b) = teams_in_game

        for my_id, my_tot, opp_tot in [
            (id_a, tot_a, tot_b),
            (id_b, tot_b, tot_a),
        ]:
            if my_id not in team_espn_ids:
                continue
            team_games[my_id].append({
                "date": my_tot["date"],
                "pts": my_tot["pts"],
                "opp_pts": opp_tot["pts"],
                "won": my_tot["pts"] > opp_tot["pts"],
                "fgm": my_tot["fgm"],
                "fga": my_tot["fga"],
                "tpm": my_tot["tpm"],
                "tpa": my_tot["tpa"],
            })

    # Step 4: Compute aggregates per team
    results = {}

    for espn_id in team_espn_ids:
        games = team_games.get(espn_id, [])

        if not games:
            results[espn_id] = {
                "win_pct": 0.0,
                "opp_avg_pts": 70.0,
                "last10_win_pct": 0.0,
                "scoring_trend": "stable",
                "recent_fg_pct": 0.0,
                "recent_three_pt_pct": 0.0,
            }
            continue

        # Sort by date
        games.sort(key=lambda g: g["date"])

        # Season aggregates
        total_games = len(games)
        wins = sum(1 for g in games if g["won"])
        win_pct = wins / total_games if total_games > 0 else 0.0
        opp_avg_pts = sum(g["opp_pts"] for g in games) / total_games
        season_avg_pts = sum(g["pts"] for g in games) / total_games

        # Last 10 games
        last10 = games[-10:]
        last10_wins = sum(1 for g in last10 if g["won"])
        last10_win_pct = last10_wins / len(last10)
        last10_avg_pts = sum(g["pts"] for g in last10) / len(last10)

        # Scoring trend
        diff = last10_avg_pts - season_avg_pts
        if diff > 3.0:
            scoring_trend = "improving"
        elif diff < -3.0:
            scoring_trend = "declining"
        else:
            scoring_trend = "stable"

        # Recent shooting
        last10_fgm = sum(g["fgm"] for g in last10)
        last10_fga = sum(g["fga"] for g in last10)
        last10_tpm = sum(g["tpm"] for g in last10)
        last10_tpa = sum(g["tpa"] for g in last10)
        recent_fg_pct = last10_fgm / last10_fga if last10_fga > 0 else 0.0
        recent_three_pt_pct = last10_tpm / last10_tpa if last10_tpa > 0 else 0.0

        results[espn_id] = {
            "win_pct": round(win_pct, 4),
            "opp_avg_pts": round(opp_avg_pts, 2),
            "last10_win_pct": round(last10_win_pct, 4),
            "scoring_trend": scoring_trend,
            "recent_fg_pct": round(recent_fg_pct, 4),
            "recent_three_pt_pct": round(recent_three_pt_pct, 4),
        }

    return results
