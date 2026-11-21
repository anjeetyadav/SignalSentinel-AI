from pathlib import Path
import pandas as pd
import numpy as np
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

daily_sales = daily_sales.sort_values("date").reset_index(drop=True)

# Compare each day with the previous 8 observations
# for the same weekday. shift(1) excludes the current day.
WINDOW = 8

daily_sales["weekday_baseline_mean"] = (
    daily_sales.groupby("wday")["total_units_sold"]
    .transform(
        lambda series: series.shift(1).rolling(
            window=WINDOW,
            min_periods=WINDOW,
        ).mean()
    )
)

daily_sales["weekday_baseline_std"] = (
    daily_sales.groupby("wday")["total_units_sold"]
    .transform(
        lambda series: series.shift(1).rolling(
            window=WINDOW,
            min_periods=WINDOW,
        ).std()
    )
)

daily_sales["weekday_z_score"] = (
    daily_sales["total_units_sold"]
    - daily_sales["weekday_baseline_mean"]
) / daily_sales["weekday_baseline_std"].replace(0, np.nan)

THRESHOLD = 3.0

daily_sales["weekday_anomaly"] = (
    daily_sales["weekday_z_score"].abs() > THRESHOLD
)

daily_sales["anomaly_type"] = np.select(
    [
        daily_sales["weekday_z_score"] < -THRESHOLD,
        daily_sales["weekday_z_score"] > THRESHOLD,
    ],
    [
        "Unusually Low",
        "Unusually High",
    ],
    default="Normal",
)

daily_sales.loc[
    daily_sales["weekday_baseline_mean"].isna(),
    "anomaly_type",
] = "Insufficient History"

eligible = daily_sales["weekday_baseline_mean"].notna()

anomalies = daily_sales.loc[
    eligible & daily_sales["weekday_anomaly"]
].copy()

print("=" * 65)
print("SIGNALSENTINEL AI - WEEKDAY-ADJUSTED ANOMALY DETECTION")
print("=" * 65)

print("\nBaseline: Previous", WINDOW, "observations for the same weekday")
print("Threshold: Absolute z-score >", THRESHOLD)
print("Days with sufficient history:", int(eligible.sum()))
print("Total flagged days:", len(anomalies))

print(
    "Unusually low days:",
    int((anomalies["anomaly_type"] == "Unusually Low").sum()),
)

print(
    "Unusually high days:",
    int((anomalies["anomaly_type"] == "Unusually High").sum()),
)

print("\nTEN MOST EXTREME FLAGGED DAYS")

if anomalies.empty:
    print("No days crossed the selected threshold.")
else:
    anomalies["absolute_z_score"] = anomalies["weekday_z_score"].abs()

    print(
        anomalies.nlargest(10, "absolute_z_score")[
            [
                "date",
                "weekday",
                "total_units_sold",
                "weekday_baseline_mean",
                "weekday_z_score",
                "anomaly_type",
            ]
        ].round(2).to_string(index=False)
    )

output_csv = REPORTS_DIR / "weekday_adjusted_anomalies.csv"
daily_sales.to_csv(output_csv, index=False)

plt.figure(figsize=(14, 6))

plt.plot(
    daily_sales["date"],
    daily_sales["total_units_sold"],
    label="Actual Daily Sales",
    linewidth=1,
)

plt.plot(
    daily_sales["date"],
    daily_sales["weekday_baseline_mean"],
    label="Same-Weekday Baseline",
    linewidth=1.5,
)

plt.scatter(
    anomalies["date"],
    anomalies["total_units_sold"],
    label="Flagged Anomalies",
    s=25,
)

plt.title("SignalSentinel AI - Weekday-Adjusted Anomaly Detection")
plt.xlabel("Date")
plt.ylabel("Total Units Sold")
plt.legend()
plt.tight_layout()

output_plot = REPORTS_DIR / "weekday_adjusted_anomalies.png"
plt.savefig(output_plot, dpi=150)
plt.close()

print("\nSaved results:", output_csv)
print("Saved chart:", output_plot)
print("\nWeekday-adjusted anomaly detection completed.")