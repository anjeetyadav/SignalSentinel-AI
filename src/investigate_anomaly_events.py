from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"
REPORTS_DIR = PROJECT_DIR / "reports"

anomalies_path = REPORTS_DIR / "weekday_adjusted_anomalies.csv"
calendar_path = RAW_DATA_DIR / "calendar.csv"

anomalies = pd.read_csv(
    anomalies_path,
    parse_dates=["date"],
)

calendar = pd.read_csv(calendar_path)

event_columns = [
    "d",
    "date",
    "weekday",
    "event_name_1",
    "event_type_1",
    "event_name_2",
    "event_type_2",
]

calendar["date"] = pd.to_datetime(calendar["date"])

# Keep only days that crossed our statistical threshold.
flagged = anomalies.loc[
    anomalies["weekday_anomaly"] == True
].copy()

# Match the flagged days with available calendar information.
investigation = flagged.merge(
    calendar[event_columns],
    on=["d", "date"],
    how="left",
    validate="one_to_one",
    suffixes=("_sales", "_calendar"),
)

investigation["has_calendar_event"] = (
    investigation["event_name_1"].notna()
    | investigation["event_name_2"].notna()
)

print("=" * 70)
print("SIGNALSENTINEL AI - ANOMALY EVENT INVESTIGATION")
print("=" * 70)

print("\n1. TOTAL FLAGGED DAYS:", len(investigation))

print(
    "Flagged days with a recorded calendar event:",
    int(investigation["has_calendar_event"].sum()),
)

print(
    "Flagged days without a recorded calendar event:",
    int((~investigation["has_calendar_event"]).sum()),
)

print("\n2. FLAGGED DAYS WITH CALENDAR EVENTS")

with_events = investigation.loc[
    investigation["has_calendar_event"]
]

if with_events.empty:
    print("No flagged days matched recorded calendar events.")
else:
    print(
        with_events[
            [
                "date",
                "weekday_sales",
                "total_units_sold",
                "weekday_z_score",
                "anomaly_type",
                "event_name_1",
                "event_type_1",
                "event_name_2",
                "event_type_2",
            ]
        ].to_string(index=False)
    )

print("\n3. ALL FLAGGED DATES")

print(
    investigation[
        [
            "date",
            "weekday_sales",
            "total_units_sold",
            "weekday_z_score",
            "anomaly_type",
            "event_name_1",
            "event_type_1",
            "event_name_2",
            "event_type_2",
        ]
    ].sort_values("date").to_string(index=False)
)

output_path = REPORTS_DIR / "anomaly_event_investigation.csv"
investigation.to_csv(output_path, index=False)

print("\nSaved investigation:", output_path)
print("\nCalendar event investigation completed.")