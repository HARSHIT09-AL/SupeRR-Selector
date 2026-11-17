import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"

balls = pd.read_csv(DATA / "ball_by_ball_cleaned.csv", low_memory=False)
matches = pd.read_csv(DATA / "matches_cleaned.csv", low_memory=False)
competitions = pd.read_csv(DATA / "competitions_cleaned.csv", low_memory=False)

output = []

def heading(title):
    output.append("\n" + "=" * 70)
    output.append(title)
    output.append("=" * 70)

# 1. Investigate innings 3 and 4
heading("INVESTIGATION: INNINGS 3 AND 4")

special = balls[balls["innings"].isin([3, 4])]

special_summary = (
    special.groupby(["match_id", "innings"])
    .agg(
        deliveries=("innings_ball_num", "size"),
        runs=("runs", "sum"),
        wickets=("is_wicket", "sum")
    )
    .reset_index()
)

special_summary = special_summary.merge(
    matches[["match_id", "comp_id", "match_date",
             "home_team", "away_team", "result"]],
    on="match_id",
    how="left"
)

special_summary = special_summary.merge(
    competitions[["comp_id", "comp_name", "match_format", "season"]],
    on="comp_id",
    how="left"
)

output.append(special_summary.to_string(index=False))

# 2. Investigate extras
heading("INVESTIGATION: EXTRAS")

extras = balls[balls["extras_type"].notna()]

output.append(
    extras.groupby("extras_type")
    .agg(
        deliveries=("match_id", "size"),
        total_runs=("runs", "sum"),
        extras1_total=("extras1_runs", "sum"),
        extras2_total=("extras_2_runs", "sum")
    )
    .to_string()
)

output.append("\nSample extras records:")
output.append(
    extras[
        ["match_id", "innings", "overid", "over_ball_num",
         "runs", "extras_type", "extras1_runs", "extras_2_runs",
         "is_wicket", "dismissal_type"]
    ].head(20).to_string(index=False)
)

# 3. Inspect competition formats
heading("INVESTIGATION: COMPETITION FORMATS")

output.append(
    competitions.groupby(["match_format", "season"])
    .size()
    .to_string()
)

output.append("\nCompetition names and IDs:")
output.append(
    competitions[
        ["comp_id", "comp_name", "match_format", "season"]
    ].sort_values(["match_format", "season", "comp_name"])
    .to_string(index=False)
)

# 4. Check delivery numbering
heading("INVESTIGATION: DELIVERY NUMBERING")

output.append("\nOver ball number distribution:")
output.append(balls["over_ball_num"].value_counts().sort_index().to_string())

output.append("\nInnings ball number maximum by innings:")
output.append(balls.groupby("innings")["innings_ball_num"].max().to_string())

result = "\n".join(output)

print(result)

REPORTS.mkdir(exist_ok=True)
(REPORTS / "pressure_rules_audit.txt").write_text(
    result, encoding="utf-8"
)

print("\nInvestigation saved to reports/pressure_rules_audit.txt")
