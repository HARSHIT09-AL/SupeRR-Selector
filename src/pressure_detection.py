import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"

balls = pd.read_csv(DATA / "ball_by_ball_cleaned.csv", low_memory=False)
matches = pd.read_csv(DATA / "matches_cleaned.csv", low_memory=False)
competitions = pd.read_csv(DATA / "competitions_cleaned.csv", low_memory=False)

# --------------------------------------------------
# 1. SELECT PROJECT MATCHES: IPL + T20I, FROM 2022
# --------------------------------------------------

matches["match_date"] = pd.to_datetime(matches["match_date"], errors="coerce")

match_data = matches.merge(
    competitions[["comp_id", "comp_name", "match_format"]],
    on="comp_id",
    how="left"
)

format_name = match_data["match_format"].astype(str).str.upper().str.strip()
competition_name = match_data["comp_name"].astype(str).str.upper()

scope = (
    (format_name == "T20I") |
    ((format_name == "T20") & competition_name.str.startswith("IPL"))
)

match_data = match_data[
    scope & (match_data["match_date"].dt.year >= 2022)
].copy()

balls = balls[balls["match_id"].isin(match_data["match_id"])].copy()

# Exclude Super Overs from standard pressure analysis.
balls = balls[balls["innings"].isin([1, 2])].copy()

# --------------------------------------------------
# 2. CLEAN RUNS, WICKETS AND EXTRAS
# --------------------------------------------------

for col in ["runs", "extras1_runs", "extras_2_runs"]:
    balls[col] = pd.to_numeric(balls[col], errors="coerce").fillna(0)

def to_bool(value):
    if pd.isna(value):
        return False
    if isinstance(value, str):
        return value.strip().lower() in ["true", "1", "yes"]
    return bool(value)

balls["is_wicket"] = balls["is_wicket"].apply(to_bool)

balls["extras_type_clean"] = (
    balls["extras_type"].fillna("normal").astype(str).str.strip().str.lower()
)

# Total team runs include batter runs and both extras columns.
balls["total_runs"] = (
    balls["runs"] + balls["extras1_runs"] + balls["extras_2_runs"]
)

# Conservative legal-ball rules.
illegal_types = ["wide", "overstep", "other", "penalty"]

balls["is_legal_ball"] = ~balls["extras_type_clean"].isin(illegal_types)

# Keep uncertain extras visible for later review.
balls["uncertain_extras"] = balls["extras_type_clean"].isin(["other", "penalty"])

# --------------------------------------------------
# 3. CALCULATE MATCH SCORES AND CHASE TARGETS
# --------------------------------------------------

innings_scores = (
    balls.groupby(["match_id", "innings"])["total_runs"]
    .sum()
    .unstack(fill_value=0)
)

if 1 not in innings_scores.columns:
    innings_scores[1] = 0

innings_scores["first_innings_score"] = innings_scores[1]

match_data = match_data.merge(
    innings_scores[["first_innings_score"]],
    left_on="match_id",
    right_index=True,
    how="left"
)

match_data["first_innings_score"] = (
    match_data["first_innings_score"].fillna(0)
)

match_lookup = match_data.set_index("match_id").to_dict("index")

# --------------------------------------------------
# 4. BUILD DELIVERY-LEVEL PRESSURE DATA
# --------------------------------------------------

processed_innings = []

# Preserve source order within each innings.
balls["_source_order"] = np.arange(len(balls))

for (match_id, innings), group in balls.groupby(
    ["match_id", "innings"], sort=False
):
    group = group.sort_values("_source_order").copy()

    match = match_lookup.get(match_id)
    if match is None:
        continue

    if innings == 1:
        revised_balls = match.get("first_inn_revised_overs")
        max_balls = 120 if pd.isna(revised_balls) else int(revised_balls)
        target = np.nan
    else:
        revised_balls = match.get("second_inn_revised_overs")
        max_balls = 120 if pd.isna(revised_balls) else int(revised_balls)

        revised_target = match.get("revised_target")
        if pd.notna(revised_target):
            target = float(revised_target)
        else:
            target = float(match["first_innings_score"] + 1)

    # State BEFORE each delivery.
    group["score_before"] = (
        group["total_runs"].cumsum().shift(1, fill_value=0)
    )

    group["wickets_before"] = (
        group["is_wicket"].astype(int).cumsum().shift(1, fill_value=0)
    )

    group["legal_balls_before"] = (
        group["is_legal_ball"].astype(int).cumsum().shift(1, fill_value=0)
    )

    group["balls_remaining"] = (
        max_balls - group["legal_balls_before"]
    ).clip(lower=0)

    group["innings_max_legal_balls"] = max_balls
    group["target"] = target

    if innings == 2:
        group["runs_required"] = target - group["score_before"]

        group["required_run_rate"] = np.where(
            group["balls_remaining"] > 0,
            group["runs_required"] / group["balls_remaining"] * 6,
            np.nan
        )

        chase_pressure = (
            (
                (group["runs_required"] > 0) &
                (group["required_run_rate"] >= 9)
            ) |
            (
                (group["runs_required"] > 0) &
                (group["balls_remaining"] <= 18) &
                (group["required_run_rate"] >= 7)
            ) |
            (
                (group["wickets_before"] >= 6) &
                (group["balls_remaining"] <= 36) &
                (group["runs_required"] > 0)
            )
        )

        group["pressure_reason"] = np.select(
            [
                (group["runs_required"] > 0) &
                (group["required_run_rate"] >= 9),

                (group["runs_required"] > 0) &
                (group["balls_remaining"] <= 18) &
                (group["required_run_rate"] >= 7),

                (group["wickets_before"] >= 6) &
                (group["balls_remaining"] <= 36) &
                (group["runs_required"] > 0)
            ],
            [
                "Required run rate >= 9",
                "Final 18 balls with required rate >= 7",
                "Six or more wickets down with 36 or fewer balls left"
            ],
            default="No pressure"
        )

        group["is_pressure"] = chase_pressure

    else:
        group["runs_required"] = np.nan
        group["required_run_rate"] = np.nan

        early_pressure_ball = int(np.ceil(max_balls * 0.70))
        late_pressure_ball = int(np.ceil(max_balls * 0.85))

        first_innings_pressure = (
            (
                (group["legal_balls_before"] >= early_pressure_ball) &
                (group["wickets_before"] >= 4)
            ) |
            (group["legal_balls_before"] >= late_pressure_ball)
        )

        group["pressure_reason"] = np.select(
            [
                (group["legal_balls_before"] >= late_pressure_ball),

                (group["legal_balls_before"] >= early_pressure_ball) &
                (group["wickets_before"] >= 4)
            ],
            [
                "Final 15% of first innings",
                "Four or more wickets down after 70% of innings"
            ],
            default="No pressure"
        )

        group["is_pressure"] = first_innings_pressure

    group["competition"] = match["comp_name"]
    group["match_date"] = match["match_date"]
    group["match_format"] = match["match_format"]

    processed_innings.append(group)

if not processed_innings:
    raise ValueError("No innings were processed. Check the competition filters.")

pressure_data = pd.concat(processed_innings, ignore_index=True)

# --------------------------------------------------
# 5. CREATE INNINGS SUMMARY
# --------------------------------------------------

summary = (
    pressure_data.groupby(["match_id", "innings"], as_index=False)
    .agg(
        competition=("competition", "first"),
        match_date=("match_date", "first"),
        match_format=("match_format", "first"),
        batting_team_id=("batting_team_id", "first"),
        total_score=("total_runs", "sum"),
        total_wickets=("is_wicket", "sum"),
        legal_balls=("is_legal_ball", "sum"),
        total_deliveries=("match_id", "size"),
        pressure_deliveries=("is_pressure", "sum"),
        uncertain_extras_deliveries=("uncertain_extras", "sum"),
        target=("target", "first")
    )
)

summary["pressure_percentage"] = np.where(
    summary["total_deliveries"] > 0,
    summary["pressure_deliveries"] / summary["total_deliveries"] * 100,
    0
)

# --------------------------------------------------
# 6. SAVE OUTPUTS AND RULES REPORT
# --------------------------------------------------

DATA.mkdir(exist_ok=True)
REPORTS.mkdir(exist_ok=True)

pressure_data.to_csv(DATA / "pressure_ball_by_ball.csv", index=False)
summary.to_csv(DATA / "innings_pressure_summary.csv", index=False)

report = f"""
SUPERR SELECTOR - PRESSURE ENGINE REPORT
========================================

Project scope:
IPL and T20I competitions from 2022 onward.

Super Overs:
Excluded from standard pressure analysis.

Pressure state:
Measured BEFORE each delivery.

Run calculation:
runs + extras1_runs + extras_2_runs.

Legal-ball assumptions:
Wide, Overstep, other and Penalty are excluded.
Normal deliveries, byes and legbyes are counted.

Uncertain extras:
other and Penalty are flagged for review.

Pressure rules - second innings:
1. Required run rate >= 9.
2. Final 18 balls with required rate >= 7.
3. Six or more wickets down with 36 or fewer balls remaining.

Pressure rules - first innings:
1. Four or more wickets down after 70% of available legal balls.
2. At least 85% of available legal balls completed.

Total selected matches: {match_data['match_id'].nunique()}
Matches with ball-by-ball data: {pressure_data['match_id'].nunique()}
Total analyzed deliveries: {len(pressure_data)}
Total pressure deliveries: {int(pressure_data['is_pressure'].sum())}
Total innings analyzed: {len(summary)}
Uncertain extras deliveries: {int(pressure_data['uncertain_extras'].sum())}

NOTE:
Revised overs are treated as legal-ball limits because the source
values are expressed as ball counts (for example, 114 = 19 overs).
The conservative treatment of 'other' and 'Penalty' must be reviewed
before final publication of player rankings.
"""

(REPORTS / "pressure_engine_report.txt").write_text(
    report, encoding="utf-8"
)

print(report)
print("OUTPUT FILES CREATED:")
print("1. data/processed/pressure_ball_by_ball.csv")
print("2. data/processed/innings_pressure_summary.csv")
print("3. reports/pressure_engine_report.txt")
