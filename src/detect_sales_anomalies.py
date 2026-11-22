from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

PROJECT_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_DIR / "reports"

daily_sales = pd.read_csv(
    REPORTS_DIR / "daily_sales_totals.csv",
    parse_dates=["date"],
)

daily_sales = daily_sales.sort_values("date").reset_index(drop=True)

# Use only previous observations when building the baseline.
# shift(1) prevents the current day's sales from entering its own baseline.
WINDOW = 28

daily_sales["baseline_mean"] = (
    daily_sales["total_units_sold"]
    .shift(1)
    .rolling(window=WINDOW, min_periods=WINDOW)
    .mean()
)

daily_sales["baseline_std"] = (
    daily_sales["total_units_sold"]
    .shift(1)
    .rolling(window=WINDOW, min_periods=WINDOW)
    .std()
)

# Measure how far the current value lies from the historical mean.
daily_sales["z_score"] = (
    daily_sales["total_units_sold"] - daily_sales["baseline_mean"]
) / daily_sales["baseline_std"].replace(0, np.nan)

# Initial statistical screening threshold.
THRESHOLD = 3.0

daily_sales["is_anomaly"] = (
    daily_sales["z_score"].abs() > THRESHOLD
)

daily_sales["anomaly_type"] = np.select(
    [
        daily_sales["z_score"] < -THRESHOLD,
        daily_sales["z_score"] > THRESHOLD,
    ],
    [
        "Unusually Low",
        "Unusually High",
    ],
    default="Normal",
)

# Early observations without 28 prior days cannot be evaluated.
daily_sales.loc[
    daily_sales["baseline_mean"].isna(),
    "anomaly_type",
] = "Insufficient History"

print("=" * 65)
print("SIGNALSENTINEL AI - INITIAL ANOMALY DETECTION")
print("=" * 65)

eligible_days = daily_sales["baseline_mean"].notna()
anomalies = daily_sales.loc[
    eligible_days & daily_sales["is_anomaly"]
].copy()

print("\n1. DETECTION SETTINGS")
print("Historical baseline window:", WINDOW, "days")
print("Absolute z-score threshold:", THRESHOLD)
print("Days with sufficient history:", int(eligible_days.sum()))

print("\n2. ANOMALY COUNTS")
print("Total flagged days:", len(anomalies))
print(
    "Unusually low days:",
    int((anomalies["anomaly_type"] == "Unusually Low").sum()),
)
print(
    "Unusually high days:",
    int((anomalies["anomaly_type"] == "Unusually High").sum()),
)

print("\n3. TEN MOST EXTREME FLAGGED DAYS")

if anomalies.empty:
    print("No days crossed the selected threshold.")
else:
    anomalies["absolute_z_score"] = anomalies["z_score"].abs()

    print(
        anomalies.nlargest(10, "absolute_z_score")[
            [
                "date",
                "total_units_sold",
                "baseline_mean",
                "z_score",
                "anomaly_type",
            ]
        ].round(2).to_string(index=False)
    )

output_csv = REPORTS_DIR / "daily_sales_anomalies.csv"
daily_sales.to_csv(output_csv, index=False)

# Plot actual sales and the rolling baseline.
plt.figure(figsize=(14, 6))

plt.plot(
    daily_sales["date"],
    daily_sales["total_units_sold"],
    label="Actual Daily Sales",
    linewidth=1,
)

plt.plot(
    daily_sales["date"],
    daily_sales["baseline_mean"],
    label="Previous 28-Day Mean",
    linewidth=1.5,
)

plt.scatter(
    anomalies["date"],
    anomalies["total_units_sold"],
    label="Flagged Anomalies",
    s=25,
)

plt.title("SignalSentinel AI - Initial Daily Sales Anomaly Detection")
plt.xlabel("Date")
plt.ylabel("Total Units Sold")
plt.legend()
plt.tight_layout()

output_plot = REPORTS_DIR / "daily_sales_anomalies.png"
plt.savefig(output_plot, dpi=150)
plt.close()

print("\nSaved results:", output_csv)
print("Saved chart:", output_plot)
print("\nInitial anomaly detection completed.")