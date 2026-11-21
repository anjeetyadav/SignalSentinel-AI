from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"
REPORTS_DIR = PROJECT_DIR / "reports"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 65)
print("SIGNALSENTINEL AI - STORE SALES DECLINE DETECTOR")
print("=" * 65)

# Load the daily sales history for all product-store combinations.
print("\n1. Loading sales data...")

daily_columns = [f"d_{i}" for i in range(1, 1914)]

sales = pd.read_csv(
    RAW_DATA_DIR / "sales_train_validation.csv",
    usecols=["store_id"] + daily_columns,
)

# Aggregate product sales to obtain total daily units for each store.
print("2. Aggregating daily store sales...")

store_daily = sales.groupby("store_id")[daily_columns].sum()

# Convert the data into one row per store per day.
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

print("3. Calculating recent sales changes...")

# The baseline ends before the recent 7-day period begins.
# Both windows use only historical observations available at that date.
store_daily_long["recent_7d_avg"] = (
    store_daily_long.groupby("store_id")["units_sold"]
    .transform(lambda s: s.rolling(7, min_periods=7).mean())
)

store_daily_long["previous_28d_avg"] = (
    store_daily_long.groupby("store_id")["units_sold"]
    .transform(lambda s: s.shift(7).rolling(28, min_periods=28).mean())
)

store_daily_long["change_percent"] = (
    (
        store_daily_long["recent_7d_avg"]
        - store_daily_long["previous_28d_avg"]
    )
    / store_daily_long["previous_28d_avg"].replace(0, pd.NA)
    * 100
)

# Initial exploratory threshold; this is not a validated business rule.
store_daily_long["potential_decline_alert"] = (
    store_daily_long["change_percent"] <= -15
)

# Keep rows with enough history to calculate both averages.
results = store_daily_long.dropna(
    subset=["recent_7d_avg", "previous_28d_avg", "change_percent"]
).copy()

results["recent_7d_avg"] = results["recent_7d_avg"].round(2)
results["previous_28d_avg"] = results["previous_28d_avg"].round(2)
results["change_percent"] = results["change_percent"].round(2)

print("\n4. SUMMARY BY STORE")

summary = (
    results.groupby("store_id")
    .agg(
        days_analyzed=("change_percent", "count"),
        alert_days=("potential_decline_alert", "sum"),
        average_change_percent=("change_percent", "mean"),
        worst_change_percent=("change_percent", "min"),
    )
    .sort_values("alert_days", ascending=False)
)

print(summary.round(2).to_string())

print("\n5. MOST RECENT POTENTIAL DECLINES")

latest_date = results["date"].max()
latest_results = results[results["date"] == latest_date].copy()

latest_results = latest_results.sort_values("change_percent")

columns_to_show = [
    "store_id",
    "date",
    "recent_7d_avg",
    "previous_28d_avg",
    "change_percent",
    "potential_decline_alert",
]

print("Latest date available:", latest_date.date())
print(latest_results[columns_to_show].to_string(index=False))

# Save detailed daily results and store-level summary.
daily_output = REPORTS_DIR / "store_decline_analysis.csv"
summary_output = REPORTS_DIR / "store_decline_summary.csv"

results.to_csv(daily_output, index=False)
summary.to_csv(summary_output)

print("\n6. OUTPUT FILES")
print("Detailed analysis:", daily_output)
print("Store summary:", summary_output)

print("\nStore decline analysis completed successfully.")