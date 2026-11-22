from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"
REPORTS_DIR = PROJECT_DIR / "reports"

sales = pd.read_csv(
    REPORTS_DIR / "daily_sales_totals.csv",
    parse_dates=["date"],
)

calendar = pd.read_csv(
    RAW_DATA_DIR / "calendar.csv",
)

calendar["date"] = pd.to_datetime(calendar["date"])

data = sales.merge(
    calendar,
    on=["d", "date"],
    how="left",
    validate="one_to_one",
)

# Combine the two event fields into one event description.
data["calendar_event"] = data["event_name_1"].fillna(
    data["event_name_2"]
)

data["calendar_event_type"] = data["event_type_1"].fillna(
    data["event_type_2"]
)

event_days = data.loc[data["calendar_event"].notna()].copy()

print("=" * 65)
print("SIGNALSENTINEL AI - CALENDAR EVENT ANALYSIS")
print("=" * 65)

print("\n1. DATA COVERAGE")
print("Total historical days:", len(data))
print("Days with a recorded event:", len(event_days))
print("Days without a recorded event:",
      int(data["calendar_event"].isna().sum()))

print("\n2. EVENT FREQUENCY")
print(
    event_days["calendar_event"]
    .value_counts()
    .to_string()
)

print("\n3. SALES BY EVENT")
event_summary = (
    event_days.groupby("calendar_event")["total_units_sold"]
    .agg(["count", "mean", "median", "min", "max"])
    .sort_values("count", ascending=False)
)

print(event_summary.round(2).to_string())

print("\n4. EVENT TYPE FREQUENCY")
print(
    event_days["calendar_event_type"]
    .value_counts(dropna=False)
    .to_string()
)

output_path = REPORTS_DIR / "calendar_event_summary.csv"
event_summary.to_csv(output_path)

print("\nSaved summary:", output_path)
print("\nCalendar event analysis completed.")