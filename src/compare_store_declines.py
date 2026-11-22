from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_DIR / "reports"

INPUT_FILE = REPORTS_DIR / "store_decline_analysis.csv"

print("=" * 70)
print("SIGNALSENTINEL AI - CROSS-STORE DECLINE COMPARISON")
print("=" * 70)

# Load the daily decline results.
print("\n1. Loading store decline data...")

df = pd.read_csv(INPUT_FILE, parse_dates=["date"])

df["potential_decline_alert"] = (
    df["potential_decline_alert"].astype(bool)
)

# Create a matrix: one row per date, one column per store.
print("2. Creating the cross-store alert matrix...")

alert_matrix = df.pivot(
    index="date",
    columns="store_id",
    values="potential_decline_alert",
).fillna(False).astype(bool)

# Count alerts across stores on each date.
alert_matrix["stores_flagged"] = alert_matrix.sum(axis=1)

print("\n3. OVERALL ALERT OVERLAP")

print("Dates analyzed:", len(alert_matrix))
print(
    "Dates with no store alerts:",
    (alert_matrix["stores_flagged"] == 0).sum(),
)
print(
    "Dates with at least one store alert:",
    (alert_matrix["stores_flagged"] >= 1).sum(),
)
print(
    "Dates with at least three stores flagged:",
    (alert_matrix["stores_flagged"] >= 3).sum(),
)
print(
    "Dates with at least five stores flagged:",
    (alert_matrix["stores_flagged"] >= 5).sum(),
)

print("\n4. MOST WIDESPREAD ALERT DATES")

most_flagged = alert_matrix.sort_values(
    "stores_flagged",
    ascending=False,
).head(15)

print(most_flagged.to_string())

# Calculate the fraction of days where each pair of stores
# was simultaneously flagged.
print("\n5. PAIRWISE ALERT OVERLAP")

store_columns = [
    column for column in alert_matrix.columns
    if column != "stores_flagged"
]

alert_only = alert_matrix[store_columns]

overlap_rows = []

for i, store_a in enumerate(store_columns):
    for store_b in store_columns[i + 1:]:
        both_alert = (
            alert_only[store_a] & alert_only[store_b]
        ).sum()

        either_alert = (
            alert_only[store_a] | alert_only[store_b]
        ).sum()

        overlap_rows.append({
            "store_a": store_a,
            "store_b": store_b,
            "days_both_alert": int(both_alert),
            "days_either_alert": int(either_alert),
            "overlap_percent_of_either_alert_days": (
                round(both_alert / either_alert * 100, 2)
                if either_alert
                else 0
            ),
        })

overlap_df = pd.DataFrame(overlap_rows)

overlap_df = overlap_df.sort_values(
    "overlap_percent_of_either_alert_days",
    ascending=False,
)

print(overlap_df.head(20).to_string(index=False))

# Save the outputs.
matrix_output = REPORTS_DIR / "cross_store_alert_matrix.csv"
overlap_output = REPORTS_DIR / "cross_store_alert_overlap.csv"

alert_matrix.to_csv(matrix_output)
overlap_df.to_csv(overlap_output, index=False)

print("\n6. OUTPUT FILES")
print("Daily alert matrix:", matrix_output)
print("Pairwise overlap:", overlap_output)

print("\nCross-store comparison completed.")
print(
    "Overlapping alerts suggest shared timing, "
    "not a proven shared cause."
)