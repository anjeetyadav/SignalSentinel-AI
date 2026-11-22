from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"

files = [
    "sales_train_validation.csv",
    "sales_train_evaluation.csv",
]

for filename in files:
    path = RAW_DATA_DIR / filename

    print("\n" + "=" * 65)
    print(filename)
    print("=" * 65)

    # Read only the header; do not load the full sales data
    columns = pd.read_csv(path, nrows=0).columns.tolist()

    identifier_columns = [
        "id",
        "item_id",
        "dept_id",
        "cat_id",
        "store_id",
        "state_id",
    ]

    daily_columns = [
        column for column in columns
        if column.startswith("d_")
    ]

    print("Total columns:", len(columns))
    print("Identifier columns:", len(identifier_columns))
    print("Daily sales columns:", len(daily_columns))

    print("First 5 daily columns:", daily_columns[:5])
    print("Last 5 daily columns:", daily_columns[-5:])

    print("Contains d_1913:", "d_1913" in daily_columns)
    print("Contains d_1941:", "d_1941" in daily_columns)

print("\nInspection completed.")