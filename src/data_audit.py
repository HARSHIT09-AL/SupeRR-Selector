import pandas as pd
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
REPORTS = ROOT / "reports"

REPORTS.mkdir(exist_ok=True)

print("\n" + "=" * 65)
print("             SUPERR SELECTOR - DATA AUDIT")
print("=" * 65)

csv_files = sorted(RAW.rglob("*.csv"))

if not csv_files:
    print("ERROR: No CSV files found!")
    raise SystemExit

summary = []

for file in csv_files:
    print(f"\nInspecting: {file.name}")

    try:
        df = pd.read_csv(file, low_memory=False)

        print(f"Rows: {len(df):,}")
        print(f"Columns: {len(df.columns)}")
        print(f"Duplicate rows: {df.duplicated().sum():,}")
        print(f"Missing cells: {df.isna().sum().sum():,}")

        summary.append({
            "file": str(file.relative_to(RAW)),
            "rows": len(df),
            "columns": len(df.columns),
            "duplicate_rows": int(df.duplicated().sum()),
            "missing_cells": int(df.isna().sum().sum()),
            "column_names": ", ".join(df.columns.astype(str))
        })

        missing = df.isna().sum()
        missing = missing[missing > 0]

        if not missing.empty:
            print("Columns with missing values:")
            print(missing.to_string())

    except Exception as error:
        print("ERROR:", error)

report = pd.DataFrame(summary)

report.to_csv(REPORTS / "data_audit_summary.csv", index=False)

with open(REPORTS / "data_audit_summary.json", "w") as f:
    json.dump(summary, f, indent=4)

print("\n" + "=" * 65)
print("DATA AUDIT COMPLETED")
print("=" * 65)
print(f"Datasets inspected: {len(summary)}")
print("Reports saved in:", REPORTS)
