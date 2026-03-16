# March Madness Bracket Builder

Simulates a 64-team NCAA tournament bracket using four expert "agents" that each evaluate matchups from a different angle, then combines their opinions via weighted voting.

## Architecture

```
[Data Layer]  ->  [Expert Layer]  ->  [Aggregator]  ->  [Bracket Engine]
   SQLite          Python fns         Python fn       Simulation loop
```

**Experts:**
- **Seed Expert** (weight 0.15) — Historical seed-vs-seed win rates
- **Efficiency Expert** (weight 0.40) — Adjusted offensive/defensive efficiency
- **Momentum Expert** (weight 0.20) — Last 10 games + conference tournament performance
- **Chaos Expert** (weight 0.25) — Controlled randomness for bracket-busting upsets

## Quick Start

```bash
python main.py              # random bracket (different each run)
python main.py --seed 42    # reproducible bracket
```

## Project Structure

```
march_madness/
    config.py               # weights, DB path, constants
    db/
        schema.sql          # SQLite table definitions
        queries.py          # all SQL access
    data/
        load_teams.py       # 64 teams + bracket structure
        load_stats.py       # season + recent stats
        load_history.py     # seed matchup history
    experts/
        seed_expert.py
        efficiency_expert.py
        momentum_expert.py
        chaos_expert.py
    engine/
        aggregator.py       # weighted average of expert scores
        bracket_engine.py   # round-by-round simulation
main.py                     # entry point
```

## How It Works

1. A fresh SQLite database is created with 2025 tournament data
2. The bracket engine walks through 6 rounds (Round of 64 through Championship)
3. For each game, all four experts score the matchup independently
4. The aggregator computes a weighted average and picks the winner
5. Winners advance to the next round until a champion is crowned

## Configuration

Edit `march_madness/config.py` to tune expert weights or other settings.
