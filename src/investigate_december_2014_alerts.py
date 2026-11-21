from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data" / "raw"
REPORTS_DIR = PROJECT_DIR / "reports"

SALES_FILE = DATA_DIR / "sales_train_validation.csv"
CALENDAR_FILE = DATA_DIR / "calendar.csv"
ALERT_FILE = REPORTS_DIR / "store_decline_analysis.csv"

print("=" * 75)
print("SIGNALSENTINEL AI - DECEMBER 2014 STORE ALERT INVESTIGATION")
print("=" * 75)

# --------------------------------------------------
# 1. Load the existing alert analysis
# --------------------------------------------------

print("\n1. Loading existing store alerts...")

alerts = pd.read_csv(ALERT_FILE, parse_dates=["date"])

alerts["potential_decline_alert"] = (
    alerts["potential_decline_alert"]
    .astype(str)
    .str.strip()
    .str.lower()
    .map({"true": True, "false": False})
)

if alerts["potential_decline_alert"].isna().any():
    raise ValueError("Unexpected values in the alert column.")

target_dates = pd.to_datetime([
    "2014-12-28",
    "2014-12-29",
    "2014-12-30",
    "2014-12-31",
])

target_alerts = alerts[
    alerts["date"].isin(target_dates)
].copy()

print("\n2. EXISTING ALERTS ON THE FOUR TARGET DATES")

print(
    target_alerts[
        [
            "date",
            "store_id",
            "recent_7d_avg",
            "previous_28d_avg",
            "change_percent",
            "potential_decline_alert",
        ]
    ].sort_values(["date", "store_id"]).to_string(index=False)
)

# --------------------------------------------------
# 2. Load daily sales and aggregate by store
# --------------------------------------------------

print("\n3. Loading store-level sales history...")

sales = pd.read_csv(SALES_FILE)

daily_columns = [
    column for column in sales.columns
    if column.startswith("d_")
]

# Sum product sales within each store.
store_daily = sales.groupby("store_id")[daily_columns].sum()

store_daily = store_daily.reset_index()

store_daily = store_daily.melt(
    id_vars="store_id",
    var_name="d",
    value_name="units_sold",
)

calendar = pd.read_csv(CALENDAR_FILE)

calendar["date"] = pd.to_datetime(calendar["date"])

store_daily = store_daily.merge(
    calendar[["d", "date"]],
    on="d",
    how="left",
    validate="many_to_one",
)

store_daily = store_daily.sort_values(
    ["store_id", "date"]
).reset_index(drop=True)

# --------------------------------------------------
# 3. Calculate comparable sales averages
# --------------------------------------------------

print("\n4. Calculating sales averages for each store...")

grouped = store_daily.groupby("store_id")["units_sold"]

# Most recent 7 days, including the date being investigated.
store_daily["recent_7d_avg"] = grouped.transform(
    lambda series: series.rolling(7, min_periods=7).mean()
)

# The 28 days before that recent 7-day period.
store_daily["previous_28d_avg"] = grouped.transform(
    lambda series: series.shift(7).rolling(
        28,
        min_periods=28,
    ).mean()
)

store_daily["change_percent"] = (
    (
        store_daily["recent_7d_avg"]
        - store_daily["previous_28d_avg"]
    )
    / store_daily["previous_28d_avg"].replace(0, float("nan"))
    * 100
)

# --------------------------------------------------
# 4. Inspect the daily sales around the alerts
# --------------------------------------------------

print("\n5. DAILY STORE SALES: DECEMBER 20-31, 2014")

start_date = pd.Timestamp("2014-12-20")
end_date = pd.Timestamp("2014-12-31")

daily_window = store_daily[
    store_daily["date"].between(start_date, end_date)
].copy()

daily_output = REPORTS_DIR / "december_2014_store_daily_sales.csv"

daily_window.to_csv(daily_output, index=False)

print(
    daily_window[
        ["date", "store_id", "units_sold"]
    ].to_string(index=False)
)

# --------------------------------------------------
# 5. Compare the detector's calculations
# --------------------------------------------------

print("\n6. STORE-LEVEL ALERT CALCULATIONS")

calculated = store_daily[
    store_daily["date"].isin(target_dates)
].copy()

calculated["calculated_alert"] = (
    calculated["change_percent"] <= -15
)

comparison = calculated.merge(
    target_alerts[
        [
            "date",
            "store_id",
            "recent_7d_avg",
            "previous_28d_avg",
            "change_percent",
            "potential_decline_alert",
        ]
    ],
    on=["date", "store_id"],
    how="left",
    suffixes=("_recalculated", "_original"),
    validate="one_to_one",
)

comparison_output = REPORTS_DIR / "december_2014_alert_comparison.csv"

comparison.to_csv(comparison_output, index=False)

print(
    comparison[
        [
            "date",
            "store_id",
            "recent_7d_avg_recalculated",
            "previous_28d_avg_recalculated",
            "change_percent_recalculated",
            "calculated_alert",
            "potential_decline_alert",
        ]
    ].sort_values(["date", "store_id"]).to_string(index=False)
)

print("\n7. SUMMARY BY DATE")

summary = (
    comparison.groupby("date")
    .agg(
        stores_checked=("store_id", "nunique"),
        stores_flagged=("calculated_alert", "sum"),
        average_change_percent=("change_percent_recalculated", "mean"),
        worst_change_percent=("change_percent_recalculated", "min"),
    )
    .reset_index()
)

for column in ["average_change_percent", "worst_change_percent"]:
    summary[column] = summary[column].round(2)

print(summary.to_string(index=False))

print("\n8. OUTPUT FILES")
print("Daily sales:", daily_output)
print("Alert comparison:", comparison_output)

print("\nInvestigation completed.")
print(
    "The comparison helps explain the rule-based alerts; "
    "it does not establish their business causes."
)