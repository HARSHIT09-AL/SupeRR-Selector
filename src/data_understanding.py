import pandas as pd
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data" / "raw"

csv_files = list(DATA_DIR.glob("*.csv"))

if not csv_files:
    print("ERROR: No CSV files found in data/raw!")
else:
    for file in csv_files:
        df = pd.read_csv(file)

        print("\n" + "=" * 70)
        print("FILE:", file.name)
        print("=" * 70)

        print("Rows:", df.shape[0])
        print("Columns:", df.shape[1])

        print("\nColumn names:")
        print(df.columns.tolist())

        print("\nFirst 5 records:")
        print(df.head().to_string())

        print("\nMissing values:")
        print(df.isnull().sum().to_string())
