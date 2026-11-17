import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

PROCESSED.mkdir(parents=True, exist_ok=True)

print("\nSUPERR SELECTOR - DATA CLEANING")
print("=" * 60)

files = sorted(RAW.rglob("*.csv"))

for file in files:
    print(f"\nProcessing: {file.name}")

    try:
        df = pd.read_csv(file, low_memory=False)

        original_rows = len(df)

        # Standardize column names
        df.columns = (
            df.columns.astype(str)
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )

        # Remove exact duplicate rows
        duplicates = df.duplicated().sum()
        df = df.drop_duplicates()

        # Save cleaned dataset
        output_name = file.stem + "_cleaned.csv"
        output_path = PROCESSED / output_name

        df.to_csv(output_path, index=False)

        print("Original rows:", original_rows)
        print("Duplicates removed:", duplicates)
        print("Final rows:", len(df))
        print("Saved:", output_path.name)

    except Exception as error:
        print("ERROR:", error)

print("\n" + "=" * 60)
print("CLEANING PROCESS COMPLETED")
print("Original files remain unchanged.")
print("Cleaned files saved in data/processed/")
