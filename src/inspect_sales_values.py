from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"

sales_path = RAW_DATA_DIR / "sales_train_validation.csv"

print("=" * 60)
print("SIGNALSENTINEL AI - SALES VALUE INSPECTION")
print("=" * 60)

print("\nLoading sales data...")
sales = pd.read_csv(sales_path)

identifier_columns = [
    "id",
    "item_id",
    "dept_id",
    "cat_id",
    "store_id",
    "state_id",
]

daily_columns = [
    column for column in sales.columns
    if column.startswith("d_")
]

print("\n1. DATASET SIZE")
print("Rows:", len(sales))
print("Daily sales columns:", len(daily_columns))

print("\n2. MISSING VALUES")
print("Total missing sales values:",
      int(sales[daily_columns].isna().sum().sum()))

print("\n3. SALES VALUE STATISTICS")

# Convert the daily sales matrix to a NumPy array for calculations.
# This avoids creating another large pandas DataFrame.
sales_values = sales[daily_columns].to_numpy(dtype=np.float32)

print("Minimum daily sales:", float(np.nanmin(sales_values)))
print("Maximum daily sales:", float(np.nanmax(sales_values)))
print("Average daily sales:", float(np.nanmean(sales_values)))
print("Total recorded sales:", float(np.nansum(sales_values)))

print("\n4. ZERO AND NEGATIVE SALES")
print("Number of zero-valued daily entries:",
      int(np.sum(sales_values == 0)))

print("Number of negative daily entries:",
      int(np.sum(sales_values < 0)))

print("\n5. PRODUCT/STORE RECORDS WITH SALES")

record_totals = np.nansum(sales_values, axis=1)

print("Records with total sales above zero:",
      int(np.sum(record_totals > 0)))

print("Records with zero total sales:",
      int(np.sum(record_totals == 0)))

print("\n6. SALES BY CATEGORY")

category_totals = (
    sales.assign(total_sales=record_totals)
    .groupby("cat_id")["total_sales"]
    .sum()
    .sort_values(ascending=False)
)

print(category_totals.to_string())

print("\n" + "=" * 60)
print("SALES VALUE INSPECTION COMPLETED")
print("=" * 60)