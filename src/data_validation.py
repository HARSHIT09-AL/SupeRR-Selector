import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"

REPORTS.mkdir(exist_ok=True)

print("\nSUPERR SELECTOR - CRICKET DATA VALIDATION")
print("=" * 65)

files = list(DATA.glob("*_cleaned.csv"))

if not files:
    print("No cleaned CSV files found!")
    raise SystemExit

results = []

for file in files:
    df = pd.read_csv(file, low_memory=False)

    print(f"\nDATASET: {file.name}")
    print("-" * 55)

    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    checks = {
        "empty_rows": int(df.isna().all(axis=1).sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_columns": int(df.columns.duplicated().sum())
    }

    for check, value in checks.items():
        print(f"{check}: {value}")

    results.append({
        "dataset": file.name,
        **checks
    })

    # Show possible cricket identifier columns
    possible_ids = [
        col for col in df.columns
        if any(word in col for word in ["match_id", "player_id", "team_id"])
    ]

    if possible_ids:
        print("\nIdentifier columns:")
        for col in possible_ids:
            print(f"{col}: {df[col].nunique(dropna=True)} unique values")

report = pd.DataFrame(results)
report.to_csv(REPORTS / "validation_report.csv", index=False)

print("\n" + "=" * 65)
print("VALIDATION COMPLETED")
print("Report saved: reports/validation_report.csv")
print("=" * 65)
