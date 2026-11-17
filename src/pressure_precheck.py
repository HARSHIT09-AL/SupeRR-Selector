import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

def load(name):
    path = DATA / f"{name}_cleaned.csv"
    if not path.exists():
        print(f"Missing dataset: {path.name}")
        return None
    return pd.read_csv(path, low_memory=False)

balls = load("ball_by_ball")
matches = load("matches")
competitions = load("competitions")

report = []

def section(title):
    report.append("\n" + "=" * 65)
    report.append(title)
    report.append("=" * 65)

if balls is not None:
    section("BALL-BY-BALL DIAGNOSTICS")

    report.append(f"Total deliveries: {len(balls):,}")
    report.append(f"Unique matches: {balls['match_id'].nunique():,}")

    report.append("\nInnings distribution:")
    report.append(balls["innings"].value_counts().sort_index().to_string())

    report.append("\nDeliveries by innings and match:")
    report.append(
        balls.groupby("innings")["match_id"]
        .nunique().to_string()
    )

    report.append("\nMaximum over number by innings:")
    report.append(
        balls.groupby("innings")["overid"].max().to_string()
    )

    report.append("\nExtras type distribution:")
    report.append(
        balls["extras_type"].fillna("No extras").value_counts().to_string()
    )

    report.append("\nExtras runs distribution:")
    report.append(
        balls[["extras1_runs", "extras_2_runs"]]
        .describe().to_string()
    )

    report.append("\nWicket records:")
    report.append(
        balls["is_wicket"].value_counts(dropna=False).to_string()
    )

if matches is not None:
    section("MATCH DATA DIAGNOSTICS")

    report.append(f"Total matches: {len(matches):,}")
    report.append(f"Unique match IDs: {matches['match_id'].nunique():,}")

    if balls is not None:
        ball_ids = set(balls["match_id"].dropna())
        match_ids = set(matches["match_id"].dropna())

        report.append(
            f"\nMatches without ball data: {len(match_ids - ball_ids)}"
        )
        report.append(
            f"Ball-data matches absent from match file: {len(ball_ids - match_ids)}"
        )

    report.append("\nCompetition IDs in matches:")
    report.append(matches["comp_id"].value_counts().to_string())

if competitions is not None:
    section("COMPETITION DATA DIAGNOSTICS")

    report.append("Columns:")
    report.append(str(competitions.columns.tolist()))

    report.append("\nFirst 15 records:")
    report.append(competitions.head(15).to_string(index=False))

    if matches is not None:
        section("MATCH AND COMPETITION MERGE CHECK")

        merged = matches.merge(
            competitions,
            on="comp_id",
            how="left",
            indicator=True,
            suffixes=("_match", "_competition")
        )

        report.append(
            merged["_merge"].value_counts().to_string()
        )

result = "\n".join(report)

print(result)

(REPORTS / "pressure_precheck.txt").write_text(
    result, encoding="utf-8"
)

print("\nDiagnostic report saved successfully!")
