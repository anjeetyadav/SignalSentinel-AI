from pathlib import Path
import pandas as pd

# Locate the project and raw data folders
PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"

# Files we want to inspect
files = [
    "calendar.csv",
    "sales_train_validation.csv",
    "sales_train_evaluation.csv",
    "sample_submission.csv",
    "sell_prices.csv",
]

print("=" * 60)
print("SIGNALSENTINEL AI - DATASET INSPECTION")
print("=" * 60)

for filename in files:
    file_path = RAW_DATA_DIR / filename

    print(f"\n{'-' * 60}")
    print(f"FILE: {filename}")
    print("-" * 60)

    if not file_path.exists():
        print("ERROR: File not found!")
        continue

    # Read only the first five rows for this initial inspection
    df = pd.read_csv(file_path, nrows=5)

    print(f"Columns: {len(df.columns)}")
    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nFirst 5 rows:")
    print(df.head().to_string(index=False))

print("\n" + "=" * 60)
print("INITIAL INSPECTION COMPLETED")
print("=" * 60)