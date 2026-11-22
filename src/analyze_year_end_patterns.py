from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data" / "raw"
REPORTS_DIR = PROJECT_DIR / "reports"

SALES_FILE = DATA_DIR / "sales_train_validation.csv"
CALENDAR_FILE = DATA_DIR / "calendar.csv"

print("=" * 70)
print("SIGNALSENTINEL AI - YEAR-END SALES PATTERN ANALYSIS")
print("=" * 70)

# --------------------------------------------------
# 1. Load the sales dataset
# --------------------------------------------------

print("\n1. Loading sales data...")

sales = pd.read_csv(SALES_FILE)

daily_columns = [
    column for column in sales.columns
    if column.startswith("d_")
]

print("Product-store records:", len(sales))
print("Daily sales columns:", len(daily_columns))

# Aggregate sales across all products and stores.
print("\n2. Aggregating total daily sales...")

daily_totals = sales[daily_columns].sum(axis=0)

daily_sales = daily_totals.rename("total_units").reset_index()

daily_sales.columns = ["d", "total_units"]

# --------------------------------------------------
# 2. Map day identifiers to actual calendar dates
# --------------------------------------------------

print("3. Mapping sales days to calendar dates...")

calendar = pd.read_csv(CALENDAR_FILE)

calendar["date"] = pd.to_datetime(calendar["date"])

day_map = calendar[["d", "date"]].copy()

daily_sales = daily_sales.merge(
    day_map,
    on="d",
    how="left",
    validate="one_to_one",
)

if daily_sales["date"].isna().any():
    raise ValueError("Some sales days could not be mapped to dates.")

daily_sales["year"] = daily_sales["date"].dt.year
daily_sales["month"] = daily_sales["date"].dt.month
daily_sales["day"] = daily_sales["date"].dt.day
daily_sales["weekday"] = daily_sales["date"].dt.day_name()

# Keep the full daily history in a report.
daily_output = REPORTS_DIR / "year_end_daily_sales.csv"
daily_sales.to_csv(daily_output, index=False)

# --------------------------------------------------
# 3. Compare November, December, and January
# --------------------------------------------------

print("\n4. MONTHLY SALES COMPARISON")

# Exclude incomplete calendar months at the beginning
# and end of the dataset from this comparison.
monthly = (
    daily_sales.groupby(["year", "month"])
    .agg(
        days_observed=("date", "count"),
        average_daily_units=("total_units", "mean"),
        median_daily_units=("total_units", "median"),
        minimum_daily_units=("total_units", "min"),
        maximum_daily_units=("total_units", "max"),
    )
    .reset_index()
)

monthly["average_daily_units"] = (
    monthly["average_daily_units"].round(2)
)

monthly["median_daily_units"] = (
    monthly["median_daily_units"].round(2)
)

monthly["minimum_daily_units"] = (
    monthly["minimum_daily_units"].round(2)
)

monthly["maximum_daily_units"] = (
    monthly["maximum_daily_units"].round(2)
)

selected_months = monthly[
    monthly["month"].isin([11, 12, 1])
].copy()

month_names = {
    1: "January",
    11: "November",
    12: "December",
}

selected_months["month_name"] = (
    selected_months["month"].map(month_names)
)

print(
    selected_months[
        [
            "year",
            "month_name",
            "days_observed",
            "average_daily_units",
            "median_daily_units",
            "minimum_daily_units",
            "maximum_daily_units",
        ]
    ].to_string(index=False)
)

monthly_output = REPORTS_DIR / "year_end_monthly_comparison.csv"
selected_months.to_csv(monthly_output, index=False)

# --------------------------------------------------
# 4. Inspect daily sales around December 25-31
# --------------------------------------------------

print("\n5. DAILY SALES FROM DECEMBER 20-31")

december = daily_sales[
    (daily_sales["month"] == 12)
    & (daily_sales["day"].between(20, 31))
].copy()

print(
    december[
        ["date", "weekday", "total_units"]
    ].to_string(index=False)
)

december_output = REPORTS_DIR / "december_daily_sales.csv"
december.to_csv(december_output, index=False)

# --------------------------------------------------
# 5. Compare the same dates across years
# --------------------------------------------------

print("\n6. YEAR-END SALES BY CALENDAR DAY")

year_end_summary = (
    december.groupby("day")
    .agg(
        years_observed=("year", "nunique"),
        average_units=("total_units", "mean"),
        median_units=("total_units", "median"),
        minimum_units=("total_units", "min"),
        maximum_units=("total_units", "max"),
    )
    .reset_index()
)

for column in [
    "average_units",
    "median_units",
    "minimum_units",
    "maximum_units",
]:
    year_end_summary[column] = (
        year_end_summary[column].round(2)
    )

print(year_end_summary.to_string(index=False))

year_end_output = REPORTS_DIR / "year_end_by_calendar_day.csv"
year_end_summary.to_csv(year_end_output, index=False)

# --------------------------------------------------
# 6. Plot December sales for each year
# --------------------------------------------------

print("\n7. Creating the year-end sales chart...")

plt.figure(figsize=(12, 6))

for year, group in december.groupby("year"):
    group = group.sort_values("date")

    plt.plot(
        group["day"],
        group["total_units"],
        marker="o",
        label=str(year),
    )

plt.title("Daily Total Sales: December 20-31 Across Years")
plt.xlabel("Day of December")
plt.ylabel("Total Units Sold")
plt.xticks(range(20, 32))
plt.legend(title="Year")
plt.grid(True, alpha=0.3)
plt.tight_layout()

chart_output = REPORTS_DIR / "year_end_sales_patterns.png"

plt.savefig(chart_output, dpi=150)
plt.close()

# --------------------------------------------------
# 7. Final report
# --------------------------------------------------

print("\n8. OUTPUT FILES")
print("Daily sales history:", daily_output)
print("Monthly comparison:", monthly_output)
print("December daily sales:", december_output)
print("Year-end day summary:", year_end_output)
print("Chart:", chart_output)

print("\nAnalysis completed.")
print(
    "Reminder: differences between years may reflect "
    "seasonality, weekday effects, trends, or other factors."
)