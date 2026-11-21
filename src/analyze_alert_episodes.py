import pandas as pd

# Load the existing anomaly report
file_path = "reports/weekday_adjusted_anomalies.csv"
data = pd.read_csv(file_path)

# Keep only dates flagged as anomalous
data["weekday_anomaly"] = (
    data["weekday_anomaly"]
    .fillna(False)
    .astype(str)
    .str.lower()
    .eq("true")
)

data["date"] = pd.to_datetime(data["date"])

alerts = data[data["weekday_anomaly"]].copy()
alerts = alerts.sort_values("date")

all_episodes = []

# Analyze unusually low and unusually high sales separately
for direction in ["Unusually Low", "Unusually High"]:
    subset = alerts[alerts["anomaly_type"] == direction].copy()

    # Start a new episode when alert dates are not consecutive
    subset["episode_id"] = (
        subset["date"].diff().dt.days.ne(1).cumsum()
    )

    episodes = (
        subset.groupby("episode_id")
        .agg(
            start_date=("date", "min"),
            end_date=("date", "max"),
            alert_days=("date", "size"),
            strongest_z=("weekday_z_score", "min")
        )
        .reset_index(drop=True)
    )

    episodes["direction"] = direction

    all_episodes.append(episodes)

# Combine both directions
result = pd.concat(all_episodes, ignore_index=True)

# Summary
print("\nEPISODES BY DIRECTION")
print(
    result.groupby("direction")["alert_days"]
    .agg(["count", "sum", "max"])
    .to_string()
)

# Multi-day episodes
print("\nEPISODES LASTING TWO OR MORE DAYS")
multi_day = result[result["alert_days"] >= 2]

print(
    multi_day.sort_values(
        ["alert_days", "start_date"],
        ascending=[False, True]
    ).to_string(index=False)
)

# Save results for future analysis
output_path = "reports/separate_direction_episodes.csv"
result.to_csv(output_path, index=False)

print(f"\nReport saved to: {output_path}")