-- March Madness Bracket Builder — Database Schema (SQLite)

CREATE TABLE IF NOT EXISTS teams (
    team_id     INTEGER PRIMARY KEY,
    team_name   TEXT    NOT NULL,
    conference  TEXT,
    seed        INTEGER NOT NULL,
    region      TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS team_season_stats (
    team_id         INTEGER NOT NULL,
    season          INTEGER NOT NULL,
    adj_eff_off     REAL,
    adj_eff_def     REAL,
    adj_tempo       REAL,
    win_pct         REAL,
    sos             REAL,
    PRIMARY KEY (team_id, season),
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
);

CREATE TABLE IF NOT EXISTS team_recent_stats (
    team_id             INTEGER NOT NULL,
    season              INTEGER NOT NULL,
    last10_win_pct      REAL,
    conf_tourney_result TEXT,
    scoring_trend       TEXT,
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
