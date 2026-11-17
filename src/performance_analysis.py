import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "processed"

df = pd.read_csv(DATA / "pressure_ball_by_ball.csv", low_memory=False)

required = [
    "match_id", "innings", "match_format", "is_pressure",
    "legal_balls_before", "innings_max_legal_balls",
    "is_legal_ball", "total_runs", "runs",
    "extras_type_clean", "is_wicket", "dismissal_type",
    "striker_id", "striker_name", "bowler_id", "bowler_name"
]

missing = [c for c in required if c not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

# Normalize imported values.
for col in ["is_pressure", "is_legal_ball", "is_wicket"]:
    df[col] = df[col].astype(str).str.lower().isin(["true", "1", "yes"])

for col in ["runs", "total_runs", "legal_balls_before",
            "innings_max_legal_balls"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

df["extras_type_clean"] = (
    df["extras_type_clean"].fillna("normal").astype(str).str.lower()
)

# Match phases are proportional to the available innings length.
progress = np.where(
    df["innings_max_legal_balls"] > 0,
    df["legal_balls_before"] / df["innings_max_legal_balls"],
    np.nan
)

df["phase"] = pd.cut(
    progress,
    bins=[-0.001, 0.30, 0.70, 1.001],
    labels=["Powerplay", "Middle", "Death"],
    right=False
)

keys = ["match_format", "innings", "phase"]
# ==================================================
# BATTING RATINGS
# ==================================================

# Operational balls-faced definition:
# Exclude wides, byes, legbyes and uncertain extras.
# Count Overstep/no-ball deliveries as faced.
not_faced = ["wide", "byes", "legbyes", "other", "penalty"]

df["batter_ball"] = ~df["extras_type_clean"].isin(not_faced)

# Create these subsets after all shared columns are ready.
normal = df[~df["is_pressure"]].copy()
pressure = df[df["is_pressure"]].copy()

normal_bat = normal[
    normal["striker_id"].notna() &
    normal["batter_ball"]
]

bat_baseline = (
    normal_bat.groupby(keys, observed=True)
    .agg(
        baseline_runs=("runs", "sum"),
        baseline_balls=("batter_ball", "sum")
    )
    .reset_index()
)

bat_baseline["baseline_sr"] = (
    bat_baseline["baseline_runs"] /
    bat_baseline["baseline_balls"] * 100
)

pressure_bat = pressure[
    pressure["striker_id"].notna() &
    pressure["batter_ball"]
]

bat_player_phase = (
    pressure_bat.groupby(
        ["striker_id", "striker_name"] + keys,
        observed=True
    )
    .agg(
        pressure_runs=("runs", "sum"),
        pressure_balls=("batter_ball", "sum"),
        pressure_fours=("is_four", "sum"),
        pressure_sixes=("is_six", "sum")
    )
    .reset_index()
)

bat_player_phase = bat_player_phase.merge(
    bat_baseline[keys + ["baseline_sr"]],
    on=keys,
    how="left"
)

bat_player_phase["expected_runs"] = (
    bat_player_phase["pressure_balls"] *
    bat_player_phase["baseline_sr"] / 100
)

bat = (
    bat_player_phase.groupby(
        ["striker_id", "striker_name"], as_index=False
    )
    .agg(
        pressure_runs=("pressure_runs", "sum"),
        pressure_balls=("pressure_balls", "sum"),
        expected_runs=("expected_runs", "sum"),
        fours=("pressure_fours", "sum"),
        sixes=("pressure_sixes", "sum")
    )
)

bat["pressure_strike_rate"] = (
    bat["pressure_runs"] / bat["pressure_balls"] * 100
)

bat["expected_strike_rate"] = (
    bat["expected_runs"] / bat["pressure_balls"] * 100
)

bat["raw_improvement_pct"] = np.where(
    bat["expected_runs"] > 0,
    (bat["pressure_runs"] / bat["expected_runs"] - 1) * 100,
    np.nan
)

# Shrink small samples toward zero.
bat["reliability"] = bat["pressure_balls"] / (
    bat["pressure_balls"] + 30
)

bat["batting_pressure_score"] = (
    100 + bat["raw_improvement_pct"] * bat["reliability"]
)

bat = bat[
    (bat["pressure_balls"] >= 30) &
    bat["expected_runs"].gt(0)
].copy()

bat = bat.sort_values(
    "batting_pressure_score", ascending=False
)

# ==================================================
# BOWLING RATINGS
# ==================================================

# Byes and legbyes are not charged to the bowler.
# Penalty and unknown 'other' extras are excluded.
# Wides and Overstep/no-ball runs are charged to the bowler.
bowling_valid = ~df["extras_type_clean"].isin(["other", "penalty"])

df["bowler_runs_conceded"] = df["total_runs"]

df.loc[
    df["extras_type_clean"].isin(["byes", "legbyes"]),
    "bowler_runs_conceded"
] -= (
    df.loc[
        df["extras_type_clean"].isin(["byes", "legbyes"]),
        "extras1_runs"
    ].fillna(0) +
    df.loc[
        df["extras_type_clean"].isin(["byes", "legbyes"]),
        "extras_2_runs"
    ].fillna(0)
)

# Only recognized bowler-credited dismissals count as wickets.
credited_dismissals = [
    "Caught", "Bowled", "LBW", "Stump", "Hit Wicket"
]

df["bowler_wicket"] = (
    df["is_wicket"] &
    df["dismissal_type"].isin(credited_dismissals)
)

# Refresh subsets after all batting and bowling columns are created.
normal = df[~df["is_pressure"]].copy()
pressure = df[df["is_pressure"]].copy()

normal_bowl = normal[
    normal["bowler_id"].notna() &
    normal["is_legal_ball"] &
    (~normal["extras_type_clean"].isin(["other", "penalty"]))
]

bowl_baseline = (
    normal_bowl.groupby(keys, observed=True)
    .agg(
        baseline_runs_conceded=("bowler_runs_conceded", "sum"),
        baseline_legal_balls=("is_legal_ball", "sum"),
        baseline_wickets=("bowler_wicket", "sum")
    )
    .reset_index()
)

bowl_baseline["baseline_economy"] = (
    bowl_baseline["baseline_runs_conceded"] /
    bowl_baseline["baseline_legal_balls"] * 6
)

bowl_baseline["baseline_wicket_rate"] = (
    bowl_baseline["baseline_wickets"] /
    bowl_baseline["baseline_legal_balls"] * 6
)

pressure_bowl = pressure[
    pressure["bowler_id"].notna() &
    pressure["is_legal_ball"] &
    (~pressure["extras_type_clean"].isin(["other", "penalty"]))
]

bowl_player_phase = (
    pressure_bowl.groupby(
        ["bowler_id", "bowler_name"] + keys,
        observed=True
    )
    .agg(
        pressure_runs_conceded=("bowler_runs_conceded", "sum"),
        pressure_legal_balls=("is_legal_ball", "sum"),
        pressure_wickets=("bowler_wicket", "sum")
    )
    .reset_index()
)

bowl_player_phase = bowl_player_phase.merge(
    bowl_baseline[keys + [
        "baseline_economy", "baseline_wicket_rate"
    ]],
    on=keys,
    how="left"
)

bowl_player_phase["expected_runs"] = (
    bowl_player_phase["pressure_legal_balls"] *
    bowl_player_phase["baseline_economy"] / 6
)

bowl_player_phase["expected_wickets"] = (
    bowl_player_phase["pressure_legal_balls"] *
    bowl_player_phase["baseline_wicket_rate"] / 6
)

bowl = (
    bowl_player_phase.groupby(
        ["bowler_id", "bowler_name"], as_index=False
    )
    .agg(
        pressure_runs_conceded=("pressure_runs_conceded", "sum"),
        pressure_legal_balls=("pressure_legal_balls", "sum"),
        pressure_wickets=("pressure_wickets", "sum"),
        expected_runs=("expected_runs", "sum"),
        expected_wickets=("expected_wickets", "sum")
    )
)

bowl["pressure_economy"] = (
    bowl["pressure_runs_conceded"] /
    bowl["pressure_legal_balls"] * 6
)

bowl["expected_economy"] = (
    bowl["expected_runs"] /
    bowl["pressure_legal_balls"] * 6
)

bowl["economy_improvement_pct"] = np.where(
    bowl["expected_runs"] > 0,
    (1 - bowl["pressure_runs_conceded"] /
     bowl["expected_runs"]) * 100,
    np.nan
)

bowl["wicket_improvement_pct"] = np.where(
    bowl["expected_wickets"] > 0,
    (bowl["pressure_wickets"] /
     bowl["expected_wickets"] - 1) * 100,
    np.nan
)

bowl["reliability"] = bowl["pressure_legal_balls"] / (
    bowl["pressure_legal_balls"] + 60
)

bowl["bowling_pressure_score"] = (
    100 + bowl["reliability"] * (
        0.70 * bowl["economy_improvement_pct"].fillna(0) +
        0.30 * bowl["wicket_improvement_pct"].fillna(0)
    )
)

bowl = bowl[
    (bowl["pressure_legal_balls"] >= 30) &
    bowl["expected_runs"].gt(0)
].copy()

bowl = bowl.sort_values(
    "bowling_pressure_score", ascending=False
)

# ==================================================
# SAVE RESULTS
# ==================================================

bat.to_csv(DATA / "batter_pressure_ratings.csv", index=False)
bowl.to_csv(DATA / "bowler_pressure_ratings.csv", index=False)

print("\nSUPERR SELECTOR - PLAYER RATINGS")
print("=" * 45)
print(f"Qualified batters: {len(bat)}")
print(f"Qualified bowlers: {len(bowl)}")

print("\nTOP 10 BATTERS")
print(
    bat[[
        "striker_name", "pressure_runs", "pressure_balls",
        "pressure_strike_rate", "batting_pressure_score"
    ]].head(10).to_string(index=False)
)

print("\nTOP 10 BOWLERS")
print(
    bowl[[
        "bowler_name", "pressure_runs_conceded",
        "pressure_legal_balls", "pressure_wickets",
        "pressure_economy", "bowling_pressure_score"
    ]].head(10).to_string(index=False)
)

print("\nSaved:")
print("data/processed/batter_pressure_ratings.csv")
print("data/processed/bowler_pressure_ratings.csv")
