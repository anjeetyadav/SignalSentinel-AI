from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"
REPORTS_DIR = PROJECT_DIR / "reports"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)

sales_path = RAW_DATA_DIR / "sales_train_validation.csv"
calendar_path = RAW_DATA_DIR / "calendar.csv"

print("Loading sales data...")

sales = pd.read_csv(sales_path)
calendar = pd.read_csv(calendar_path)

daily_columns = [
    column for column in sales.columns
    if column.startswith("d_")
]

print("Calculating total daily sales...")

# Sum sales across all products and stores for each day.
daily_totals = sales[daily_columns].sum(axis=0)

daily_sales = pd.DataFrame({
    "d": daily_totals.index,
    "total_units_sold": daily_totals.values,
})

# Join the sales totals to actual calendar dates.
daily_sales = daily_sales.merge(
    calendar[["d", "date"]],
    on="d",
    how="left",
    validate="one_to_one",
)

daily_sales["date"] = pd.to_datetime(daily_sales["date"])
daily_sales = daily_sales.sort_values("date")

print("\n1. DAILY SALES SUMMARY")
print("Number of days:", len(daily_sales))
print("First date:", daily_sales["date"].min().date())
print("Last date:", daily_sales["date"].max().date())
print("Average total units per day:",
      round(daily_sales["total_units_sold"].mean(), 2))
print("Minimum daily total:",
      int(daily_sales["total_units_sold"].min()))
print("Maximum daily total:",
      int(daily_sales["total_units_sold"].max()))

print("\n2. FIVE LOWEST-SELLING DAYS")
print(
    daily_sales.nsmallest(5, "total_units_sold")[
        ["date", "d", "total_units_sold"]
    ].to_string(index=False)
)

print("\n3. FIVE HIGHEST-SELLING DAYS")
print(
    daily_sales.nlargest(5, "total_units_sold")[
        ["date", "d", "total_units_sold"]
    ].to_string(index=False)
)

# Save daily totals for later project steps.
output_csv = REPORTS_DIR / "daily_sales_totals.csv"
daily_sales.to_csv(output_csv, index=False)

# Plot daily sales.
plt.figure(figsize=(14, 6))
plt.plot(
    daily_sales["date"],
    daily_sales["total_units_sold"],
)
plt.title("SignalSentinel AI - Total Daily Units Sold")
plt.xlabel("Date")
plt.ylabel("Total Units Sold")
plt.tight_layout()

output_plot = REPORTS_DIR / "daily_sales_trend.png"
plt.savefig(output_plot, dpi=150)
plt.close()

print("\nSaved daily totals:", output_csv)
print("Saved sales trend chart:", output_plot)
print("\nDaily sales analysis completed.")