import pandas as pd

# Load the existing daily sales report
file_path = "reports/daily_store_sales.csv"
data = pd.read_csv(file_path)

data["date"] = pd.to_datetime(data["date"])

# Select the four-day investigation period
start_date = "2015-11-26"
end_date = "2015-11-29"

period = data[
    (data["date"] >= start_date)
    & (data["date"] <= end_date)
].copy()

# Summarize sales for each store during the period
summary = (
    period.groupby("store_id")
    .agg(
        total_units=("units_sold", "sum"),
        average_daily_units=("units_sold", "mean"),
        minimum_daily_units=("units_sold", "min"),
        maximum_daily_units=("units_sold", "max"),
        days_recorded=("date", "nunique")
    )
    .reset_index()
)

summary = summary.sort_values(
    "total_units",
    ascending=True
)

print("\nSTORE-LEVEL SALES: NOVEMBER 26-29, 2015")
print(summary.to_string(index=False))

# Display daily sales for every store
print("\nDAILY SALES BY STORE")

daily = period.pivot(
    index="store_id",
    columns="date",
    values="units_sold"
)

print(daily.to_string())

# Save the investigation reports
summary.to_csv(
    "reports/november_2015_store_summary.csv",
    index=False
)

daily.to_csv(
    "reports/november_2015_daily_store_sales.csv"
)

print("\nReports saved:")
print("reports/november_2015_store_summary.csv")
print("reports/november_2015_daily_store_sales.csv")