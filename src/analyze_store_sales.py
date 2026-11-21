from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"
REPORTS_DIR = PROJECT_DIR / "reports"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 65)
print("SIGNALSENTINEL AI - STORE SALES ANALYSIS")
print("=" * 65)

# Load store identifiers and daily sales
print("\n1. Loading sales data...")

daily_columns = [f"d_{i}" for i in range(1, 1914)]

sales = pd.read_csv(
    RAW_DATA_DIR / "sales_train_validation.csv",
    usecols=["store_id"] + daily_columns,
)

# Calculate total daily sales for each store
print("2. Aggregating daily sales by store...")

store_daily = sales.groupby("store_id")[daily_columns].sum()

# Summarize each store
store_summary = pd.DataFrame({
    "total_units_sold": store_daily.sum(axis=1),
    "average_daily_units": store_daily.mean(axis=1),
    "minimum_daily_units": store_daily.min(axis=1),
    "maximum_daily_units": store_daily.max(axis=1),
})

store_summary["sales_share_percent"] = (
    store_summary["total_units_sold"]
    / store_summary["total_units_sold"].sum()
    * 100
)

store_summary = store_summary.sort_values(
    "total_units_sold",
    ascending=False,
)

print("\n3. STORE SALES SUMMARY")
print(store_summary.round(2).to_string())

# Prepare daily store sales with actual dates
print("\n4. Preparing daily store trends...")

store_daily_long = (
    store_daily
    .rename_axis("store_id")
    .reset_index()
    .melt(
        id_vars="store_id",
        var_name="d",
        value_name="units_sold",
    )
)

calendar = pd.read_csv(
    RAW_DATA_DIR / "calendar.csv",
    usecols=["d", "date"],
)

calendar["date"] = pd.to_datetime(calendar["date"])

store_daily_long = store_daily_long.merge(
    calendar,
    on="d",
    how="left",
    validate="many_to_one",
)

store_daily_long = store_daily_long.sort_values(
    ["store_id", "date"]
).reset_index(drop=True)

# Save daily store sales
daily_output = REPORTS_DIR / "daily_store_sales.csv"
store_daily_long.to_csv(daily_output, index=False)

# Save store summary
summary_output = REPORTS_DIR / "store_sales_summary.csv"
store_summary.to_csv(summary_output)

# Plot 28-day rolling averages
print("\n5. Creating store trend chart...")

plt.figure(figsize=(14, 7))

for store_id, group in store_daily_long.groupby("store_id"):
    group = group.sort_values("date")

    rolling_sales = group["units_sold"].rolling(
        window=28,
        min_periods=28,
    ).mean()

    plt.plot(
        group["date"],
        rolling_sales,
        label=store_id,
        linewidth=1.5,
    )

plt.title("SignalSentinel AI - 28-Day Average Sales by Store")
plt.xlabel("Date")
plt.ylabel("Average Daily Units Sold")
plt.legend(title="Store", ncol=2)
plt.grid(True, alpha=0.3)
plt.tight_layout()

chart_output = REPORTS_DIR / "store_sales_trends.png"
plt.savefig(chart_output, dpi=150)
plt.close()

print("\n6. OUTPUT FILES")
print("Daily store sales:", daily_output)
print("Store summary:", summary_output)
print("Store trend chart:", chart_output)

print("\nStore sales analysis completed successfully.")