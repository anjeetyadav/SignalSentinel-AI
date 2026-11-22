from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_DIR / "reports"

INPUT_FILE = REPORTS_DIR / "store_decline_analysis.csv"

print("=" * 70)
print("SIGNALSENTINEL AI - STORE ALERT INVESTIGATION")
print("=" * 70)

# Load the decline analysis produced by our previous script.
print("\n1. Loading previous analysis...")

df = pd.read_csv(INPUT_FILE, parse_dates=["date"])

# Investigate the two stores with the highest alert counts.
target_stores = ["WI_2", "WI_3"]

focus = df[df["store_id"].isin(target_stores)].copy()

print("\n2. ALERT SUMMARY")

summary = (
    focus.groupby("store_id")
    .agg(
        days_analyzed=("potential_decline_alert", "count"),
        alert_days=("potential_decline_alert", "sum"),
        average_change_percent=("change_percent", "mean"),
        worst_change_percent=("change_percent", "min"),
    )
)

summary["alert_rate_percent"] = (
    summary["alert_days"] / summary["days_analyzed"] * 100
)

print(summary.round(2).to_string())

# List the most severe declines for each store.
print("\n3. TEN MOST SEVERE DECLINE DAYS PER STORE")

for store_id in target_stores:
    store_data = focus[
        (focus["store_id"] == store_id)
        & (focus["potential_decline_alert"] == True)
    ].copy()

    store_data = store_data.sort_values("change_percent").head(10)

    print(f"\n{store_id}")
    print(
        store_data[
            [
                "date",
                "recent_7d_avg",
                "previous_28d_avg",
                "change_percent",
            ]
        ].to_string(index=False)
    )

# Count separate alert episodes.
# A new episode starts when an alert follows a non-alert day,
# or when there is a gap of more than one calendar day.
print("\n4. ALERT EPISODES")

episode_rows = []

for store_id in target_stores:
    store_data = focus[focus["store_id"] == store_id].copy()
    store_data = store_data.sort_values("date").reset_index(drop=True)

    store_data["alert"] = (
        store_data["potential_decline_alert"].astype(bool)
    )

    store_data["previous_alert"] = (
        store_data["alert"].shift(1, fill_value=False)
    )

    store_data["date_gap"] = store_data["date"].diff().dt.days

    store_data["new_episode"] = (
        store_data["alert"]
        & (
            (~store_data["previous_alert"])
            | (store_data["date_gap"] > 1)
        )
    )

    store_data["episode_id"] = (
        store_data["new_episode"].cumsum()
    )

    alert_data = store_data[store_data["alert"]].copy()

    for episode_id, episode in alert_data.groupby("episode_id"):
        episode_rows.append({
            "store_id": store_id,
            "start_date": episode["date"].min(),
            "end_date": episode["date"].max(),
            "alert_days": len(episode),
            "worst_change_percent": episode["change_percent"].min(),
        })

episodes = pd.DataFrame(episode_rows)

if not episodes.empty:
    episodes = episodes.sort_values(
        ["store_id", "start_date"]
    )

    print(episodes.round(2).to_string(index=False))

    episode_output = REPORTS_DIR / "store_alert_episodes.csv"
    episodes.to_csv(episode_output, index=False)

    print("\nEpisode details saved to:", episode_output)
else:
    print("No alert episodes found.")

print("\n5. INVESTIGATION COMPLETED")
print("This analysis identifies patterns, not confirmed business causes.")