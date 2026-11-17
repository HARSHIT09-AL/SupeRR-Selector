from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

required_files = [
    "data/processed/pressure_ball_by_ball.csv",
    "data/processed/innings_pressure_summary.csv",
    "data/processed/batter_pressure_ratings.csv",
    "data/processed/bowler_pressure_ratings.csv",
    "reports/pressure_engine_report.txt",
    "dashboard/superrr_selector_dashboard.html",
]

print("\nSUPERR SELECTOR - FINAL PROJECT CHECK")
print("=" * 50)

failed = False

for file in required_files:
    path = ROOT / file
    if path.exists() and path.stat().st_size > 0:
        print(f"[PASS] {file}")
    else:
        print(f"[FAIL] {file}")
        failed = True

if not failed:
    batters = pd.read_csv(ROOT / "data/processed/batter_pressure_ratings.csv")
    bowlers = pd.read_csv(ROOT / "data/processed/bowler_pressure_ratings.csv")

    print("\nPLAYER RATING VALIDATION")
    print("-" * 50)

    print(f"Qualified batters: {len(batters)}")
    print(f"Qualified bowlers: {len(bowlers)}")

    print("Unique batter names:", batters["striker_name"].nunique())
    print("Unique bowler names:", bowlers["bowler_name"].nunique())

    print("Missing batter scores:", batters["batting_pressure_score"].isna().sum())
    print("Missing bowler scores:", bowlers["bowling_pressure_score"].isna().sum())

    print("\nTOP BATTER:", batters.nlargest(1, "batting_pressure_score")["striker_name"].iloc[0])
    print("TOP BOWLER:", bowlers.nlargest(1, "bowling_pressure_score")["bowler_name"].iloc[0])

    print("\nFINAL STATUS:", "CHECK COMPLETE" if not failed else "ISSUES FOUND")
else:
    print("\nSome required files are missing. Fix those before proceeding.")
