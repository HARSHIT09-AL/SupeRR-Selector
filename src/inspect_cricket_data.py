import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"

REPORTS.mkdir(exist_ok=True)

files = list(DATA.glob("*_cleaned.csv"))

targets = ["ball_by_ball", "matches"]

output = []

for target in targets:

    matches = [f for f in files if target in f.stem.lower()]

    if not matches:
        output.append(f"\nDATASET NOT FOUND: {target}")
        continue

    file = matches[0]
    df = pd.read_csv(file, low_memory=False)

    output.append("\n" + "=" * 70)
    output.append(f"DATASET: {file.name}")
    output.append("=" * 70)

    output.append(f"Rows: {len(df):,}")
    output.append(f"Columns: {len(df.columns)}")

    output.append("\nCOLUMN NAMES AND DATA TYPES:")

    for col in df.columns:
        output.append(f"{col}: {df[col].dtype}")

    output.append("\nFIRST 3 RECORDS:")
    output.append(df.head(3).to_string(index=False))

    output.append("\nUNIQUE VALUES IN IMPORTANT COLUMNS:")

    for col in df.columns:
        if any(word in col for word in [
            "match", "innings", "over", "ball",
            "batter", "bowler", "team", "wicket",
            "run", "date", "competition"
        ]):
            output.append(
                f"{col}: {df[col].nunique(dropna=True)} unique values"
            )

report = "\n".join(output)

print(report)

(REPORTS / "cricket_schema_report.txt").write_text(
    report, encoding="utf-8"
)

print("\nSchema report saved successfully!")
