from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_DIR / "reports"
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"

daily_sales = pd.read_csv(
    REPORTS_DIR / "daily_sales_totals.csv",
    parse_dates=["date"],
)

calendar = pd.read_csv(
    RAW_DATA_DIR / "calendar.csv",
    usecols=["d", "weekday", "wday"],
)

daily_sales = daily_sales.merge(
    calendar,
    on="d",
    how="left",
    validate="one_to_one",
)

print("=" * 60)
print("SIGNALSENTINEL AI - WEEKLY SALES PATTERNS")
print("=" * 60)

weekday_summary = (
    daily_sales.groupby(["wday", "weekday"])["total_units_sold"]
    .agg(["mean", "median", "std", "count"])
    .reset_index()
    .sort_values("wday")
)

weekday_summary = weekday_summary.rename(
    columns={
        "mean": "average_sales",
        "median": "median_sales",
        "std": "sales_std_dev",
        "count": "number_of_days",
    }
)

print("\nAVERAGE SALES BY WEEKDAY")
print(weekday_summary.round(2).to_string(index=False))

output_csv = REPORTS_DIR / "weekday_sales_summary.csv"
weekday_summary.to_csv(output_csv, index=False)

plt.figure(figsize=(10, 5))
plt.bar(
    weekday_summary["weekday"],
    weekday_summary["average_sales"],
)
plt.title("Average Daily Sales by Weekday")
plt.xlabel("Weekday")
plt.ylabel("Average Units Sold")
plt.xticks(rotation=30)
plt.tight_layout()

output_plot = REPORTS_DIR / "weekday_sales_patterns.png"
plt.savefig(output_plot, dpi=150)
plt.close()

print("\nSaved summary:", output_csv)
print("Saved chart:", output_plot)
print("\nWeekly pattern analysis completed.")