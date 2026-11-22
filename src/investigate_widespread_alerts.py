from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data" / "raw"
REPORTS_DIR = PROJECT_DIR / "reports"

ALERT_FILE = REPORTS_DIR / "store_decline_analysis.csv"
CALENDAR_FILE = DATA_DIR / "calendar.csv"

print("=" * 70)
print("SIGNALSENTINEL AI - WIDESPREAD ALERT INVESTIGATION")
print("=" * 70)

# --------------------------------------------------
# 1. Load the existing store-level alert results
# --------------------------------------------------

print("\n1. Loading store alert data...")

alerts = pd.read_csv(ALERT_FILE, parse_dates=["date"])

# Ensure the alert column contains actual Boolean values.
if alerts["potential_decline_alert"].dtype != bool:
    alerts["potential_decline_alert"] = (
        alerts["potential_decline_alert"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map({"true": True, "false": False})
    )

if alerts["potential_decline_alert"].isna().any():
    raise ValueError("Unexpected values found in the alert column.")

# Count the number of stores flagged on each date.
daily_alert_counts = (
    alerts.groupby("date")["potential_decline_alert"]
    .sum()
    .rename("stores_flagged")
    .reset_index()
)

# --------------------------------------------------
# 2. Load and prepare calendar information
# --------------------------------------------------

print("2. Loading calendar information...")

calendar = pd.read_csv(CALENDAR_FILE)

calendar["date"] = pd.to_datetime(calendar["date"])

event_columns = [
    column
    for column in ["event_name_1", "event_name_2"]
    if column in calendar.columns
]

def combine_events(row):
    events = []

    for column in event_columns:
        value = row[column]

        if pd.notna(value) and str(value).strip():
            events.append(str(value).strip())

    return ", ".join(events) if events else "No recorded event"


calendar["calendar_events"] = calendar.apply(
    combine_events,
    axis=1,
)

calendar["weekday"] = calendar["date"].dt.day_name()
calendar["month"] = calendar["date"].dt.month
calendar["year"] = calendar["date"].dt.year

calendar_info = calendar[
    ["date", "weekday", "month", "year", "calendar_events"]
].copy()

# --------------------------------------------------
# 3. Combine alerts and calendar information
# --------------------------------------------------

print("3. Combining alerts with calendar information...")

investigation = daily_alert_counts.merge(
    calendar_info,
    on="date",
    how="left",
)

investigation["calendar_events"] = (
    investigation["calendar_events"]
    .fillna("No calendar match")
)

investigation["widespread_alert"] = (
    investigation["stores_flagged"] >= 5
)

investigation["all_store_alert"] = (
    investigation["stores_flagged"] == 10
)

# --------------------------------------------------
# 4. Summarize widespread alerts
# --------------------------------------------------

print("\n4. WIDESPREAD ALERT SUMMARY")

print("Dates analyzed:", len(investigation))
print(
    "Dates with at least 5 stores flagged:",
    int(investigation["widespread_alert"].sum()),
)
print(
    "Dates with all 10 stores flagged:",
    int(investigation["all_store_alert"].sum()),
)

print("\n5. ALL DATES WITH AT LEAST 5 STORES FLAGGED")

widespread = investigation[
    investigation["widespread_alert"]
].sort_values(
    ["stores_flagged", "date"],
    ascending=[False, True],
)

columns_to_display = [
    "date",
    "stores_flagged",
    "weekday",
    "calendar_events",
]

print(
    widespread[columns_to_display]
    .to_string(index=False)
)

# --------------------------------------------------
# 5. Compare event and non-event dates
# --------------------------------------------------

print("\n6. ALERT RATES: EVENT VS NON-EVENT DATES")

investigation["has_recorded_event"] = (
    investigation["calendar_events"]
    .ne("No recorded event")
    & investigation["calendar_events"].ne("No calendar match")
)

event_summary = (
    investigation.groupby("has_recorded_event")
    .agg(
        days=("date", "count"),
        average_stores_flagged=("stores_flagged", "mean"),
        days_with_5plus_alerts=("widespread_alert", "sum"),
        days_with_all_10_alerts=("all_store_alert", "sum"),
    )
    .reset_index()
)

event_summary["days_with_5plus_alerts"] = (
    event_summary["days_with_5plus_alerts"].astype(int)
)

event_summary["days_with_all_10_alerts"] = (
    event_summary["days_with_all_10_alerts"].astype(int)
)

event_summary["widespread_alert_rate_percent"] = (
    event_summary["days_with_5plus_alerts"]
    / event_summary["days"]
    * 100
).round(2)

event_summary["average_stores_flagged"] = (
    event_summary["average_stores_flagged"].round(2)
)

print(event_summary.to_string(index=False))

# --------------------------------------------------
# 6. Identify months with the most widespread alerts
# --------------------------------------------------

print("\n7. WIDESPREAD ALERTS BY MONTH")

investigation["month_name"] = investigation["date"].dt.month_name()

monthly_summary = (
    investigation.groupby("month_name")
    .agg(
        days=("date", "count"),
        widespread_alert_days=("widespread_alert", "sum"),
        average_stores_flagged=("stores_flagged", "mean"),
    )
)

monthly_summary["widespread_alert_rate_percent"] = (
    monthly_summary["widespread_alert_days"]
    / monthly_summary["days"]
    * 100
).round(2)

monthly_summary["average_stores_flagged"] = (
    monthly_summary["average_stores_flagged"].round(2)
)

month_order = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December",
]

monthly_summary = monthly_summary.reindex(month_order)

print(monthly_summary.to_string())

# --------------------------------------------------
# 7. Save the investigation results
# --------------------------------------------------

output_file = REPORTS_DIR / "widespread_alert_investigation.csv"
event_output = REPORTS_DIR / "widespread_alert_event_summary.csv"
monthly_output = REPORTS_DIR / "widespread_alert_monthly_summary.csv"

investigation.to_csv(output_file, index=False)
event_summary.to_csv(event_output, index=False)
monthly_summary.to_csv(monthly_output)

print("\n8. REPORTS SAVED")
print("Detailed investigation:", output_file)
print("Event comparison:", event_output)
print("Monthly summary:", monthly_output)

print("\nInvestigation completed.")
print(
    "Reminder: calendar associations are descriptive, "
    "not proof that events caused the alerts."
)