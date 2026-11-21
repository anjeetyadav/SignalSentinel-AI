from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"

print("=" * 60)
print("SIGNALSENTINEL AI - DATASET SUMMARY")
print("=" * 60)

# 1. Inspect the calendar
calendar = pd.read_csv(RAW_DATA_DIR / "calendar.csv")

print("\n1. CALENDAR")
print("Rows:", len(calendar))
print("Columns:", len(calendar.columns))
print("First date:", calendar["date"].min())
print("Last date:", calendar["date"].max())
print("Unique calendar days:", calendar["d"].nunique())

# 2. Inspect the sales files using only their headers and IDs
for filename in [
    "sales_train_validation.csv",
    "sales_train_evaluation.csv",
]:
    path = RAW_DATA_DIR / filename

    print(f"\n2. {filename}")

    # Read the identifiers and column names without loading all sales values
    df = pd.read_csv(
        path,
        usecols=["id", "item_id", "dept_id", "cat_id", "store_id", "state_id"],
    )

    print("Product/store records:", len(df))
    print("Unique IDs:", df["id"].nunique())
    print("Unique products:", df["item_id"].nunique())
    print("Unique departments:", df["dept_id"].nunique())
    print("Unique categories:", df["cat_id"].nunique())
    print("Unique stores:", df["store_id"].nunique())
    print("Unique states:", df["state_id"].nunique())

# 3. Inspect the price file
prices = pd.read_csv(RAW_DATA_DIR / "sell_prices.csv")

print("\n3. SELL PRICES")
print("Rows:", len(prices))
print("Columns:", len(prices.columns))
print("Unique products:", prices["item_id"].nunique())
print("Unique stores:", prices["store_id"].nunique())
print("Missing values by column:")
print(prices.isna().sum().to_string())

print("\n" + "=" * 60)
print("DATASET SUMMARY COMPLETED")
print("=" * 60)