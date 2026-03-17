-- March Madness Bracket Builder — Database Schema (SQLite)

CREATE TABLE IF NOT EXISTS teams (
    team_id       INTEGER PRIMARY KEY,
    team_name     TEXT    NOT NULL,
    espn_id       INTEGER NOT NULL,
    seed          INTEGER NOT NULL,
    region        TEXT    NOT NULL,
    is_first_four INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS team_season_stats (
    team_id         INTEGER NOT NULL,
    season          INTEGER NOT NULL,
    games           INTEGER,
    avg_pts         REAL,
    fg_pct          REAL,
    three_pt_pct    REAL,
    ft_pct          REAL,
    avg_reb         REAL,
    avg_ast         REAL,
    avg_to          REAL,
    avg_stl         REAL,
    avg_blk         REAL,
    opp_avg_pts     REAL,
    win_pct         REAL,
    PRIMARY KEY (team_id, season),
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
);

CREATE TABLE IF NOT EXISTS team_recent_stats (
    team_id             INTEGER NOT NULL,
    season              INTEGER NOT NULL,
    last10_win_pct      REAL,
    scoring_trend       TEXT,
    recent_fg_pct       REAL,
    recent_three_pt_pct REAL,
    PRIMARY KEY (team_id, season),
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
);

CREATE TABLE IF NOT EXISTS seed_matchup_history (
    high_seed           INTEGER NOT NULL,
    low_seed            INTEGER NOT NULL,
    games_played        INTEGER NOT NULL,
    high_seed_win_pct   REAL    NOT NULL,
    PRIMARY KEY (high_seed, low_seed)
);

CREATE TABLE IF NOT EXISTS tournament_bracket (
    game_id     INTEGER PRIMARY KEY,
    round       INTEGER NOT NULL,
    region      TEXT,
    slot_a      INTEGER NOT NULL,
    slot_b      INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_season_stats_team ON team_season_stats(team_id);
CREATE INDEX IF NOT EXISTS idx_recent_stats_team ON team_recent_stats(team_id);
CREATE INDEX IF NOT EXISTS idx_bracket_round     ON tournament_bracket(round);
CREATE INDEX IF NOT EXISTS idx_seed_matchup      ON seed_matchup_history(high_seed, low_seed);
