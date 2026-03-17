# March Madness Bracket Builder

Simulates a 68-team NCAA tournament bracket using a four-expert ensemble system. Each expert evaluates every matchup from a different angle, then an aggregator combines their opinions to pick a winner. The result is a full bracket from the First Four through the Championship.

## Quick Start

```bash
python main.py                      # random bracket (different each run)
python main.py --seed 42            # reproducible bracket
python main.py --stochastic         # Monte Carlo aggregator
python main.py --stochastic --seed 42  # reproducible stochastic bracket
```

## Architecture

```
CSV Data  -->  SQLite DB  -->  4 Experts  -->  Aggregator  -->  Bracket Engine
                                (score)        (combine)        (simulate)
```

Each game flows through this pipeline: the bracket engine resolves the two teams, calls all four experts independently, passes their scores to the aggregator, and records the winner for the next round.

### Why This Design

- **Experts are pure functions** `(team_a, team_b, conn) -> {"team_a": float, "team_b": float}`. They don't depend on each other, so they can be added, removed, or modified in isolation.
- **The aggregator is generic** — it works with any number of experts and doesn't know what they measure.
- **SQLite as the data store** — single-file, no server, sufficient for 68 teams. A fresh database is created each run to guarantee clean state.

## The Four Experts

| Expert | Weight | Purpose |
|--------|--------|---------|
| Seed | 25% | Historical seed-vs-seed win rates from 30+ years of NCAA data |
| Efficiency | 40% | Composite of current-season offensive/defensive performance |
| Momentum | 25% | Last 10 games: win rate, scoring trend, recent shooting |
| Chaos | 10% | Controlled randomness to generate realistic upsets |

Weights must sum to 1.0 and are configured in `march_madness/config.py`.


### Expert Details

#### Seed Expert

Looks up the historical win rate for the seed pairing (e.g., 1-vs-16 historically results in the 1-seed winning 99.3% of the time). Returns 50/50 for same-seed matchups or unknown pairings.

#### Efficiency Expert

Computes a composite score from four components:

| Component | Weight | Formula | Rationale |
|-----------|--------|---------|-----------|
| Offensive power | 30% | `(avg_pts - 55) / 35` | Normalizes typical 55-90 PPG range |
| Shooting efficiency | 25% | `fg_pct * 0.6 + three_pt_pct * 0.4` | FG% is more stable; 3PT% reflects modern game |
| Ball security | 15% | `1 - (avg_to - 8) / 8` | Inverted (fewer turnovers = better), 8-16 TO range |
| Defense | 30% | `1 - (opp_avg_pts - 55) / 30` | Inverted (fewer points allowed = better) |

The difference between two teams' composite scores maps to a confidence value clamped to [0.05, 0.95]. The clamp prevents any single expert from completely dictating the outcome — it always reserves room for the other experts to influence the result.

#### Momentum Expert

Starts with the team's last-10-games win percentage, then applies two adjustments:

- **Scoring trend**: If the team's last 10 games average more than 3 PPG above their season average, they get a +0.05 boost ("improving"). More than 3 PPG below gets a -0.05 penalty ("declining"). The 3 PPG threshold filters out noise while catching real momentum shifts.
- **Recent shooting bonus**: `(recent_fg_pct - 0.44) * 0.5`, clamped to [-0.05, +0.10]. Teams shooting above the 44% FG baseline get a small boost.

#### Chaos Expert

Calculates an upset probability based on seed difference:

```
upset_chance = max(0.08, 0.50 - seed_diff * 0.03)
```

This produces: 47% upset chance at 1-seed difference, 29% at 7, and floors at 8% for the largest mismatches (ensuring even a 16-seed has a small chance). When an upset triggers, the underdog receives a random confidence score between 0.55 and 0.80; otherwise, the favorite gets a score in that range.

The 8% floor exists because real March Madness has produced 16-over-1 upsets (UMBC over Virginia, 2018). The linear decay (3% per seed difference) is simple and interpretable.

## Aggregation Modes

### Deterministic (default)

Computes the weighted sum of all expert scores for each team and picks the team with the higher total. Given a fixed random seed, the bracket is fully reproducible (though the chaos expert still introduces randomness).

### Monte Carlo (`--stochastic`)

Converts weighted scores into a win probability and samples the outcome:

```
prob_a = weighted_score_a / (weighted_score_a + weighted_score_b)
winner = team_a if random() < prob_a else team_b
```

In deterministic mode, a team favored 60/40 always wins. In stochastic mode, that team wins 60% of the time. This is useful for generating multiple bracket variations to explore the range of possible outcomes.

## Data Pipeline

### Source Data

Two CSV files in `notebooks/`:
- **Team summary**: One row per team with season stats (PPG, FG%, 3PT%, rebounds, assists, etc.)
- **Raw boxscores**: Individual player boxscores for every game, used to compute derived stats

### Boxscore Aggregation

The raw boxscores are processed into per-team aggregates before the simulation runs. This step:

1. **Deduplicates** player rows by `(game_id, player_id)` — games can appear twice when scraped from both teams' schedules
2. **Aggregates** player stats into team-level game totals
3. **Sorts by date** and computes last-10-game stats (win%, scoring, shooting)
4. **Detects scoring trends** using a 3 PPG threshold between last-10 average and season average

This computation runs once per execution before any simulation begins.

### Database Schema

```
teams                    68 tournament teams (name, seed, region, ESPN ID)
team_season_stats        Full-season stats per team (scoring, shooting, defense)
team_recent_stats        Last 10 games: win%, trend, recent shooting %
seed_matchup_history     Historical win rates for each seed pairing (50 records)
tournament_bracket       Game structure: 67 games across 7 rounds with slot references
```

### Bracket Slot Resolution

The bracket engine uses a recursive slot system. Each game has two slots that reference either a `team_id` (for first-round matchups) or a `game_id` from a previous round. The engine maintains a `winners` dictionary mapping `game_id -> team`, so later rounds automatically resolve by looking up previous winners. Game IDs start at 1001+ to avoid collision with team IDs (1-68).

This design handles First Four integration cleanly: Round 1 slots can reference either a team directly or a First Four game's winner, using the same resolution logic.

## Project Structure

```
march_madness/
    config.py                  # Weights, DB path, season, CSV paths
    db/
        schema.sql             # Table definitions + indexes
        queries.py             # All SQL access (init, inserts, lookups)
    data/
        load_teams.py          # Load 68 teams + build bracket structure
        load_stats.py          # Load season + recent stats from CSV
        load_history.py        # Load historical seed matchup win rates
        compute_aggregates.py  # Derive per-team stats from raw boxscores
    experts/
        seed_expert.py         # Historical seed-vs-seed probabilities
        efficiency_expert.py   # Composite offensive/defensive scoring
        momentum_expert.py     # Last 10 games + trend detection
        chaos_expert.py        # Controlled random upset generation
    engine/
        aggregator.py          # Deterministic + Monte Carlo aggregation
        bracket_engine.py      # Round-by-round tournament simulation
main.py                        # CLI entry point
```

## Adding a New Expert

1. Create `march_madness/experts/your_expert.py` with a function signature `(team_a, team_b, conn) -> {"team_a": float, "team_b": float}`
2. Add it to the `EXPERTS` list in `march_madness/experts/__init__.py`
3. Add a weight entry in `config.py` (all weights must sum to 1.0)
4. Add the weight to the `weights` list in `main.py` in the same position as the expert

The aggregator and bracket engine require no changes.

## Configuration

All tunable parameters live in `march_madness/config.py`:

- `EXPERT_WEIGHTS` — relative influence of each expert (must sum to 1.0)
- `SEASON` — tournament year (currently 2026)
- `DB_PATH` — SQLite database location (recreated each run)
- CSV paths for team summaries and raw boxscores
