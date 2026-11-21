from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"
REPORTS_DIR = PROJECT_DIR / "reports"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 65)
print("SIGNALSENTINEL AI - CATEGORY SALES ANALYSIS")
print("=" * 65)

# Load sales data
print("\n1. Loading sales data...")

daily_columns = [f"d_{i}" for i in range(1, 1914)]

sales = pd.read_csv(
    RAW_DATA_DIR / "sales_train_validation.csv",
    usecols=["cat_id"] + daily_columns,
)

# Aggregate sales by category
print("2. Calculating category totals...")

category_totals = sales.groupby("cat_id")[daily_columns].sum()

category_summary = pd.DataFrame({
    "total_units_sold": category_totals.sum(axis=1),
    "average_daily_units": category_totals.mean(axis=1),
    "minimum_daily_units": category_totals.min(axis=1),
    "maximum_daily_units": category_totals.max(axis=1),
})

category_summary = category_summary.sort_values(
    "total_units_sold",
    ascending=False,
)

print("\nTOTAL SALES BY CATEGORY")
print(category_summary.round(2).to_string())

# Convert to long format
print("\n3. Preparing daily category trends...")

daily_category = (
    category_totals
    .rename_axis("category")
    .reset_index()
    .melt(
        id_vars="category",
        var_name="d",
        value_name="units_sold",
    )
)

# Merge actual dates
calendar = pd.read_csv(
    RAW_DATA_DIR / "calendar.csv",
    usecols=["d", "date"],
)

calendar["date"] = pd.to_datetime(calendar["date"])

daily_category = daily_category.merge(
    calendar,
    on="d",
    how="left",
    validate="many_to_one",
)

daily_category = daily_category.sort_values(
    ["category", "date"]
).reset_index(drop=True)

# Save daily category data
daily_output = REPORTS_DIR / "daily_category_sales.csv"
daily_category.to_csv(daily_output, index=False)

# Summarize by year
print("4. Calculating yearly category trends...")

daily_category["year"] = daily_category["date"].dt.year

yearly_summary = (
    daily_category
    .groupby(["year", "category"])["units_sold"]
    .agg(["sum", "mean", "median"])
    .reset_index()
)

yearly_output = REPORTS_DIR / "yearly_category_sales.csv"
yearly_summary.to_csv(yearly_output, index=False)

print("\nYEARLY AVERAGE DAILY SALES BY CATEGORY")
print(
    yearly_summary.pivot(
        index="year",
        columns="category",
        values="mean",
    ).round(2).to_string()
)

# Plot 28-day rolling averages
print("\n5. Creating category trend chart...")

plt.figure(figsize=(14, 7))

for category in category_totals.index:
    category_data = daily_category[
        daily_category["category"] == category
    ].sort_values("date")

    rolling_sales = category_data["units_sold"].rolling(
        window=28,
        min_periods=28,
    ).mean()

    plt.plot(
        category_data["date"],
        rolling_sales,
        label=category,
        linewidth=2,
    )

plt.title("SignalSentinel AI - 28-Day Average Sales by Category")
plt.xlabel("Date")
plt.ylabel("Average Daily Units Sold")
plt.legend(title="Category")
plt.grid(True, alpha=0.3)
plt.tight_layout()

chart_output = REPORTS_DIR / "category_sales_trends.png"
plt.savefig(chart_output, dpi=150)
plt.close()

print("\n6. OUTPUT FILES")
print("Daily category sales:", daily_output)
print("Yearly category sales:", yearly_output)
print("Category trend chart:", chart_output)

print("\nCategory sales analysis completed successfully.")