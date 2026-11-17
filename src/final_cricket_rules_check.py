import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"

balls = pd.read_csv(DATA / "ball_by_ball_cleaned.csv", low_memory=False)
matches = pd.read_csv(DATA / "matches_cleaned.csv", low_memory=False)

output = []

def add(title, df):
    output.append("\n" + "=" * 65)
    output.append(title)
    output.append("=" * 65)
    output.append(df.to_string(index=False))

# Check unusual extras
add(
    "SAMPLES OF OVERSTEP DELIVERIES",
    balls[balls["extras_type"] == "Overstep"][
        ["match_id", "innings", "overid", "over_ball_num",
         "runs", "extras1_runs", "extras_2_runs",
         "is_wicket", "dismissal_type"]
    ].head(12)
)

add(
    "SAMPLES OF OTHER EXTRAS",
    balls[balls["extras_type"] == "other"][
        ["match_id", "innings", "overid", "over_ball_num",
         "runs", "extras1_runs", "extras_2_runs",
         "is_wicket", "dismissal_type"]
    ].head(20)
)

# Wicket types
add(
    "WICKET DISMISSAL TYPES",
    balls[balls["is_wicket"] == True]
    ["dismissal_type"]
    .value_counts(dropna=False)
    .rename_axis("dismissal_type")
    .reset_index(name="count")
)

# Run accounting
balls["calculated_total_runs"] = (
    balls["runs"] +
    balls["extras1_runs"] +
    balls["extras_2_runs"]
)

add(
    "RUN ACCOUNTING BY EXTRAS TYPE",
    balls.groupby("extras_type", dropna=False)
    .agg(
        deliveries=("match_id", "size"),
        batter_runs=("runs", "sum"),
        extras1=("extras1_runs", "sum"),
        extras2=("extras_2_runs", "sum"),
        calculated_total=("calculated_total_runs", "sum")
    )
    .reset_index()
)

# Revised match information
add(
    "REVISED MATCHES",
    matches[
        matches["revised_target"].notna() |
        matches["first_inn_revised_overs"].notna() |
        matches["second_inn_revised_overs"].notna()
    ][
        ["match_id", "comp_id", "match_date",
         "first_inn_revised_overs",
         "second_inn_revised_overs",
         "revised_target"]
    ].head(30)
)

result = "\n".join(output)

print(result)

REPORTS.mkdir(exist_ok=True)
(REPORTS / "final_cricket_rules_check.txt").write_text(
    result, encoding="utf-8"
)

print("\nReport saved successfully!")
