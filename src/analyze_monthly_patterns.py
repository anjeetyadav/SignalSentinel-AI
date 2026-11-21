from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_DIR / "reports"

daily_sales = pd.read_csv(
    REPORTS_DIR / "daily_sales_totals.csv",
    parse_dates=["date"],
)

daily_sales["year"] = daily_sales["date"].dt.year
daily_sales["month"] = daily_sales["date"].dt.month
daily_sales["month_name"] = daily_sales["date"].dt.strftime("%b")

print("=" * 60)
print("SIGNALSENTINEL AI - MONTHLY SALES PATTERNS")
print("=" * 60)

# Average daily sales for each calendar month, across all available years.
monthly_summary = (
    daily_sales.groupby("month")
    .agg(
        average_daily_sales=("total_units_sold", "mean"),
        median_daily_sales=("total_units_sold", "median"),
        minimum_daily_sales=("total_units_sold", "min"),
        maximum_daily_sales=("total_units_sold", "max"),
        number_of_days=("total_units_sold", "count"),
    )
    .reset_index()
)

monthly_summary["month_name"] = monthly_summary["month"].map(
    {
        1: "Jan",
        2: "Feb",
        3: "Mar",
        4: "Apr",
        5: "May",
        6: "Jun",
        7: "Jul",
        8: "Aug",
        9: "Sep",
        10: "Oct",
        11: "Nov",
        12: "Dec",
    }
)

print("\n1. AVERAGE DAILY SALES BY MONTH")
print(
    monthly_summary[
        [
            "month_name",
            "average_daily_sales",
            "median_daily_sales",
            "number_of_days",
        ]
    ].round(2).to_string(index=False)
)

# Compare average daily sales for each year.
yearly_summary = (
    daily_sales.groupby("year")["total_units_sold"]
    .agg(["mean", "median", "min", "max", "count"])
    .reset_index()
)

yearly_summary = yearly_summary.rename(
    columns={
        "mean": "average_daily_sales",
        "median": "median_daily_sales",
        "min": "minimum_daily_sales",
        "max": "maximum_daily_sales",
        "count": "number_of_days",
    }
)

print("\n2. AVERAGE DAILY SALES BY YEAR")
print(yearly_summary.round(2).to_string(index=False))

monthly_summary.to_csv(
    REPORTS_DIR / "monthly_sales_summary.csv",
    index=False,
)

yearly_summary.to_csv(
    REPORTS_DIR / "yearly_sales_summary.csv",
    index=False,
)

plt.figure(figsize=(10, 5))
plt.bar(
    monthly_summary["month_name"],
    monthly_summary["average_daily_sales"],
)
plt.title("Average Daily Sales by Calendar Month")
plt.xlabel("Month")
plt.ylabel("Average Units Sold")
plt.tight_layout()
plt.savefig(
    REPORTS_DIR / "monthly_sales_patterns.png",
    dpi=150,
)
plt.close()

print("\nSaved monthly summary: reports/monthly_sales_summary.csv")
print("Saved yearly summary: reports/yearly_sales_summary.csv")
print("Saved chart: reports/monthly_sales_patterns.png")
print("\nMonthly pattern analysis completed.")