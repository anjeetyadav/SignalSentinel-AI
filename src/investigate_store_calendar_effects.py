from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"
REPORTS_DIR = PROJECT_DIR / "reports"

INPUT_FILE = REPORTS_DIR / "store_decline_analysis.csv"

print("=" * 70)
print("SIGNALSENTINEL AI - STORE CALENDAR INVESTIGATION")
print("=" * 70)

# Load the historical decline analysis.
print("\n1. Loading data...")

df = pd.read_csv(INPUT_FILE, parse_dates=["date"])

calendar = pd.read_csv(
    RAW_DATA_DIR / "calendar.csv",
    usecols=[
        "date",
        "weekday",
        "event_name_1",
        "event_type_1",
        "event_name_2",
        "event_type_2",
    ],
)

calendar["date"] = pd.to_datetime(calendar["date"])

# Combine any event names recorded for each date.
calendar["event_names"] = (
    calendar[["event_name_1", "event_name_2"]]
    .fillna("")
    .agg(
        lambda row: ", ".join(value for value in row if value),
        axis=1,
    )
)

calendar["has_event"] = calendar["event_names"].ne("")

# Attach calendar information to the store-level analysis.
df = df.merge(
    calendar[
        [
            "date",
            "weekday",
            "event_names",
            "event_type_1",
            "event_type_2",
            "has_event",
        ]
    ],
    on="date",
    how="left",
    validate="many_to_one",
)

# Focus on the two stores with the most alerts.
target_stores = ["WI_2", "WI_3"]
focus = df[df["store_id"].isin(target_stores)].copy()

print("\n2. ALERT RATES BY STORE")

alert_rates = (
    focus.groupby("store_id")
    .agg(
        days=("potential_decline_alert", "size"),
        alert_days=("potential_decline_alert", "sum"),
    )
)

alert_rates["alert_rate_percent"] = (
    alert_rates["alert_days"] / alert_rates["days"] * 100
)

print(alert_rates.round(2).to_string())

# Compare alert rates on dates with and without recorded events.
print("\n3. ALERT RATES: EVENT DAYS VS NON-EVENT DAYS")

event_summary = (
    focus.groupby(["store_id", "has_event"])
    .agg(
        days=("potential_decline_alert", "size"),
        alert_days=("potential_decline_alert", "sum"),
        average_change_percent=("change_percent", "mean"),
    )
)

event_summary["alert_rate_percent"] = (
    event_summary["alert_days"] / event_summary["days"] * 100
)

print(event_summary.round(2).to_string())

# Compare alert rates by weekday.
print("\n4. ALERT RATES BY WEEKDAY")

weekday_summary = (
    focus.groupby(["store_id", "weekday"])
    .agg(
        days=("potential_decline_alert", "size"),
        alert_days=("potential_decline_alert", "sum"),
        average_change_percent=("change_percent", "mean"),
    )
)

weekday_summary["alert_rate_percent"] = (
    weekday_summary["alert_days"] / weekday_summary["days"] * 100
)

print(weekday_summary.round(2).to_string())

# List the strongest alert days and their recorded calendar context.
print("\n5. MOST SEVERE ALERT DAYS WITH CALENDAR CONTEXT")

severe = focus[
    focus["potential_decline_alert"].astype(bool)
].nsmallest(20, "change_percent")

print(
    severe[
        [
            "store_id",
            "date",
            "weekday",
            "recent_7d_avg",
            "previous_28d_avg",
            "change_percent",
            "event_names",
        ]
    ].to_string(index=False)
)

# Save the enriched investigation data.
output_file = REPORTS_DIR / "store_calendar_investigation.csv"

focus.to_csv(output_file, index=False)

print("\n6. OUTPUT")
print("Calendar investigation saved to:", output_file)

print("\nInvestigation completed.")
print("Calendar associations are descriptive and do not prove causation.")